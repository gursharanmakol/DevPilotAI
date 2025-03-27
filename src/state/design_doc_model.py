from pydantic import BaseModel
from typing import Optional

class DesignDocumentModel(BaseModel):
    functional_doc: Optional[str] = None
    technical_doc: Optional[str] = None
    review_status: str = "Pending"  # Could be: "Pending", "Approved", "Feedback"
    feedback: Optional[str] = None  # Holds user feedback on design