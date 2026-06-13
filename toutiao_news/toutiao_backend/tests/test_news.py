from main import app
from fastapi.testclient import TestClient
client = TestClient(app)

def test_get_categories():
    response = client.get("/api/news/categories")
    assert response.status_code == 200
    

def test_get_news_list():
    response = client.get("/api/news/list?categoryId=1")
    assert response.status_code == 200

def test_get_news_detail():
    response = client.get("/api/news/detail?id=1")
    assert response.status_code == 200