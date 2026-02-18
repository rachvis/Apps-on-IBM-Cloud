import app as vibe_app


def test_health_endpoint():
    client = vibe_app.app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_roast_returns_message_when_disabled(monkeypatch):
    monkeypatch.setenv("FLAG_SHOW_ROAST", "false")
    client = vibe_app.app.test_client()
    res = client.get("/api/roast")
    assert res.status_code == 200
    assert "napping" in res.get_json()["message"]
