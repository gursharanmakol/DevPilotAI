from pydantic import BaseModel, Field
from typing import Optional, List

class WorkflowState(BaseModel):
    requirement: Optional[str] = ""  # <-- Make it optional
    user_stories: Optional[str] = ""
    user_story_status: Optional[str] = "Pending"
    feedback: Optional[str] = ""
    feedback_history: List[str] = Field(default_factory=list)
    revisions: List[str] = Field(default_factory=list)
    review_attempts: int = 0
    next_step: Optional[str] = "review_user_stories"
