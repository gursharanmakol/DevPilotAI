import logging
from typing import Callable

from src.state.workflow_state import WorkflowState
from src.utils.design_doc_parser import parse_design_doc_response

logger = logging.getLogger(__name__)

def handle_design_doc_generation(state: WorkflowState, llm_handler: Callable[[str, str], str]) -> WorkflowState:
    """
    Calls LLM to generate design documentation based on requirement and user stories.

    Args:
        state: WorkflowState containing requirement and user stories
        llm_handler: function to send prompt and return raw LLM response (as string)

    Returns:
        Updated WorkflowState with functional and technical doc filled
    """
    if not state.requirement or not state.user_stories:
        raise ValueError("Requirement or user stories missing in state.")

    try:
        user_story_text = "\n".join([s.user_story for s in state.user_stories])
        raw_response = llm_handler(state.requirement, user_story_text)

        parsed = parse_design_doc_response(raw_response)

        state.design_doc.functional_doc = parsed.get("functional_doc", "")
        state.design_doc.technical_doc = parsed.get("technical_doc", "")
        state.design_doc.review_status = "Pending"
        return state

    except Exception as e:
        logger.exception("Failed to generate design document.")
        raise
