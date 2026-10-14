"""Loopback-only HTTP integration, intended for an SSH tunnel to Junhao's UI."""
from __future__ import annotations

import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .copilot import Copilot, _strict_json
from .schema import ContractError

MAX_BODY_BYTES = 2_000_000
MAX_BATCH = 128


def create_server(copilot: Copilot, host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    if host != "localhost":
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            raise ValueError("server host must be a loopback IP address or localhost") from None
        if not address.is_loopback or address.version != 4:
            raise ValueError("server host must be an IPv4 loopback address")

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(30)

        def log_message(self, format, *args):
            # Suppress default request logging, including potentially identifying URLs.
            pass

        def send_json(self, status, payload):
            body = json.dumps(payload, ensure_ascii=True, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self.send_json(200, {"status": "ok", "backend": copilot.backend, "schema_version": "1.0",
                                    "model_loaded": copilot.metadata.get("execution", {}).get("model_loaded", False)})
            else:
                self.send_json(404, {"error": "unknown endpoint"})

        def do_POST(self):
            if self.path not in {"/v1/interpret", "/v1/interpret-batch"}:
                self.send_json(404, {"error": "unknown endpoint"})
                return
            if self.headers.get_content_type() != "application/json":
                self.send_json(415, {"error": "Content-Type must be application/json"})
                return
            try:
                lengths = self.headers.get_all("Content-Length", [])
                if len(lengths) != 1 or self.headers.get("Transfer-Encoding"):
                    raise ValueError("one Content-Length header is required; chunked requests are unsupported")
                length = int(lengths[0])
                if length <= 0:
                    raise ValueError("request body must be nonempty")
                if length > MAX_BODY_BYTES:
                    self.send_json(413, {"error": "request body exceeds maximum size"})
                    return
                body = self.rfile.read(length)
                if len(body) != length:
                    raise ValueError("incomplete request body")
                payload = _strict_json(body.decode("utf-8"))
                if self.path == "/v1/interpret":
                    result = copilot.interpret(payload)
                else:
                    if not isinstance(payload, dict) or set(payload) != {"patients"} or not isinstance(payload["patients"], list):
                        raise ContractError("batch request must be an object with one patients list")
                    if not 1 <= len(payload["patients"]) <= MAX_BATCH:
                        raise ContractError(f"batch requires between 1 and {MAX_BATCH} patients")
                    result = {"schema_version": "1.0", "results": copilot.interpret_many(payload["patients"])}
                self.send_json(200, result)
            except (ValueError, UnicodeDecodeError) as exc:
                self.send_json(422, {"error": str(exc)})
            except Exception:
                self.send_json(503, {"error": "local inference failed; inspect the HPC runtime and model configuration"})

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server
