from main import app
from fastapi.testclient import TestClient

client = TestClient(app)
def test_login():
    response = client.post("/api/user/login",json={"username":"yuanshen","password":"123456"},headers={"Authorization":"Bearer ef0d78b0-95f2-494b-8295-f203ad53ebcb"})
    assert response.status_code == 200

def test_register():
    response = client.post("/api/user/register",json={"username":"yuanshen2","password":"123456"})
    assert response.status_code == 200

