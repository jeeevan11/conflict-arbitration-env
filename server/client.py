"""
HTTP client for the Conflict Arbitration Environment.
Used by the training loop to communicate with the FastAPI server.
"""
import json
import urllib.request
import urllib.error


class EnvClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict = None) -> dict:
        data = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(self.base_url + path, method="GET")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def reset(self) -> dict:
        return self._post("/reset")

    def step(self, action: dict) -> dict:
        return self._post("/step", action)

    def state(self) -> dict:
        return self._get("/state")

    def health(self) -> dict:
        return self._get("/health")
