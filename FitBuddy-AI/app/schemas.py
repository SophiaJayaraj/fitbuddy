from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class FitnessGoal(str, Enum):

    weight_loss = "weight loss"
    muscle_gain = "muscle gain"
    general_wellness = "general wellness"
    flexibility = "flexibility"


class Intensity(str, Enum):

    low = "low"
    medium = "medium"
    high = "high"


class UserInput(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=80
    )

    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight_kg: float = Field(
        gt=20,
        le=300
    )

    goal: FitnessGoal

    intensity: Intensity

    @field_validator(
        "name",
        "user_id"
    )
    @classmethod
    def clean_text(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    feedback: str = Field(
        min_length=3,
        max_length=1200
    )

    @field_validator(
        "user_id",
        "feedback"
    )
    @classmethod
    def clean_text(cls, value: str):

        return value.strip()


class PlanResponse(BaseModel):

    user_id: str
    name: str
    goal: str
    intensity: str

    workout_plan: str

    nutrition_tip: str

    updated_plan: str | None = None


class MessageResponse(BaseModel):

    message: str