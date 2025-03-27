from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.utils.decorators import log_node
from src.prompts.code_generation_prompt import generate_code_generation_prompt
from src.utils.code_parser import parse_generated_code_response

logger = Logger(__name__)

@log_node
def review_code(self, state: WorkflowState) -> WorkflowState:
    try:
        logger.info("Reviewing generated code...")

        if state.code_generation.code_review_status == "Approved":
            logger.info("Code generation approved.")
            state.next_step = "end"

        elif state.code_generation.code_feedback:
            logger.info("Feedback received. Regenerating code...")
            combined_doc = f"{state.design_doc.functional_doc}\n\n{state.design_doc.technical_doc}"
            prompt = generate_code_generation_prompt(combined_doc)
            raw = self.ai_service._call_openai_chat(prompt, context="regenerate code")
            files = parse_generated_code_response(raw)

            state.code_generation.generated_code = files
            state.code_generation.code_review_status = "Pending"
            state.code_generation.code_feedback = ""
            state.next_step = "review_code"

        else:
            state.next_step = "review_code"  # Waiting for input

        return state

    except Exception as e:
        logger.exception("Code review failed.")
        state.next_step = "end"
        return state