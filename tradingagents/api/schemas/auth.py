"""Authentication request/response models."""

from pydantic import BaseModel


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
