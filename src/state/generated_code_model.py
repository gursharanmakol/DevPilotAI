from pydantic import BaseModel, Field
from typing import Optional, Dict


class CodeGenerationModel(BaseModel):
    # generated_code is a dict of {filename: code_string}, 
    # allowing multi-file code in one structure.
    generated_code: Dict[str, str] = Field(default_factory=dict)
    code_review_status: str = "Pending"  # e.g. "Pending", "Approved", or "Needs Changes"
    code_feedback: Optional[str] = None  # user or reviewer feedback on the code