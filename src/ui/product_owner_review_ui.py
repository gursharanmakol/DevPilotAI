import streamlit as st
from src.state.workflow_state import WorkflowState
from src.ui.components import render_section_heading, render_divider
from src.tools.logger import Logger
from src.services.product_owner_service import approve_user_stories, submit_feedback

logger = Logger("product_owner_review_ui")


def product_owner_review(state: WorkflowState, handle_approval, handle_feedback):
    if not state or not getattr(state, "user_stories", None):
        logger.warning("Skipping Product Owner Review: no user stories found.")
        return state

    with st.expander("Step 2: Product Owner Review", expanded=True):
        st.write("📦 Debug: Current State", state)
        if not isinstance(state, WorkflowState):
            logger.error("Invalid or missing workflow_state in session.")
            st.error("Workflow session state is invalid.")
            return None

        render_section_heading("Step 2: Product Owner Review")
        render_section_heading("Approve or Provide Feedback")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Approve User Stories"):
                try:
                    updated_state = approve_user_stories(st.session_state.workflow_state, handle_approval)
                    st.session_state.workflow_state = updated_state
                    st.success("✅ User stories approved!")
                    logger.info("[product_owner_review] Approval handled successfully.")
                except Exception as e:
                    st.error("Approval failed.")
                    st.exception(e)

        with col2:
            feedback = st.text_area("Enter Feedback", value=state.feedback or "", height=120, key="feedback_input")

            if st.button("✍️ Submit Feedback"):
                try:
                    updated_state = submit_feedback(state, feedback, handle_feedback)

                    if isinstance(updated_state, WorkflowState):
                        st.session_state.workflow_state = updated_state
                        st.session_state.workflow_state.feedback = ""
                        st.rerun()
                    else:
                        st.error("Workflow state update failed. Unexpected return type.")
                except Exception as e:
                    st.error("Feedback submission failed.")
                    st.exception(e)

        render_divider()
        logger.info(f"[product_owner_review] Final state: {state.__dict__}")
        return state
