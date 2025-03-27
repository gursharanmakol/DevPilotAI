import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st

from src.state.workflow_state import WorkflowState
from src.ui.requirement_input_ui import requirement_input
from src.ui.handlers import handle_initial_workflow, handle_approval, handle_feedback
from src.ui.product_owner_review_ui import product_owner_review
from src.ui.design_doc_ui import design_doc_ui
from src.ui.handlers import handle_create_design_doc, handle_design_approval, handle_design_feedback
from src.ui.handlers import handle_generate_code, handle_code_approval, handle_code_feedback
from src.ui.code_generation_ui import code_generation_ui
from src.utils.logger import Logger

logger = Logger("app")

try:
    if "workflow_state" not in st.session_state or st.session_state.workflow_state is None:
        st.session_state.workflow_state = WorkflowState(requirement="")
        logger.info("Initialized workflow state.")
    elif not isinstance(st.session_state.workflow_state, WorkflowState):
        st.session_state.workflow_state = WorkflowState(requirement="")

    state = st.session_state.workflow_state

    state = requirement_input(state, handle_initial_workflow)

    if hasattr(state, "user_stories") and state.user_stories:
        state = product_owner_review(state, handle_approval, handle_feedback)
    else:
        logger.warning("Skipping Product Owner Review: no user stories found.")
    
    state = design_doc_ui(state, handle_create_design_doc, handle_design_approval, handle_design_feedback)

    state = code_generation_ui(state, handle_generate_code, handle_code_approval, handle_code_feedback)

except Exception as e:
    logger.exception("Unexpected error in main Streamlit app:")
    st.error("An unexpected error occurred.")
    st.exception(e)
