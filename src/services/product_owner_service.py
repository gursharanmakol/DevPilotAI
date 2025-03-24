from src.state.workflow_state import WorkflowState
import logging

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
    Handles feedback flow for user stories.

    Args:
        state: WorkflowState
        feedback: feedback string entered by product owner
        handle_feedback: function to process feedback

    Returns:
        Updated WorkflowState
    """
    feedback = feedback.strip() if isinstance(feedback, str) else ""
    if not feedback:
        raise ValueError("Feedback cannot be empty.")

    try:
        state.feedback = feedback
        logger.info(f"Submitting feedback: {feedback}")
        updated_state = handle_feedback(state)
        return updated_state
    except Exception as e:
        logger.exception("Feedback submission failed.")
        raise
