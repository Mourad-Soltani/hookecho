# HookEcho Tests
# Signature: Mourad.Soltani

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    """Health test must pass."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "hookecho"
    assert data["signature"] == "Mourad.Soltani"

def test_create_and_hook():
    # Create endpoint
    res = client.post("/create")
    assert res.status_code == 200
    data = res.json()
    eid = data["endpoint_id"]
    assert len(eid) == 8
    
    # Send a webhook
    hook_res = client.post(f"/hook/{eid}", json={"event": "test", "data": 123})
    assert hook_res.status_code == 200
    assert hook_res.json()["received"] is True
    
    # Inspect
    inspect_res = client.get(f"/inspect/{eid}")
    assert inspect_res.status_code == 200
    assert inspect_res.json()["count"] == 1
    assert "test" in str(inspect_res.json())

def test_invalid_endpoint():
    res = client.post("/hook/nonexistent", json={})
    assert res.status_code == 404
