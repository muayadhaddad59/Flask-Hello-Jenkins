import json
from app import app

def test_health():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    data = json.loads(res.data.decode())
    assert data.get("ok") is True
