"""
schemas.py
Pydantic models used to validate incoming requests.
"""

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str
    user_id: int
    age: int
    weight: float
    goal: str
    intensity: str = Field(pattern="^(low|medium|high)$")


class WorkoutRequest(BaseModel):
    goal: str
    intensity: str


class FeedbackRequest(BaseModel):
    feedback: str
