from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.utils.decorators import log_node
from src.utils.user_story_parser import parse_user_stories_from_llm_response

logger = Logger(__name__)


@log_node
def get_user_stories(self, state: WorkflowState) -> WorkflowState:
    try:
        if not hasattr(state, "requirement") or not state.requirement:
            logger.error("State missing 'requirement'.")
            return state

        user_stories_response = get_user_stories(state.requirement)
        state.user_stories = parse_user_stories_from_llm_response(user_stories_response)
        state.user_story_status = "Pending Review"
        state.next_step = "review_user_stories"
        logger.info(f"Parsed {len(state.user_stories)} user stories.")
        logger.info(f"User stories generated for: {state.requirement[:60]}...")
        return state

    except Exception as e:
        logger.exception("Failed in get_user_stories node.")
        state.next_step = "end"
        return state