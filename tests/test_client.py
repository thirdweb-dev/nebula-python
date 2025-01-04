import pytest
from unittest.mock import patch, MagicMock

from src.nebula.client import Nebula
from src.nebula.exceptions import NebulaAPIError
from src.nebula.models import ChatResponse

@pytest.fixture
def nebula_client():
    """
    Pytest fixture for creating a fresh NebulaClient 
    with defaults for each test.
    """
    return Nebula(secret_key="test-secret-key")


def test_non_streaming_success(nebula_client: Nebula):
    """
    Test a successful non-streaming chat request 
    where the Nebula API returns a 200 status and valid JSON.
    """
    with patch("src.client.requests.post") as mock_post:
        # Mock requests.post to return a fake successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = { "message": "Hello from Nebula!" }
        mock_post.return_value = mock_response

        # Call the chat function
        response = nebula_client.chat("Hello from test!")

        # Verify the request was made to /chat
        mock_post.assert_called_once_with(
            f"{nebula_client.base_url}/chat",
            json={
                "message": "Hello from test!",
                "stream": False,
            },
            headers=nebula_client._headers(),
            stream=False
        )

        # Check the response
        assert isinstance(response, ChatResponse)
        assert response.message == "Hello from Nebula!"


def test_non_streaming_error(nebula_client: Nebula):
    """
    Test non-streaming chat request where the API returns an error status.
    This should raise NebulaAPIError.
    """
    with patch("src.client.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(NebulaAPIError) as excinfo:
            nebula_client.chat("Trigger error")

        assert "Request failed with status code 500: Internal Server Error" in str(excinfo.value)


def test_streaming_success(nebula_client: Nebula):
    """
    Test a successful streaming chat request using iter_lines.
    """
    with patch("src.client.requests.post") as mock_post:
        # Mock the POST response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Mock iter_lines to return encoded SSE-formatted data
        mock_response.iter_lines.return_value = [
            b'data: First chunk',
            b'data: Second chunk',
            b'data: Third chunk'
        ]
        mock_post.return_value = mock_response

        # Now call chat with stream=True
        chunks = list(nebula_client.chat("Hello streaming!", stream=True))

        # Verify the request was made with stream=True
        mock_post.assert_called_once_with(
            f"{nebula_client.base_url}/chat",
            json={
                "message": "Hello streaming!",
                "stream": True,
            },
            headers=nebula_client._headers(),
            stream=True
        )

        # We expect each chunk without the "data: " prefix
        assert chunks == ["First chunk", "Second chunk", "Third chunk"]

        # We expect each event's data to be yielded
        assert chunks == ["First chunk", "Second chunk", "Third chunk"]


def test_streaming_error(nebula_client: Nebula):
    """
    Test that a streaming chat request raises an error if the API returns non-200 status.
    """
    with patch("src.client.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_post.return_value = mock_response

        with pytest.raises(NebulaAPIError) as excinfo:
            # Force generator iteration to trigger the error
            list(nebula_client.chat("Hello streaming error!", stream=True))

        assert "Request failed with status code 403: Forbidden" in str(excinfo.value)
