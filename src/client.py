from collections.abc import Generator
from typing import Any

import requests
import sseclient  # For streaming SSE (Server-Sent Events)

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
        api_key: str | None = None
    ):
        """
        :param base_url: The base URL of your Nebula service.
                         Defaults to "https://nebula-api.thirdweb.com".
        :param api_key: Optional API key or token for authentication.
        """
        if not base_url:
            base_url = "https://nebula-api.thirdweb.com"
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> dict[str, str]:
        """
        Return the default headers for the request.
        Include API key or other auth tokens if required.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(
        self,
        message: str,
        stream: bool = False,
        session_id: str | None = None,
        execute_config: ExecuteConfig | dict[str, Any] | None = None,
        context_filter: ContextFilter | dict[str, Any] | None = None,
        model_name: str | None = None
    ) -> ChatResponse | Generator[str, None, None]:
        """
        Send a chat message to Nebula's /chat endpoint. 

        If stream=False, returns a single ChatResponse.
        If stream=True, yields each part of the streaming response (Server-Sent Events).
        
        :param message: The text of the user’s message to the Nebula agent.
        :param stream: Whether to return (yield) a streaming response.
        :param session_id: Optional session ID to maintain conversation context.
        :param config: A dict or ExecuteConfig object for execution (legacy).
        :param execute_config: A dict or ExecuteConfig object for execution (new).
        :param context_filter: A dict or ContextFilter object for chain/contract context.
        :param model_name: Optional model name (e.g. "gpt-4").
        :return: 
            - If stream=False, a ChatResponse with the agent's reply.
            - If stream=True, a generator yielding strings (chunks of the streamed response).
        """
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

        if not stream:
            # Non-streaming request
            response = requests.post(url, json=payload, headers=self._headers())
            if response.status_code != 200:
                raise NebulaAPIError(
                    f"Request failed with status code {response.status_code}: {response.text}"
                )

            try:
                data = response.json()
                return ChatResponse(**data)
            except ValueError:
                raise NebulaAPIError("Invalid JSON response from Nebula API.")

        else:
            # Streaming request with SSE
            response = requests.post(url, json=payload, headers=self._headers(), stream=True)
            if response.status_code != 200:
                raise NebulaAPIError(
                    f"Streaming request failed with status code {response.status_code}: {response.text}"
                )
            client = sseclient.SSEClient(response)
            # Yield each part of the streaming response as it arrives
            for event in client:
                if event.event == "message":
                    yield event.data
