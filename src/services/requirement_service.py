from src.state.workflow_state import WorkflowState
from src.state.workflow_state import UserStoryModel
from pydantic import ValidationError

import logging
from typing import Callable 
import json

logger = logging.getLogger(__name__)


def generate_user_stories(requirement: str, handler_func: Callable[[WorkflowState], WorkflowState]) -> WorkflowState:
    """
    Handles the user story generation from a requirement in the workflow state.

    Args:
        requirement (str): The software requirement text to process.
        handler_func (function): Function to process the workflow and return updated state.

    Returns:
        WorkflowState: Updated state with user stories populated.
    """
    if not requirement:
        raise ValueError("Requirement is missing in state.")

    try:
        raw_response = handler_func(WorkflowState(requirement=requirement))
        if isinstance(raw_response, WorkflowState):
            return raw_response

        try:
   
            parsed = json.loads(raw_response)
            stories = parsed.get("user_stories", [])

            # Normalize: wrap in list if it's a single dict
            if isinstance(stories, dict):
                logger.debug("LLM returned a single user story; wrapping it in a list.")
                stories = [stories]

            validated = [UserStoryModel(**story).model_dump() for story in stories]
            return WorkflowState(requirement=requirement, user_stories=validated)

        except json.JSONDecodeError:
            logger.error("Invalid JSON format returned by LLM.")
            return WorkflowState(
                requirement=requirement,
                user_stories=[{
                    "user_story": raw_response,
                    "acceptance_criteria": []
                }]
            )

        except ValidationError as ve:
            logger.error(f"Pydantic validation failed - {ve}")
            logger.debug(f"Error - LLM raw response: {raw_response}")
            raise

    except Exception as e:
        logger.exception("Error generating user stories.")
        raise