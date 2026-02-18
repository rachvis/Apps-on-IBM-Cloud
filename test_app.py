import app as vibe_app


def test_home_endpoint():
    client = vibe_app.app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["status"] == "slaying"


def test_roast_disabled_by_default(monkeypatch):
    monkeypatch.setenv("FLAG_ENABLE_DAILY_ROAST", "false")
    client = vibe_app.app.test_client()
    res = client.get("/roast")
    assert res.status_code == 404
