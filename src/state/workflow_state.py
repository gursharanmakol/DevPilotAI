from pydantic import BaseModel, Field
from typing import Optional, List
from src.state.user_story_model import UserStoryModel

class WorkflowState(BaseModel):
    requirement: Optional[str] = ""  # <-- Make it optional
    user_stories: Optional[List[UserStoryModel]] = Field(default_factory=list)
    user_story_status: Optional[str] = "Pending"
    feedback: Optional[str] = ""
    feedback_history: List[str] = Field(default_factory=list)
    revisions: List[List[UserStoryModel]] = Field(default_factory=list)
    review_attempts: int = 0
    next_step: Optional[str] = "review_user_stories"

