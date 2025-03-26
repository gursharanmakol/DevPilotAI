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
