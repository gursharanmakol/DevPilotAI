from src.graph.workflow import Workflow
from src.state.workflow_state import WorkflowState
from src.tools.logger import Logger

logger = Logger("handlers")

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
        workflow = Workflow(requirement=state.requirement)
        workflow.state = state
        result = workflow.run_review_only()
        logger.info("User stories approved and workflow advanced.")
        return result
    except Exception as e:
        logger.exception("Error during approval.")
        raise

def handle_feedback(state: WorkflowState) -> WorkflowState:
    try:
        workflow = Workflow(requirement=state.requirement)
        workflow.state = state
        result = workflow.run_review_only(feedback=state.feedback)
        result.next_step = "end"
        logger.info(f"[handle_feedback] Revised user stories: {result['user_stories']}")
        return result
    except Exception as e:
        logger.exception("Error during feedback processing.")
        raise
