from pathlib import Path

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)
YAML = (Path(__file__).resolve().parents[2] / "machines" / "reconocedora.yaml").read_text(encoding="utf-8")


def test_validate_ok():
    j = client.post("/validate", json={"yaml": YAML}).json()
    assert j["ok"] and j["machine"]["initial"] == "0" and j["errors"] == []


def test_validate_errores():
    j = client.post("/validate", json={"yaml": "q_states: 1"}).json()
    assert not j["ok"] and j["errors"]


def test_run():
    j = client.post("/run", json={"yaml": YAML}).json()
    assert [r["accepted"] for r in j["results"]] == [True, True, False, False]
    assert j["results"][0]["steps"][0]["transition"] is None


def test_run_max_steps():
    j = client.post("/run", json={"yaml": YAML, "max_steps": 2}).json()
    assert "límite de pasos" in j["results"][0]["reason"]


def test_run_invalido_400():
    r = client.post("/run", json={"yaml": "x: 1"})
    assert r.status_code == 400 and not r.json()["ok"]


def test_cors():
    r = client.options("/run", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
