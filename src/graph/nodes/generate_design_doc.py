
from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.utils.decorators import log_node
from src.prompts.design_doc_prompt import generate_design_doc_prompt
from src.utils.design_doc_parser import parse_design_doc_response

logger = Logger(__name__)

@log_node
def generate_design_doc(self, state: WorkflowState) -> WorkflowState:
    try:
        logger.info("Generating design document...")

        if not state.user_stories:
            logger.warning("No user stories found, skipping design doc.")
            state.next_step = "end"
            return state

        user_story_text = "\n".join([s.user_story for s in state.user_stories])
        prompt = generate_design_doc_prompt((state.requirement or ""), user_story_text)
        raw = self.ai_service._call_openai_chat(prompt, context="generate design doc")

        parsed = parse_design_doc_response(raw)
        state.design_doc.functional_doc = parsed.get("functional_doc", "")
        state.design_doc.technical_doc = parsed.get("technical_doc", "")
        state.design_doc.review_status = "Pending"
        state.next_step = "generate_code"
        return state

    except Exception as e:
        logger.exception("Design doc generation failed.")
        state.next_step = "end"
        return state