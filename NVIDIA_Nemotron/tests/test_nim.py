"""Exercise the hosted adapter with synthetic replies and no network or credentials."""

import hashlib
import io
import json
import os
import traceback
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request

from icb_copilot.backends import REPLY_SCHEMA
from icb_copilot.nim import DEFAULT_NIM_BASE_URL, DEFAULT_NIM_MODEL, NIMBackend


KEY = "synthetic-test-credential"
MESSAGES = [{"role": "system", "content": "Return JSON containing only the text field."},
            {"role": "user", "content": "Synthetic evidence for the adapter unit test."}]


def reply(content='{"text":"Synthetic generated interpretation."}', *, finish_reason="stop", usage=None):
    response = {"choices": [{"index": 0, "finish_reason": finish_reason,
                              "message": {"role": "assistant", "content": content}}]}
    if usage is not None:
        response["usage"] = usage
    return response


class Response:
    def __init__(self, payload=None, *, status=200):
        self.status = status
        self.data = (payload if isinstance(payload, bytes) else json.dumps(payload if payload is not None else reply()).encode())
        self.read = Mock(side_effect=lambda limit: self.data[:limit])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class NIMTests(unittest.TestCase):
    def setUp(self):
        # Explicitly replace any real environment credential for every test.
        self.environment = patch.dict(os.environ, {"NVIDIA_API_KEY": KEY})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.opener = Mock()
        self.factory = patch("icb_copilot.nim.build_opener", return_value=self.opener)
        self.opener_factory = self.factory.start()
        self.addCleanup(self.factory.stop)
        self.sleep = patch("icb_copilot.nim.time.sleep")
        self.sleeper = self.sleep.start()
        self.addCleanup(self.sleep.stop)

    def error(self, status):
        # A reflected key in every location must never reach the public error.
        body = io.BytesIO(("provider body " + KEY).encode())
        return HTTPError(DEFAULT_NIM_BASE_URL + "/" + KEY, status, "provider reason " + KEY,
                         {"X-Error": KEY}, body)

    def assert_sanitized(self, error):
        rendered = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        self.assertNotIn(KEY, rendered)
        self.assertNotIn("provider body", rendered)
        self.assertNotIn("provider reason", rendered)

    def test_lazy_defaults_and_secret_free_metadata(self):
        adapter = NIMBackend()
        self.opener.open.assert_not_called()
        metadata = adapter.metadata
        self.assertEqual(metadata["backend"], "nim")
        self.assertEqual(metadata["model"], {"model_id": DEFAULT_NIM_MODEL, "revision": "provider-managed"})
        self.assertEqual(metadata["settings"], {"base_url": DEFAULT_NIM_BASE_URL, "max_tokens": 200, "seed": 42,
                                             "temperature": 0.0, "timeout": 120.0, "max_retries": 2,
                                             "json_mode": "json_schema", "enable_thinking": False})
        self.assertEqual(metadata["execution"], {"remote_requests": 0, "remote_successes": 0,
                                              "generation_calls": 0, "generated_records": 0,
                                              "message_sha256": []})
        self.assertNotIn(KEY, json.dumps(metadata))
        self.assertFalse(any("key" in name for name in vars(adapter)))

    def test_payload_auth_order_usage_and_message_digests(self):
        usage = {"prompt_tokens": 100, "completion_tokens": 12, "total_tokens": 112}
        self.opener.open.side_effect = [Response(reply(usage=usage)), Response(reply('{"text":"Second reply."}', usage=usage))]
        adapter = NIMBackend()
        second_messages = [*MESSAGES[:-1], {"role": "user", "content": "Second synthetic case."}]
        results = adapter.generate([MESSAGES, second_messages])
        self.assertEqual(results, ['{"text":"Synthetic generated interpretation."}', '{"text":"Second reply."}'])
        digests = []
        for call, conversation in zip(self.opener.open.call_args_list, [MESSAGES, second_messages]):
            request = call.args[0]
            self.assertEqual(request.full_url, DEFAULT_NIM_BASE_URL + "/chat/completions")
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Authorization"), "Bearer " + KEY)
            self.assertEqual(request.get_header("Content-type"), "application/json")
            self.assertEqual(call.kwargs, {"timeout": 120.0})
            payload = json.loads(request.data)
            self.assertEqual(payload, {"model": DEFAULT_NIM_MODEL, "messages": conversation,
                                      "max_tokens": 200, "temperature": 0.0, "seed": 42, "stream": False, "n": 1,
                                      "chat_template_kwargs": {"enable_thinking": False},
                                      "response_format": {"type": "json_schema", "json_schema": {
                                          "name": "icb_reply", "strict": True, "schema": REPLY_SCHEMA}}})
            self.assertNotIn(KEY, request.data.decode())
            canonical = json.dumps(conversation, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
            digests.append(hashlib.sha256(canonical.encode()).hexdigest())
        self.assertEqual(adapter.metadata["execution"], {"remote_requests": 2, "remote_successes": 2,
                                                       "generation_calls": 1, "generated_records": 2,
                                                       "message_sha256": digests,
                                                       "token_usage": {"prompt_tokens": 200, "completion_tokens": 24, "total_tokens": 224}})
        self.assertNotIn(KEY, json.dumps(adapter.metadata))
        self.assertNotIn(MESSAGES[1]["content"], json.dumps(adapter.metadata))

    def test_key_is_read_at_generation_and_never_saved_on_adapter(self):
        adapter = NIMBackend()
        self.opener.open.return_value = Response()
        adapter.generate([MESSAGES])
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "different-synthetic-key"}):
            adapter.generate([MESSAGES])
        keys = [call.args[0].get_header("Authorization") for call in self.opener.open.call_args_list]
        self.assertEqual(keys, ["Bearer " + KEY, "Bearer different-synthetic-key"])
        self.assertNotIn(KEY, json.dumps(adapter.metadata))
        self.assertNotIn("different-synthetic-key", json.dumps(adapter.metadata))
        self.assertEqual(adapter.metadata["execution"]["generation_calls"], 2)

    def test_missing_or_invalid_key_fails_before_network(self):
        for value in ("", KEY + "\n", KEY + "\rInjected: header", " " + KEY, "non-ascii-\u00e9", KEY + "\x7f"):
            with self.subTest(value=value), patch.dict(os.environ, {"NVIDIA_API_KEY": value}):
                adapter = NIMBackend()
                with self.assertRaisesRegex(ValueError, "NVIDIA_API_KEY") as raised:
                    adapter.generate([MESSAGES])
                self.assert_sanitized(raised.exception)
                self.assertEqual(adapter.metadata["execution"]["remote_requests"], 0)
        with patch.dict(os.environ):
            os.environ.pop("NVIDIA_API_KEY", None)
            with self.assertRaisesRegex(ValueError, "required"):
                NIMBackend().generate([MESSAGES])
        self.opener.open.assert_not_called()

    def test_empty_generation_needs_no_credential_and_counts_no_requests(self):
        with patch.dict(os.environ, {"NVIDIA_API_KEY": ""}):
            adapter = NIMBackend()
            self.assertEqual(adapter.generate([]), [])
        self.opener.open.assert_not_called()
        self.assertEqual(adapter.metadata["execution"]["generation_calls"], 0)

    def test_all_conversations_are_validated_before_network(self):
        for invalid in ([], None, [{"role": "user", "content": ""}], [{"role": "user", "content": 1}],
                        [{"role": ["user"], "content": "test"}], [{"role": "tool", "content": "test"}],
                        [{"role": "user", "content": "test", "extra": "not part of the chat contract"}]):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "role/content"):
                NIMBackend().generate([MESSAGES, invalid])
        self.opener.open.assert_not_called()

    def test_json_mode_is_explicit_and_settings_can_be_configured(self):
        for mode, expected in (("json_object", {"type": "json_object"}), ("none", None)):
            with self.subTest(mode=mode):
                self.opener.open.return_value = Response()
                adapter = NIMBackend("nvidia/synthetic-test-model", max_tokens=300, seed=7, temperature=0.2,
                                     timeout=30, max_retries=0, json_mode=mode)
                adapter.generate([MESSAGES])
                payload = json.loads(self.opener.open.call_args.args[0].data)
                self.assertEqual(payload.get("response_format"), expected)
                self.assertEqual(payload["model"], "nvidia/synthetic-test-model")
                self.assertEqual((payload["max_tokens"], payload["seed"], payload["temperature"]), (300, 7, 0.2))
                self.assertEqual(self.opener.open.call_args.kwargs, {"timeout": 30})
                self.assertEqual(adapter.metadata["settings"]["json_mode"], mode)

    def test_invalid_constructor_settings_are_rejected(self):
        cases = [{"max_tokens": 0}, {"max_tokens": 1025}, {"max_tokens": True}, {"seed": -1}, {"seed": True},
                 {"temperature": float("nan")}, {"temperature": 2}, {"temperature": "0"},
                 {"timeout": 0}, {"timeout": float("inf")}, {"timeout": float("nan")}, {"timeout": 601},
                 {"max_retries": -1}, {"max_retries": 6}, {"max_retries": True}, {"json_mode": "automatic"},
                 {"model_id": "https://other.example/model"}, {"model_id": KEY + "\n"}]
        for settings in cases:
            with self.subTest(settings=settings), self.assertRaises(ValueError) as raised:
                NIMBackend(**settings)
            self.assert_sanitized(raised.exception)
        self.opener.open.assert_not_called()

    def test_only_approved_https_endpoint_is_allowed(self):
        invalid = ["http://integrate.api.nvidia.com/v1", "https://evil.example/v1",
                   "https://integrate.api.nvidia.com.evil.example/v1", "https://api.nvidia.com/v1",
                   "https://" + KEY + "@integrate.api.nvidia.com/v1", "https://user:" + KEY + "@integrate.api.nvidia.com/v1",
                   DEFAULT_NIM_BASE_URL + "?key=" + KEY, DEFAULT_NIM_BASE_URL + "#" + KEY,
                   DEFAULT_NIM_BASE_URL + "?", DEFAULT_NIM_BASE_URL + "#",
                   "https://integrate.api.nvidia.com:80/v1", "https://integrate.api.nvidia.com:bad/v1",
                   "https://integrate.api.nvidia.com/v1/../other", DEFAULT_NIM_BASE_URL + "/chat/completions",
                   "https://integrate.api.nvidia.com./v1", "\n" + DEFAULT_NIM_BASE_URL,
                   "https://[invalid/v1", "https://integrate.api.nvidia.com/v1\x00", None]
        for endpoint in invalid:
            with self.subTest(endpoint=endpoint), self.assertRaisesRegex(ValueError, "NIM base_url") as raised:
                NIMBackend(base_url=endpoint)
            self.assert_sanitized(raised.exception)
        for endpoint in (DEFAULT_NIM_BASE_URL + "/", "https://INTEGRATE.API.NVIDIA.COM:443/v1"):
            self.assertEqual(NIMBackend(base_url=endpoint).metadata["settings"]["base_url"], DEFAULT_NIM_BASE_URL)
        self.opener.open.assert_not_called()

    def test_redirect_handler_refuses_to_construct_any_redirect_request(self):
        NIMBackend()
        handler = self.opener_factory.call_args.args[0]
        self.assertIsInstance(handler, HTTPRedirectHandler)
        request = Request(DEFAULT_NIM_BASE_URL, data=b"{}", headers={"Authorization": "Bearer " + KEY})
        for status in (301, 302, 303, 307, 308):
            self.assertIsNone(handler.redirect_request(request, None, status, "redirect", {}, "https://evil.example"))

    def test_nonretryable_http_errors_are_sanitized_and_never_read(self):
        for status in (400, 401, 403, 404, 422, 302, 307, 418):
            with self.subTest(status=status):
                error = self.error(status)
                error.read = Mock(side_effect=AssertionError("error bodies must never be read"))
                self.opener.open.side_effect = error
                adapter = NIMBackend()
                with self.assertRaisesRegex(RuntimeError, f"HTTP {status}") as raised:
                    adapter.generate([MESSAGES])
                self.assert_sanitized(raised.exception)
                if status in {400, 422}:
                    self.assertIn("json_mode", str(raised.exception))
                if status in {302, 307}:
                    self.assertIn("redirect refused", str(raised.exception))
                error.read.assert_not_called()
                self.assertEqual(adapter.metadata["execution"]["remote_requests"], 1)
                self.assertEqual(adapter.metadata["execution"]["remote_successes"], 0)
                self.assertEqual(adapter.metadata["execution"]["generation_calls"], 0)
        self.sleeper.assert_not_called()

    def test_non200_returned_response_is_checked_before_reading(self):
        response = Response(b"body " + KEY.encode(), status=401)
        self.opener.open.return_value = response
        with self.assertRaisesRegex(RuntimeError, "HTTP 401") as raised:
            NIMBackend().generate([MESSAGES])
        response.read.assert_not_called()
        self.assert_sanitized(raised.exception)

    def test_rate_limit_and_server_errors_retry_boundedly(self):
        self.opener.open.side_effect = [self.error(429), self.error(503), Response()]
        adapter = NIMBackend()
        self.assertEqual(len(adapter.generate([MESSAGES])), 1)
        self.assertEqual(adapter.metadata["execution"]["remote_requests"], 3)
        self.assertEqual(adapter.metadata["execution"]["remote_successes"], 1)
        self.assertEqual([call.args[0] for call in self.sleeper.call_args_list], [1, 2])

    def test_retry_exhaustion_has_no_success_or_generation_claim(self):
        self.opener.open.side_effect = [self.error(500), self.error(500), self.error(500)]
        adapter = NIMBackend(max_retries=2)
        with self.assertRaisesRegex(RuntimeError, "HTTP 500") as raised:
            adapter.generate([MESSAGES])
        self.assert_sanitized(raised.exception)
        execution = adapter.metadata["execution"]
        self.assertEqual(execution["remote_requests"], 3)
        for name in ("remote_successes", "generation_calls", "generated_records"):
            self.assertEqual(execution[name], 0)
        self.assertEqual(self.sleeper.call_count, 2)

    def test_timeouts_including_urllib_wrapper_are_retryable(self):
        for error in (TimeoutError(KEY), URLError(TimeoutError(KEY))):
            with self.subTest(error=type(error)):
                self.opener.open.side_effect = [error, Response()]
                adapter = NIMBackend(max_retries=1)
                self.assertEqual(len(adapter.generate([MESSAGES])), 1)
                self.assertEqual(adapter.metadata["execution"]["remote_requests"], 2)

    def test_timeout_exhaustion_and_other_network_errors_are_sanitized(self):
        for error, expected in ((TimeoutError(KEY), "timed out"), (URLError(KEY), "connection failed"),
                                (OSError(KEY), "connection failed")):
            with self.subTest(error=type(error)):
                self.opener.open.side_effect = error
                adapter = NIMBackend(max_retries=0)
                with self.assertRaisesRegex(RuntimeError, expected) as raised:
                    adapter.generate([MESSAGES])
                self.assert_sanitized(raised.exception)
                self.assertEqual(adapter.metadata["execution"]["remote_requests"], 1)
        self.sleeper.assert_not_called()

    def test_non_timeout_network_failure_is_not_retried(self):
        self.opener.open.side_effect = URLError("TLS connection problem " + KEY)
        with self.assertRaisesRegex(RuntimeError, "connection failed") as raised:
            NIMBackend().generate([MESSAGES])
        self.assert_sanitized(raised.exception)
        self.assertEqual(self.opener.open.call_count, 1)
        self.sleeper.assert_not_called()

    def test_invalid_outer_json_and_oversized_responses_are_rejected(self):
        for payload in (b"not json " + KEY.encode(), b"\xff", b'{"choices": [], "choices": []}', b"[NaN]", b" " * (1024 * 1024 + 1)):
            with self.subTest(size=len(payload)):
                self.opener.open.return_value = Response(payload)
                adapter = NIMBackend()
                with self.assertRaises(RuntimeError) as raised:
                    adapter.generate([MESSAGES])
                self.assert_sanitized(raised.exception)
                self.assertEqual(adapter.metadata["execution"]["remote_requests"], 1)
                self.assertEqual(adapter.metadata["execution"]["remote_successes"], 0)
        self.sleeper.assert_not_called()

    def test_response_count_must_be_exactly_one(self):
        for payload in ([], {}, {"choices": []}, {"choices": "one"}, {"choices": [None]},
                        {"choices": reply()["choices"] * 2}):
            with self.subTest(payload=payload):
                self.opener.open.return_value = Response(payload)
                with self.assertRaisesRegex(RuntimeError, "output count"):
                    NIMBackend().generate([MESSAGES])

    def test_finish_reason_must_indicate_complete_text(self):
        for reason in (None, "length", "content_filter", "tool_calls", "arbitrary reason " + KEY):
            with self.subTest(reason=reason):
                self.opener.open.return_value = Response(reply(finish_reason=reason))
                with self.assertRaisesRegex(RuntimeError, "truncated" if reason == "length" else "complete text") as raised:
                    NIMBackend().generate([MESSAGES])
                self.assert_sanitized(raised.exception)

    def test_message_must_contain_json_with_one_string_text_field(self):
        for content in (None, [], "", "x" * 3001, "prose " + KEY, '```json\n{"text":"x"}\n```',
                        '{"text":null}', '{"text":42}', '{"text":"x","extra":"y"}',
                        '{"text":"x","text":"y"}', '["text"]', '{"text":NaN}'):
            with self.subTest(content=content):
                self.opener.open.return_value = Response(reply(content))
                with self.assertRaises(RuntimeError) as raised:
                    NIMBackend().generate([MESSAGES])
                self.assert_sanitized(raised.exception)
        self.sleeper.assert_not_called()

    def test_refusals_and_tool_calls_are_rejected_without_reflected_detail(self):
        for message in (None, {"refusal": KEY}, {"tool_calls": [{"arguments": KEY}]}):
            payload = reply()
            payload["choices"][0]["message"] = message
            self.opener.open.return_value = Response(payload)
            with self.assertRaisesRegex(RuntimeError, "assistant text") as raised:
                NIMBackend().generate([MESSAGES])
            self.assert_sanitized(raised.exception)

    def test_invalid_usage_fields_are_ignored_and_metadata_is_a_copy(self):
        self.opener.open.return_value = Response(reply(usage={"prompt_tokens": -1, "completion_tokens": True,
                                                            "total_tokens": KEY, "other": KEY}))
        adapter = NIMBackend()
        adapter.generate([MESSAGES])
        metadata = adapter.metadata
        self.assertNotIn("token_usage", metadata["execution"])
        metadata["settings"]["base_url"] = "https://evil.example"
        metadata["execution"]["message_sha256"].clear()
        self.assertEqual(adapter.metadata["settings"]["base_url"], DEFAULT_NIM_BASE_URL)
        self.assertEqual(len(adapter.metadata["execution"]["message_sha256"]), 1)
        self.assertNotIn(KEY, json.dumps(adapter.metadata))

    def test_partial_batch_failure_records_received_replies_without_claiming_returned_batch(self):
        self.opener.open.side_effect = [Response(), self.error(401)]
        adapter = NIMBackend()
        with self.assertRaisesRegex(RuntimeError, "HTTP 401"):
            adapter.generate([MESSAGES, MESSAGES])
        execution = adapter.metadata["execution"]
        self.assertEqual(execution["remote_requests"], 2)
        self.assertEqual(execution["remote_successes"], 1)
        self.assertEqual(execution["generation_calls"], 0)
        self.assertEqual(execution["generated_records"], 0)
        self.assertEqual(len(execution["message_sha256"]), 1)


if __name__ == "__main__":
    unittest.main()
