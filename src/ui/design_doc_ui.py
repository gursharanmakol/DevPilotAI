import streamlit as st
from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.ui.components import render_section_heading, render_divider

logger = Logger(__name__)

def design_doc_ui(state: WorkflowState, handle_create_design_doc, 
                     handle_design_approval, handle_design_feedback) -> WorkflowState | None:
    """
    Main entry point for Step 3: Design Document UI.

    1) Validates the state.
    2) Creates an expander with a heading.
    3) Uses sub-functions to render the doc creation area and doc review area.
    4) Updates session state and returns it.
    """
    if not validate_state(state):
        return None

    with st.expander("Step 3: Design Document", expanded=True):
        render_section_heading("Step 3: Design Document")

        # We'll split the layout into two columns, for example,
        # one for "Create/Show Docs" and the other for "Approval/Feedback".
        col1, col2 = st.columns(2)
        
        render_design_doc_area(
            container=col1,
            state=state,
            handle_create_design_doc=handle_create_design_doc
        )
        
        render_design_review_area(
            container=col2,
            state=state,
            handle_design_approval=handle_design_approval,
            handle_design_feedback=handle_design_feedback
        )

        # Update session state
        st.session_state.workflow_state = state
        render_divider()
        logger.info(f"[design_doc_ui] Final state: {state.__dict__}")

    return state


def validate_state(state: WorkflowState | None) -> bool:
    """
    Follows the same pattern as requirement_input_ui.py: checks that
    'state' is a valid WorkflowState before proceeding.
    """
    if not isinstance(state, WorkflowState):
        logger.error(f"Expected WorkflowState but got {type(state)}")
        st.error("Invalid workflow state detected.")
        return False
    if state is None:
        logger.error("State was None in design_doc_ui.")
        st.error("Workflow state is not initialized.")
        return False
    return True


def render_design_doc_area(container, state: WorkflowState, handle_create_design_doc) -> None:
    """
    Handles showing or creating the design doc. If the doc doesn't exist,
    we display a 'Create' button. If it exists, we display functional & technical text areas.
    """
    with container:
        # If no docs yet, show a 'Create' button:
        if not state.design_doc.functional_doc and not state.design_doc.technical_doc:
            st.info("No design document created yet.")
            if st.button("Create Design Document"):
                state = handle_create_design_doc(state)
                st.success("Design document created.")
        else:
            # If docs already exist, show them in disabled text areas
            st.subheader("Functional Document")
            st.text_area(
                "Functional Doc Content",
                value=state.design_doc.functional_doc or "",
                disabled=True,
                height=150
            )

            st.subheader("Technical Document")
            st.text_area(
                "Technical Doc Content",
                value=state.design_doc.technical_doc or "",
                disabled=True,
                height=150
            )


def render_design_review_area(container, state: WorkflowState, handle_design_approval, handle_design_feedback) -> None:
    """
    Handles the 'Review' side, including approval or feedback.
    """
    with container:
        st.subheader("Design Review")

        st.markdown(f"**Current Review Status:** {state.design_doc.review_status}")

        user_feedback = st.text_area("Enter Design Feedback", "", height=80)

        approve_btn, feedback_btn = st.columns(2)
        with approve_btn:
            if st.button("Approve Design"):
                state = handle_design_approval(state)
                st.success("Design approved.")
        with feedback_btn:
            if st.button("Submit Design Feedback"):
                if not user_feedback.strip():
                    st.warning("Please enter feedback before submitting.")
                else:
                    state = handle_design_feedback(state, user_feedback.strip())
                    st.info("Feedback submitted. Status set to 'Feedback'.")
