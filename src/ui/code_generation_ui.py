import streamlit as st
from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.ui.components import render_section_heading, render_divider

logger = Logger(__name__)

def code_generation_ui(state: WorkflowState, handle_generate_code, 
                       handle_code_approval, handle_code_feedback) -> WorkflowState | None:
    if not validate_state(state):
        return None

    with st.expander("Step 4: Code Generation", expanded=True):
        render_section_heading("Step 4: Code Generation")

        col1, col2 = st.columns(2)

        # Left column: maybe show code generation button or code files
        render_code_gen_area(
            container=col1,
            state=state,
            handle_generate_code=handle_generate_code
        )

        # Right column: code approval or feedback
        render_code_review_area(
            container=col2,
            state=state,
            handle_code_approval=handle_code_approval,
            handle_code_feedback=handle_code_feedback
        )

        st.session_state.workflow_state = state
        render_divider()
        logger.info(f"[code_generation_ui] Final state: {state.__dict__}")

    return state


def validate_state(state: WorkflowState | None) -> bool:
    if not isinstance(state, WorkflowState):
        logger.error(f"Expected WorkflowState but got {type(state)}")
        st.error("Invalid workflow state detected.")
        return False
    if state is None:
        logger.error("State was None in code_generation_ui.")
        st.error("Workflow state is not initialized.")
        return False
    return True


def render_code_gen_area(container, state: WorkflowState, handle_generate_code) -> None:
    with container:
        st.subheader("Generate Code")
        # If design not approved, warn
        if state.design_doc.review_status != "Approved":
            st.warning("Design must be approved before generating code.")
        else:
            # If no code, show 'Generate Code' button
            if not state.code_generation.generated_code:
                st.info("No code generated yet.")
                if st.button("Generate Code"):
                    state = handle_generate_code(state)
                    st.success("Code generation complete.")
            else:
                # Display code files
                st.subheader("Generated Code Files")
                for filename, code_content in state.code_generation.generated_code.items():
                    st.markdown(f"**{filename}**")
                    st.code(code_content, language="python")


def render_code_review_area(container, state: WorkflowState, handle_code_approval, handle_code_feedback) -> None:
    with container:
        st.subheader("Code Review")

        st.markdown(f"**Code Review Status:** {state.code_generation.code_review_status}")
        code_feedback_text = st.text_area("Enter Code Feedback", "", height=80)

        approve_btn, feedback_btn = st.columns(2)
        with approve_btn:
            if st.button("Approve Code"):
                state = handle_code_approval(state)
                st.success("Code approved.")
        with feedback_btn:
            if st.button("Submit Code Feedback"):
                if not code_feedback_text.strip():
                    st.warning("Please enter feedback before submitting.")
                else:
                    state = handle_code_feedback(state, code_feedback_text.strip())
                    st.info("Feedback submitted. Code status updated.")
