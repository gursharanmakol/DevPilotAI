from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.utils.decorators import log_node
from src.prompts.code_generation_prompt import generate_code_generation_prompt
from src.utils.code_parser import parse_generated_code_response

logger = Logger(__name__)

@log_node
def generate_code_files(self, state: WorkflowState) -> WorkflowState:
    try:
        logger.info("Generating code from design doc...")

        if state.design_doc.review_status != "Approved":
            logger.warning("Design doc not approved.")
            state.next_step = "end"
            return state

        combined_doc = f"{state.design_doc.functional_doc}\n\n{state.design_doc.technical_doc}"
        prompt = generate_code_generation_prompt(combined_doc)
        raw = self.ai_service._call_openai_chat(prompt, context="generate code")

        files = parse_generated_code_response(raw)
        state.code_generation.generated_code = files
        state.code_generation.code_review_status = "Pending"
        state.next_step = "end"
        return state

    except Exception as e:
        logger.exception("Code generation failed.")
        state.next_step = "end"
        return state