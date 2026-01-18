import pytest
import json
from moto import mock_aws
from main import app


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-2"
    # Note: Setting dummy credentials is important to prevent boto3 from attempting to use real credentials


@pytest.fixture
def mocked_aws(aws_credentials):
    """Mock all AWS interactions for a test function."""
    with mock_aws():
        yield


@pytest.fixture
def client():
    app.testing = True 
    with app.test_client() as client:
        yield client

@mock_aws
def test_index( client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"

    # def test_generate_api_invalid_request(client):
    #     response = client.post("/api/generate/campaign", json={})
    #     assert response.status_code == 400
    #     data = json.loads(response.data)
    #     assert "error" in data

    # def test_serve_static_file(client):
    #     response = client.get("/style.css")
    #     assert response.status_code == 200
    #     assert response.content_type == "text/css; charset=utf-8"
