from src.state.workflow_state import WorkflowState
from src.state.workflow_state import UserStoryModel
from src.utils.user_story_parser import parse_user_stories_from_llm_response

from pydantic import ValidationError

import logging
from typing import Callable 
import json

logger = logging.getLogger(__name__)


def handle_user_story_generation(state: WorkflowState, handler_func: Callable[[WorkflowState], WorkflowState]) -> WorkflowState:
    """
    Handles the user story generation from a requirement in the workflow state.

    Args:
        requirement (str): The software requirement text to process.
        handler_func (function): Function to process the workflow and return updated state.

    Returns:
        WorkflowState: Updated state with user stories populated.
    """
    if not state.requirement:
        raise ValueError("Requirement is missing in state.")

    try:
        raw_response = handler_func(WorkflowState(requirement=state.requirement))
        if isinstance(raw_response, WorkflowState):
            return raw_response

        validated = parse_user_stories_from_llm_response(raw_response)
        return WorkflowState(requirement=state.requirement, user_stories=validated)

    except Exception as e:
        logger.exception("Error generating user stories", exc_info=True)
        raise