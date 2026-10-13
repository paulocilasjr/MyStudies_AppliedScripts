"""Verify the local demo API with synthetic inputs and an ephemeral port."""

import http.client
import json
import threading
import unittest

from nemotron_copilot import Copilot
from icb_copilot.server import create_server

from helpers import clinical_only, prediction


class LocalHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(Copilot(backend="mock"), port=0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, payload=None, content_type="application/json", headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        try:
            body = json.dumps(payload).encode("utf-8") if payload is not None else None
            request_headers = {"Content-Type": content_type}
            request_headers.update(headers or {})
            connection.request(method, path, body=body, headers=request_headers)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), json.loads(response.read())
        finally:
            connection.close()

    def test_health_is_available_without_loading_a_model(self):
        status, headers, payload = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["backend"], "mock")
        self.assertFalse(payload["model_loaded"])
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_single_patient_matches_python_api(self):
        source = prediction()
        status, _, output = self.request("POST", "/v1/interpret", source)
        self.assertEqual(status, 200)
        self.assertEqual(output, Copilot(backend="mock").interpret(source))

    def test_batch_preserves_order_and_missing_modalities(self):
        source = [prediction("P48"), clinical_only("P07")]
        status, _, output = self.request("POST", "/v1/interpret-batch", {"patients": source})
        self.assertEqual(status, 200)
        self.assertEqual([row["patient_id"] for row in output["results"]], ["P48", "P07"])
        self.assertEqual(set(output["results"][1]["predictions"]), {"clinical"})

    def test_bad_input_does_not_expose_a_traceback(self):
        source = prediction()
        source["predictions"]["clinical"]["probability"] = 4.5
        status, _, output = self.request("POST", "/v1/interpret", source)
        self.assertEqual(status, 422)
        self.assertIn("error", output)
        self.assertNotIn("Traceback", output["error"])

    def test_bad_batch_sizes_and_duplicate_ids_are_rejected(self):
        for patients in [[], [prediction(), prediction()], [clinical_only(f"P{i}") for i in range(129)]]:
            with self.subTest(patient_count=len(patients)):
                status, _, output = self.request("POST", "/v1/interpret-batch", {"patients": patients})
                self.assertEqual(status, 422)
                self.assertIn("error", output)

    def test_body_size_limit_is_checked_before_reading(self):
        status, _, output = self.request(
            "POST", "/v1/interpret", {}, headers={"Content-Length": "2000001"}
        )
        self.assertEqual(status, 413)
        self.assertIn("maximum size", output["error"])

    def test_wrong_content_type_is_rejected(self):
        status, _, _ = self.request("POST", "/v1/interpret", prediction(), content_type="text/plain")
        self.assertEqual(status, 415)

    def test_unknown_endpoint_is_not_accepted(self):
        status, _, _ = self.request("GET", "/patients/P48")
        self.assertEqual(status, 404)

    def test_service_refuses_non_loopback_bind_addresses(self):
        for host in ["0.0.0.0", "192.0.2.1", "::1", "untrusted.example"]:
            with self.subTest(host=host):
                with self.assertRaises(ValueError):
                    create_server(Copilot(backend="mock"), host=host, port=0)


if __name__ == "__main__":
    unittest.main()
