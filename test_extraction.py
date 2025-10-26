import pytest
from fastapi.testclient import TestClient
from application import app  # import your FastAPI app

client = TestClient(app)

# --------------------------
# sample test data
# --------------------------
single_json = '{ "name": "Alice", "age": 30 }'
double_json = '"{\\"name\\": \\"Bob\\", \\"age\\": 25,}"'
messy_llm_output = 'random text { "id": 1, "valid": true, } end text'

# --------------------------
# tests
# --------------------------
def test_single_json():
    response = client.post("/extract", data=single_json)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["count"] == 1
    assert json_data["results"][0]["valid"] is True
    assert json_data["results"][0]["json"]["name"] == "Alice"

def test_double_json():
    response = client.post("/extract", data=double_json)
    print("response json:", response.json())              # parsed JSON

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["count"] == 1
    assert json_data["results"][0]["valid"] is True
    assert json_data["results"][0]["json"]["name"] == "Bob"

def test_messy_llm_output():
    response = client.post("/extract", data=messy_llm_output)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["count"] == 1
    assert json_data["results"][0]["valid"] is True
    assert json_data["results"][0]["json"]["id"] == 1
