from pydantic import BaseModel, Field
from datetime import datetime


class WorkoutDTO(BaseModel):
    id: int
    workout_datetime: datetime
    title: str
    workout_type: str


class UserWorkoutsDTO(BaseModel):
    user_id: int
    from_datetime: datetime
    workouts: list[WorkoutDTO] = Field(default_factory=list)
