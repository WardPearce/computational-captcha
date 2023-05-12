from pydantic import BaseModel, Field


class CaptchaModel(BaseModel):
    id: str = Field(..., alias="_id")
    secret: str
    salt: str
    expires: float


class ValidateModel(BaseModel):
    id: str = Field(..., alias="_id", regex=r"^[a-fA-F0-9]{24}$")
    computed_hash: str = Field(..., max_length=42)
