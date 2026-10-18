"""NVIDIA hosted chat completions with explicit remote provenance and no key persistence."""
from __future__ import annotations

import hashlib
import http.client
import json
import math
import os
import re
import time
from typing import Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .backends import DEFAULT_MAX_TOKENS, REPLY_SCHEMA

DEFAULT_NIM_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
DEFAULT_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
_MAX_RESPONSE_BYTES = 1024 * 1024


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Returning None leaves the response to urllib's HTTP error handler. Never
        # forward an Authorization header, even to another NVIDIA URL.
        return None


def _base_url(value: str) -> str:
    error = "NIM base_url must be https://integrate.api.nvidia.com/v1 without credentials, query, or fragment"
    if not isinstance(value, str) or any(char.isspace() or ord(char) < 32 for char in value):
        raise ValueError(error)
    try:
        parts = urlsplit(value)
        valid = (parts.scheme == "https" and parts.hostname == "integrate.api.nvidia.com"
                 and parts.port in {None, 443} and parts.username is None and parts.password is None
                 and parts.netloc.lower() in {"integrate.api.nvidia.com", "integrate.api.nvidia.com:443"}
                 and parts.path in {"/v1", "/v1/"} and "?" not in value and "#" not in value)
    except ValueError:
        raise ValueError(error) from None
    if not valid:
        raise ValueError(error)
    return DEFAULT_NIM_BASE_URL


def _strict_json(value: str):
    def pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = item
        return result

    def constant(value):
        raise ValueError("nonfinite JSON value")

    return json.loads(value, object_pairs_hook=pairs, parse_constant=constant)


def _http_failure(status: int) -> RuntimeError:
    # Do not inspect or include provider response bodies, headers, or exception
    # text: all can contain request data or a reflected credential.
    if status in {401, 403}:
        detail = "check NVIDIA_API_KEY and access to the selected model"
    elif status in {400, 422}:
        detail = "check the model and generation settings; if JSON schema is unsupported, explicitly select json_mode=json_object or none"
    elif status == 404:
        detail = "check that the selected model is available on NVIDIA's hosted API"
    elif status == 429:
        detail = "rate limit reached; retry later or check your NVIDIA API quota"
    elif 300 <= status < 400:
        detail = "redirect refused to protect the API credential; use the approved NVIDIA endpoint"
    elif 500 <= status < 600:
        detail = "the NVIDIA service is unavailable; retry later"
    else:
        detail = "check the selected model and NVIDIA API settings"
    return RuntimeError(f"NIM request failed (HTTP {status}); {detail}")


