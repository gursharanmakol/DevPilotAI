
from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.utils.decorators import log_node
from src.prompts.design_doc_prompt import generate_design_doc_prompt
from src.utils.design_doc_parser import parse_design_doc_response

logger = Logger(__name__)

@log_node
def review_design_doc(self, state: WorkflowState) -> WorkflowState:
    try:
        logger.info("Reviewing design document...")

        if state.design_doc.review_status == "Approved":
            logger.info("Design doc approved.")
            state.next_step = "generate_code"

        elif state.design_doc.feedback:
            logger.info("Feedback received. Regenerating design doc...")
            prompt = generate_design_doc_prompt(
                state.requirement or "",
                "\n".join([s.user_story for s in state.user_stories or []])
            )
            raw = self.ai_service._call_openai_chat(prompt, context="revise design doc")
            parsed = parse_design_doc_response(raw)

            state.design_doc.functional_doc = parsed.get("functional_doc", "")
            state.design_doc.technical_doc = parsed.get("technical_doc", "")
            state.design_doc.feedback = ""
            state.design_doc.review_status = "Pending"
            state.next_step = "review_design_doc"

        else:
            state.next_step = "review_design_doc"  # Waiting for review or feedback

        return state

    except Exception as e:
        logger.exception("Design doc review failed.")
        state.next_step = "end"
        return state