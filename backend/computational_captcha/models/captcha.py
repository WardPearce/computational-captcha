from typing import List

from computational_captcha.env import SETTINGS, ArgonParameters
from pydantic import BaseModel, Field


class GoalModel(BaseModel):
    blake2b: str
    order: int


class CaptchaModel(ArgonParameters):
    salt: str
    secrets: List[str] = Field(..., max_items=SETTINGS.captcha.provided_secrets)
    goals: List[GoalModel]


class CompletedGoalModel(BaseModel):
    secret: str = Field(..., min_length=42, max_length=42)
    argon2: str = Field(..., max_length=42)


class ValidateModel(BaseModel):
    completed_goals: List[CompletedGoalModel] = Field(
        ..., max_items=SETTINGS.captcha.required_secrets
    )