class NIMBackend:
    """One nonstreaming NVIDIA request per focused report-part conversation.

    The key is read from NVIDIA_API_KEY only when generating and is never stored
    on this adapter. JSON mode changes are explicit; a server rejection never
    silently changes the requested decoding settings. Retries cover only HTTP
    429, HTTP 5xx, and timeouts, up to max_retries additional attempts.
    """

    def __init__(self, model_id: str = DEFAULT_NIM_MODEL, *, base_url: str = DEFAULT_NIM_BASE_URL,
                 max_tokens: int = DEFAULT_MAX_TOKENS, seed: int = 42, temperature: float = 0.0,
                 timeout: float = 120.0, max_retries: int = 2, json_mode: str = "json_schema"):
        if not isinstance(model_id, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", model_id):
            raise ValueError("NIM model_id must have the form namespace/model")
        if type(max_tokens) is not int or not 32 <= max_tokens <= 1024:
            raise ValueError("NIM max_tokens must be an integer between 32 and 1024")
        if type(seed) is not int or not 0 <= seed <= 2 ** 32 - 1:
            raise ValueError("NIM seed must be an integer between 0 and 4294967295")
        if type(temperature) not in {int, float} or not 0 <= temperature <= 1:
            raise ValueError("NIM temperature must be between 0 and 1")
        if type(timeout) not in {int, float} or not math.isfinite(timeout) or not 0 < timeout <= 600:
            raise ValueError("NIM timeout must be finite and between 0 and 600 seconds")
        if type(max_retries) is not int or not 0 <= max_retries <= 5:
            raise ValueError("NIM max_retries must be an integer between 0 and 5")
        if json_mode not in {"json_schema", "json_object", "none"}:
            raise ValueError("NIM json_mode must be json_schema, json_object, or none")
        self.model_id = model_id
        self.settings = {"base_url": _base_url(base_url), "max_tokens": max_tokens, "seed": seed,
                         "temperature": temperature, "timeout": timeout, "max_retries": max_retries,
                         "json_mode": json_mode, "enable_thinking": False}
        self._opener = build_opener(_NoRedirects())
        self._remote_requests = 0
        self._remote_successes = 0
        self._generation_calls = 0
        self._generated_records = 0
        self._token_usage: dict[str, int] = {}
        self._message_sha256: list[str] = []

    @property
    def metadata(self) -> dict:
        execution = {"remote_requests": self._remote_requests, "remote_successes": self._remote_successes,
                     "generation_calls": self._generation_calls, "generated_records": self._generated_records,
                     "message_sha256": list(self._message_sha256)}
        if self._token_usage:
            execution["token_usage"] = dict(self._token_usage)
        return {"backend": "nim", "model": {"model_id": self.model_id, "revision": "provider-managed"},
                "settings": dict(self.settings), "execution": execution}

    def _payload(self, conversation: list[dict]) -> bytes:
        if not isinstance(conversation, list) or not conversation or any(
            not isinstance(message, dict) or set(message) != {"role", "content"}
            or not isinstance(message["role"], str)
            or message["role"] not in {"system", "user", "assistant"}
            or not isinstance(message["content"], str) or not message["content"].strip()
            for message in conversation
        ):
            raise ValueError("NIM conversations require nonempty role/content chat messages")
        payload = {"model": self.model_id, "messages": conversation, "max_tokens": self.settings["max_tokens"],
                   "temperature": self.settings["temperature"], "seed": self.settings["seed"], "stream": False,
                   "n": 1, "chat_template_kwargs": {"enable_thinking": False}}
        if self.settings["json_mode"] == "json_schema":
            payload["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "icb_reply", "strict": True, "schema": REPLY_SCHEMA}}
        elif self.settings["json_mode"] == "json_object":
            payload["response_format"] = {"type": "json_object"}
        try:
            return json.dumps(payload, ensure_ascii=True, allow_nan=False).encode("utf-8")
        except (ValueError, TypeError):
            raise ValueError("NIM input could not be serialized as a chat request") from None

    def _request(self, payload: bytes, key: str) -> bytes:
        for attempt in range(self.settings["max_retries"] + 1):
            request = Request(self.settings["base_url"] + "/chat/completions", data=payload, method="POST",
                              headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                       "Accept": "application/json"})
            self._remote_requests += 1
            retry = False
            try:
                with self._opener.open(request, timeout=self.settings["timeout"]) as response:
                    status = response.status
                    if type(status) is not int or not 100 <= status <= 599:
                        raise RuntimeError("NIM returned an invalid HTTP status")
                    if status != 200:
                        failure = _http_failure(status)
                        retry = status == 429 or 500 <= status < 600
                    else:
                        data = response.read(_MAX_RESPONSE_BYTES + 1)
                        if len(data) > _MAX_RESPONSE_BYTES:
                            raise RuntimeError("NIM response exceeded the permitted size")
                        return data
            except HTTPError as error:
                status = error.code
                # Release the connection without ever reading the error body.
                error.close()
                failure = _http_failure(status)
                retry = status == 429 or 500 <= status < 600
            except TimeoutError:
                failure = RuntimeError("NIM request timed out; retry later or increase the finite timeout setting")
                retry = True
            except URLError as error:
                retry = isinstance(error.reason, TimeoutError)
                failure = (RuntimeError("NIM request timed out; retry later or increase the finite timeout setting")
                           if retry else RuntimeError("NIM connection failed; check network access to the NVIDIA API"))
            except (OSError, http.client.HTTPException, ValueError):
                failure = RuntimeError("NIM connection failed; check network access to the NVIDIA API")
            if not retry or attempt == self.settings["max_retries"]:
                raise failure from None
            time.sleep(min(2 ** attempt, 16))
        raise RuntimeError("NIM retry limit exceeded")  # Defensive: the bounded loop always returns or raises.

    def _reply(self, data: bytes) -> str:
        try:
            response = _strict_json(data.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError):
            raise RuntimeError("NIM returned invalid JSON") from None
        choices = response.get("choices") if isinstance(response, dict) else None
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise RuntimeError("NIM output count does not match the requested single reply")
        choice = choices[0]
        if choice.get("finish_reason") == "length":
            raise RuntimeError("NIM reply was truncated; increase max_tokens within the supported limit")
        if choice.get("finish_reason") != "stop":
            raise RuntimeError("NIM did not finish with a complete text reply; check the model and request settings")
        message = choice.get("message")
        if not isinstance(message, dict) or message.get("refusal") or message.get("tool_calls"):
            raise RuntimeError("NIM did not return an assistant text reply")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip() or len(content) > 3000:
            raise RuntimeError("NIM returned missing, invalid, or oversized text content")
        try:
            reply = _strict_json(content)
        except (ValueError, RecursionError):
            raise RuntimeError("NIM reply must be valid JSON containing only the text field; check json_mode") from None
        if not isinstance(reply, dict) or set(reply) != {"text"} or not isinstance(reply["text"], str):
            raise RuntimeError("NIM reply must contain only one string field named text")
        usage = response.get("usage")
        if isinstance(usage, dict):
            for name in ("prompt_tokens", "completion_tokens", "total_tokens"):
                value = usage.get(name)
                if type(value) is int and value >= 0:
                    self._token_usage[name] = self._token_usage.get(name, 0) + value
        self._remote_successes += 1
        return content.strip()

    def generate(self, conversations: Sequence[list[dict]]) -> list[str]:
        # Validate every conversation before sending any of a batch's evidence.
        payloads = [self._payload(conversation) for conversation in conversations]
        if not payloads:
            return []
        key = os.environ.get("NVIDIA_API_KEY", "")
        if not key:
            raise ValueError("NVIDIA_API_KEY is required for the NIM backend; set it in the process environment")
        if not key.isascii() or any(char.isspace() or ord(char) < 33 or ord(char) == 127 for char in key):
            raise ValueError("NVIDIA_API_KEY has an invalid format; check the process environment")
        texts = []
        for payload in payloads:
            text = self._reply(self._request(payload, key))
            # Hash only the chat messages, so audits can compare evidence and
            # skill prompts across providers without saving a request body.
            messages = json.loads(payload)["messages"]
            canonical = json.dumps(messages, ensure_ascii=True, allow_nan=False, sort_keys=True,
                                   separators=(",", ":")).encode("utf-8")
            self._message_sha256.append(hashlib.sha256(canonical).hexdigest())
            texts.append(text)
        self._generation_calls += 1
        self._generated_records += len(texts)
        return texts
