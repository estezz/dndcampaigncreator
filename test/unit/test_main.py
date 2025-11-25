
import pytest
import json
from main import app
import main

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.mark.unit
def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"

def test_generate_api_no_api_key(client):
    from main import API_KEY
    original_api_key = API_KEY
    try:
        import main
        main.API_KEY = "TODO"
        response = client.post("/api/generate", json={})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "error" in data
        assert "To get started, get an API key" in data["error"]
    finally:
        main.API_KEY = original_api_key

def test_generate_api_invalid_request(client):
    response = client.post("/api/generate", json={})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "error" in data

def test_serve_static_file(client):
    response = client.get("/style.css")
    assert response.status_code == 200
    assert response.content_type == "text/css; charset=utf-8"

def test_find_key_recursive(client):
    print("starting test_find_key_recursive")
    mydict = { 
                "imagePrompt": {
                                "name" : "plotStepPrompt",
                                "type": "STRING",
                                "description": "A prompt for generating an atmospheric image (16:9) representing this plot step."
                            },
                "key1": {
                     "imagePrompt": {
                                "name" : "plotStepPrompt",
                                "type": "STRING",
                                "description": "A prompt for generating an atmospheric image (16:9) representing this plot step."
                            },
                     "key2": 2,
                     "key3": 3,
                 },
            "key4": 2,
            "key5": 3, }
    return_dict = {}
    main.find_key_recursive(mydict, "imagePrompt", return_dict=return_dict)
    print(return_dict)
    assert return_dict["plotStepPrompt"] == mydict["imagePrompt"]