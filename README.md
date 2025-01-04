# Nebula Python SDK

A Python client for interacting with the Nebula API, providing a seamless interface for chat-based interactions with thirdweb's Nebula service.

## Installation

```bash
pip install thirdweb-nebula
```

## Quick Start

```python
from nebula import Nebula

# Initialize the client
client = Nebula(
    base_url="https://nebula-api.thirdweb.com",
    secret_key="your-secret-key"
)

# Basic chat request
response = client.chat("Hello, Nebula!")
print(response.message)

# Streaming chat request
for chunk in client.chat("Hello, Nebula!", stream=True):
    print(chunk, end="")
```

## Features

- Synchronous and streaming chat responses
- Session management
- Configurable execution environments
- Context filtering capabilities
- Custom model selection
- Type-safe request/response handling with Pydantic

## Advanced Usage

### Context Filtering

Filter the context of your chat based on specific blockchain parameters:

```python
from nebula import ContextFilter

context = ContextFilter(
    chain_ids=["1", "137"],
    contract_addresses=["0x..."],
    wallet_addresses=["0x..."]
)

response = client.chat(
    "Tell me about my contracts",
    context_filter=context
)
```

### Execution Configuration

Configure how your requests are executed:

```python
from nebula import ExecuteConfig

config = ExecuteConfig(
    mode="client",
    signer_wallet_address="0x...",
    engine_url="https://your-engine.com"
)

response = client.chat(
    "Execute this transaction",
    execute_config=config
)
```

### Session Management

Maintain conversation context across multiple messages:

```python
response = client.chat(
    "Remember this conversation",
    session_id="unique-session-id"
)
```

## Error Handling

The SDK provides custom exceptions for proper error handling:

```python
from nebula import NebulaAPIError

try:
    response = client.chat("Hello")
except NebulaAPIError as e:
    print(f"API Error: {e}")
```

## Configuration

The client can be configured with:

- `base_url`: The base URL for the Nebula API (defaults to "https://nebula-api.thirdweb.com")
- `secret_key`: Your thirdweb API secret key for authentication

## Development

### Requirements

- Python 3.12+
- `requests`
- `pydantic`

### Running Tests

```bash
pytest tests/
```

## License

[License Type] - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
