import logging
from typing import Callable

from src.state.workflow_state import WorkflowState
from src.utils.code_parser import parse_generated_code_response

logger = logging.getLogger(__name__)

def handle_code_generation(state: WorkflowState, llm_handler: Callable[[str], str]) -> WorkflowState:
    """
    Generates code based on the approved design document.

    Args:
        state: WorkflowState with functional + technical doc
        llm_handler: function to call OpenAI with design doc and return raw response

    Returns:
        Updated WorkflowState with code in the generated_code field
    """
    if state.design_doc.review_status != "Approved":
        raise ValueError("Design document must be approved before code generation.")

    try:
        full_design_doc = f"{state.design_doc.functional_doc}\n\n{state.design_doc.technical_doc}"
        raw_response = llm_handler(full_design_doc)

        files = parse_generated_code_response(raw_response)
        state.code_generation.generated_code = files
        state.code_generation.code_review_status = "Pending"
        return state

    except Exception as e:
        logger.exception("Failed to generate code from design doc.")
        raise
