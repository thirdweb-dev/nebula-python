import pytest
from src.client import Nebula
from src.models import ChatResponse
from dotenv import load_dotenv
import os

load_dotenv()

THIRDWEB_API_SECRET_KEY = os.environ.get("THIRDWEB_API_SECRET_KEY")

@pytest.fixture
def nebula_local():
    """
    Returns a Nebula instance that points to the local Nebula server.
    """
    return Nebula(base_url="http://localhost:4242", secret_key=THIRDWEB_API_SECRET_KEY)

def test_local_chat(nebula_local: Nebula):
    """
    This test makes a real HTTP request to the local Nebula instance.
    Make sure Nebula is running on localhost:4242.
    """
    response = nebula_local.chat("Hello from local test!")

    # Add assertions based on what you expect from your local Nebula instance
    assert isinstance(response, ChatResponse)

    print("Response:", response.message)
    assert response.message is not None

def test_local_chat_streaming(nebula_local: Nebula):
    chunks = list(nebula_local.chat("Hello streaming test!", stream=True))
    print("Streamed chunks:", chunks)
    # Basic assertion that we got some data
    assert len(chunks) > 0

