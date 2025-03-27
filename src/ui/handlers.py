from src.graph.workflow import Workflow
from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger

logger = Logger(__name__)

def handle_initial_workflow(state: WorkflowState) -> WorkflowState:
    try:
        requirement_str = getattr(state, "requirement", "")
        workflow = Workflow(requirement=requirement_str)
        result = workflow.run_initial_only()
        logger.info("Initial workflow run completed.")
        return result
    except Exception as e:
        logger.exception("Error during initial workflow execution.")
        raise

def handle_approval(state: WorkflowState) -> WorkflowState:
    try:
        state.user_story_status = "Approved"
        workflow = Workflow(requirement=(state.requirement or ""))
        workflow.state = state
        result = workflow.run_review_only()
        logger.info("User stories approved and workflow advanced.")
        return result
    except Exception as e:
        logger.exception("Error during approval.")
        raise


def handle_feedback(state: WorkflowState) -> WorkflowState:
    try:
        workflow = Workflow(requirement=(state.requirement or ""))
        workflow.state = state
        result = workflow.run_review_only(feedback=state.feedback)

        result.next_step = "end"

        # 👇 FIX: ensure the result is a proper WorkflowState object
        if not isinstance(result, WorkflowState):
            result = WorkflowState(**result)

        logger.info(f"[handle_feedback] Revised user stories: {getattr(result, 'user_stories', None)}")
        return result

    except Exception as e:
        logger.exception("Error during feedback processing.")
        raise


def handle_create_design_doc(state: WorkflowState) -> WorkflowState:
    """
    Creates or updates the design document with placeholders or
    content from an LLM, then marks review_status as Pending.
    """
    # Example placeholders (replace with actual AI-generated text if desired)
    state.design_doc.functional_doc = (
        "Placeholder functional requirements describing system behavior..."
    )
    state.design_doc.technical_doc = (
        "Placeholder technical architecture details (data models, APIs, etc.)..."
    )

    # Reset to 'Pending' if it's a brand-new doc or a refresh
    state.design_doc.review_status = "Pending"
    state.design_doc.feedback = None  # Clear any old feedback
    return state


def handle_design_approval(state: WorkflowState) -> WorkflowState:
    """
    Approve the design document, resetting feedback if any.
    """
    state.design_doc.review_status = "Approved"
    state.design_doc.feedback = None
    return state


def handle_design_feedback(state: WorkflowState, feedback: str) -> WorkflowState:
    """
    Mark the design document as needing changes/feedback.
    """
    state.design_doc.review_status = "Feedback"
    state.design_doc.feedback = feedback
    return state


def handle_generate_code(state: WorkflowState) -> WorkflowState:
    """
    Generates multi-file code if design doc is approved.
    Otherwise, does nothing or returns state unchanged.
    """
    if state.design_doc.review_status != "Approved":
        # Optionally raise an exception or log a warning
        return state

    # Example placeholders for multi-file code:
    state.code_generation.generated_code = {
        "main.py": "def main():\n    print('Hello from main')\n",
        "utils.py": "def helper():\n    return 'Helper result'\n"
    }
    state.code_generation.code_review_status = "Pending"
    state.code_generation.code_feedback = None
    return state


def handle_code_approval(state: WorkflowState) -> WorkflowState:
    """
    Approve the generated code, resetting feedback if any.
    """
    state.code_generation.code_review_status = "Approved"
    state.code_generation.code_feedback = None
    return state


def handle_code_feedback(state: WorkflowState, feedback: str) -> WorkflowState:
    """
    Mark the generated code as needing changes/feedback.
    """
    state.code_generation.code_review_status = "Needs Changes"
    state.code_generation.code_feedback = feedback
    return state
