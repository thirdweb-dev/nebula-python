from collections.abc import Generator
from typing import Any

import requests

from .exceptions import NebulaAPIError
from .models import ChatParams, ChatResponse, ContextFilter, ExecuteConfig
from .utils import parse_or_none  # Our utility function from above


class Nebula:
    """
    A client to interact with the Nebula chat endpoint.
    """

    def __init__(
        self,
        base_url: str | None = None,
        secret_key: str | None = None
    ):
        """
        :param base_url: The base URL of your Nebula service.
                         Defaults to "https://nebula-api.thirdweb.com".
        :param api_key: Optional API key or token for authentication.
        """
        if not base_url:
            base_url = "https://nebula-api.thirdweb.com"
        self.base_url = base_url.rstrip("/")
        self.secret_key = secret_key

    def _headers(self) -> dict[str, str]:
        """
        Return the default headers for the request.
        Include API key or other auth tokens if required.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.secret_key:
            headers["x-secret-key"] = self.secret_key
        return headers

    def _make_streaming_request(self, response: requests.Response) -> Generator[str, None, None]:
        """Handle streaming response"""
        for line in response.iter_lines():
            if line:
                # Decode the line from bytes to string
                line = line.decode("utf-8")
                # SSE format typically starts with "data: "
                if line.startswith("data: "):
                    # Remove the "data: " prefix and yield the content
                    yield line[6:]

    def _make_request(self, response: requests.Response) -> ChatResponse:
        """Handle non-streaming response"""
        try:
            data = response.json()
            return ChatResponse(**data)
        except ValueError as e:
            raise NebulaAPIError(f"Invalid JSON response from Nebula API: {e}")


    def chat(
        self,
        message: str,
        stream: bool = False,
        session_id: str | None = None,
        execute_config: ExecuteConfig | dict[str, Any] | None = None,
        context_filter: ContextFilter | dict[str, Any] | None = None,
        model_name: str | None = None
    ) -> ChatResponse | Generator[str, None, None]:
        """Internal method to make the actual chat request"""
        url = f"{self.base_url}/chat"

        # Convert dicts to Pydantic objects if needed
        parsed_execute_config = parse_or_none(execute_config, ExecuteConfig)
        parsed_context_filter = parse_or_none(context_filter, ContextFilter)

        # Build Pydantic request model for validation
        chat_params = ChatParams(
            message=message,
            stream=stream,
            session_id=session_id,
            execute_config=parsed_execute_config,
            context_filter=parsed_context_filter,
            model_name=model_name
        )

        payload = chat_params.model_dump(exclude_none=True)
        response = requests.post(url, json=payload, headers=self._headers(), stream=stream)

        if response.status_code != 200:
            raise NebulaAPIError(
                f"Request failed with status code {response.status_code}: {response.text}"
            )

        if stream:
            return self._make_streaming_request(response)
        return self._make_request(response)

