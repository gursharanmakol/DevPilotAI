import logging
import json
import re

from src.state.workflow_state import WorkflowState
from src.state.workflow_state import UserStoryModel
from src.utils.user_story_parser import parse_user_stories_from_llm_response

from pydantic import ValidationError

logger = logging.getLogger(__name__)

def approve_user_stories(state: WorkflowState, handle_approval) -> WorkflowState:
    """
    Handles approval flow for user stories.

    Args:
        state: WorkflowState
        handle_approval: function to process approval step

    Returns:
        Updated WorkflowState
    """
    try:
        updated_state = handle_approval(state)
        logger.info("User stories approved successfully.")
        return updated_state
    except Exception as e:
        logger.exception("Approval failed.")
        raise


def submit_feedback(state: WorkflowState, feedback: str, handle_feedback) -> WorkflowState:
    """
    Handles feedback flow for user stories while preserving structured data.
    """
    feedback = feedback.strip() if isinstance(feedback, str) else ""
    if not feedback:
        raise ValueError("Feedback cannot be empty.")

    try:
        state.feedback = feedback
        logger.info(f"Submitting feedback: {feedback}")
        raw_response = handle_feedback(state)

        if isinstance(raw_response, WorkflowState):
                return raw_response

        validated = parse_user_stories_from_llm_response(raw_response)
        return WorkflowState(requirement=state.requirement, user_stories=validated)

    except Exception as e:
        logger.exception("Error generating user stories", exc_info=True)
        raise


def parse_user_story_markdown(text: str):
    """
    Converts markdown output from LLM into structured user stories.
    Handles both 'User Story' and 'Acceptance Criteria'.
    """
    if not isinstance(text, str):
        return []

    # Match user story section
    user_story_match = re.search(r"\*\*User Story:.*?\*\*\s*(.+?)(?=\*\*Acceptance Criteria:|\Z)", text, re.DOTALL)
    user_story = user_story_match.group(1).strip() if user_story_match else ""

    # Match acceptance criteria block
    criteria_match = re.search(r"\*\*Acceptance Criteria:.*?\*\*(.+)", text, re.DOTALL)
    criteria_block = criteria_match.group(1).strip() if criteria_match else ""

    # Extract numbered (1., 2., etc.) or bullet (*) points
    acceptance_criteria = re.findall(r"(?:\n|^)(?:\d+\.|\*)\s+(.*)", criteria_block)

    return [{
        "user_story": user_story,
        "acceptance_criteria": [c.strip() for c in acceptance_criteria]
    }]



def parse_user_story_with_criteria(response: str):
    """
    Parses OpenAI response into structured user story + acceptance criteria list.
    """
    user_story_part, _, rest = response.partition("**Acceptance Criteria:**")
    criteria_matches = re.findall(r"\d+\.\s+(.*)", rest.strip())

    return {
        "user_story": user_story_part.strip(),
        "acceptance_criteria": criteria_matches
    }