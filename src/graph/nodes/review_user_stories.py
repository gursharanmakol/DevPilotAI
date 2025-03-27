from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.utils.decorators import log_node
from src.utils.user_story_parser import parse_user_stories_from_llm_response

logger = Logger(__name__)

@log_node
def review_user_stories(self, state: WorkflowState) -> WorkflowState:
    try:
        logger.info("Reviewing user stories...")

        if state.user_story_status == "Approved":
            logger.info("User stories approved. Workflow complete.")
            state.next_step = "end"

        elif state.feedback:
            logger.info("Feedback received. Regenerating user stories...")
            state.feedback_history.append(state.feedback)
            if state.user_stories is not None:
                state.revisions.append(state.user_stories)

            revised_response = self.ai_service.revise_user_stories(
                feedback=state.feedback,
                requirement=state.requirement or "",
            )
            state.user_stories = parse_user_stories_from_llm_response(revised_response)
            state.feedback = ""

            logger.info(f"[review_user_stories] Updated user stories: {revised_response}")

            state.next_step = "review_user_stories" if state.user_stories else "end"
        else:
            state.review_attempts += 1
            if state.review_attempts >= 2:
                logger.warning("Max feedback attempts exceeded. Ending workflow.")
                state.next_step = "end"
            else:
                logger.info("Waiting for feedback...")
                state.next_step = "review_user_stories"

        return state

    except Exception as e:
        logger.exception("Error in review_user_stories node.")
        state.next_step = "end"
        return state