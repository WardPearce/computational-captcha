from pydantic import BaseModel, Field


class CaptchaModel(BaseModel):
    id: str
    secret: str
    salt: str


class ValidateModel(BaseModel):
    id: str = Field(..., regex=r"^[a-fA-F0-9]{24}$")
    computed_hash: str = Field(..., max_length=42)
