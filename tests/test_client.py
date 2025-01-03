import pytest
from unittest.mock import patch, MagicMock

from src.client import Nebula
from src.exceptions import NebulaAPIError
from src.models import ChatResponse

@pytest.fixture
def nebula_client():
    """
    Pytest fixture for creating a fresh NebulaClient 
    with defaults for each test.
    """
    return Nebula(api_key="test-api-key")


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
    Test a successful streaming chat request. 
    We mock out SSEClient so we can control the chunks.
    """
    with patch("src.client.requests.post") as mock_post, \
         patch("sseclient.SSEClient") as mock_sse_client:

        # Mock the POST response (must be status 200 for a successful stream)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mock SSEClient to yield some SSE events
        mock_event_1 = MagicMock(event="message", data="First chunk")
        mock_event_2 = MagicMock(event="message", data="Second chunk")
        mock_event_3 = MagicMock(event="message", data="Third chunk")

        # sseclient.SSEClient(response) will be replaced by our mock_sse_client,
        # which we make iterable by just returning a list of these mock events
        mock_sse_client.return_value = [mock_event_1, mock_event_2, mock_event_3]

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

        # We expect each event's data to be yielded
        assert chunks == ["First chunk", "Second chunk", "Third chunk"]


def test_streaming_error(nebula_client: Nebula):
    """
    Test that a streaming chat request returns an error if the API is not 200.
    """
    with patch("src.client.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_post.return_value = mock_response

        # Because chat returns a generator, we wrap it with list()
        # to force iteration (and thus the request) to happen,
        # which should raise NebulaAPIError.
        with pytest.raises(NebulaAPIError) as excinfo:
            list(nebula_client.chat("Hello streaming error!", stream=True))

        assert "Streaming request failed with status code 403" in str(excinfo.value)

