import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from src.state.workflow_state import WorkflowState
from src.ui.components import requirement_input, product_owner_review
from src.ui.handlers import handle_initial_workflow, handle_approval, handle_feedback
from src.tools.logger import Logger

logger = Logger("main")

try:
    if "workflow_state" not in st.session_state or st.session_state.workflow_state is None:
        st.session_state.workflow_state = WorkflowState(requirement="")
        logger.info("Initialized workflow state.")
    elif not isinstance(st.session_state.workflow_state, WorkflowState):
        st.session_state.workflow_state = WorkflowState(requirement="")

    state = st.session_state.workflow_state

    state = requirement_input(state, handle_initial_workflow)

    if state and state.user_stories:
        state = product_owner_review(state, handle_approval, handle_feedback)

except Exception as e:
    logger.exception("Unexpected error in main Streamlit app:")
    st.error("An unexpected error occurred.")
    st.exception(e)
