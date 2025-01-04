from typing import Literal

from pydantic import BaseModel


class ContextFilter(BaseModel):
    chain_ids: list[str] | None = None
    contract_addresses: list[str] | None = None
    wallet_addresses: list[str] | None = None

class ExecuteConfig(BaseModel):
    mode: Literal["client", "engine", "session_key"] | None = "client"
    signer_wallet_address: str | None = None
    engine_url: str | None = None
    engine_authorization_token: str | None = None
    engine_backend_wallet_address: str | None = None
    smart_account_address: str | None = None
    smart_account_factory_address: str | None = None
    smart_account_session_key: str | None = None

class ChatParams(BaseModel):
    message: str
    stream: bool | None = False
    session_id: str | None = None

    execute_config: ExecuteConfig | None = None
    context_filter: ContextFilter | None = None
    model_name: str | None = None

class ChatResponse(BaseModel):
    message: str

