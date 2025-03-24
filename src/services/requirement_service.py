from src.state.workflow_state import WorkflowState
import logging

logger = logging.getLogger(__name__)


def generate_user_stories(state: WorkflowState, handler_func) -> WorkflowState:
    """
    Handles the user story generation from a requirement in the workflow state.

    Args:
        state (WorkflowState): The current state containing the requirement.
        handler_func (function): Function to process the workflow and return updated state.

    Returns:
        WorkflowState: Updated state with user stories populated.
    """
    if not state.requirement:
        raise ValueError("Requirement is missing in state.")

    try:
        logger.info("Generating user stories from requirement...")
        updated_state = handler_func(state)
        if updated_state:
            return updated_state
        else:
            logger.warning("Handler returned no updated state.")
            return state
    except Exception as e:
        logger.exception("Error generating user stories.")
        raise
