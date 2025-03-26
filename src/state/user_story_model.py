from pydantic import BaseModel, Field
from typing import Optional, List

class UserStoryModel(BaseModel):
    user_story: str
    acceptance_criteria: List[str]