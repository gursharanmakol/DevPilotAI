import streamlit as st
from src.state.workflow_state import WorkflowState
from src.ui.components import render_section_heading, render_divider, render_labeled_text
from src.tools.logger import Logger
from src.services.requirement_service import generate_user_stories

logger = Logger("requirement_input_ui")


def requirement_input(state: WorkflowState, handle_initial_workflow):
    if not validate_state(state):
        return None

    with st.expander("Requirement Gathering", expanded=True):
        render_section_heading("Step 1: Enter Software Requirement")

        col1, col2 = st.columns(2)
        render_requirement_input_area(col1, state, handle_initial_workflow)
        render_user_stories_column(col2, state)

        st.session_state.workflow_state = state
        render_divider()
        logger.info(f"[requirement_input] Final state: {state.__dict__}")
        return state


def validate_state(state):
    if not isinstance(state, WorkflowState):
        logger.error(f"Expected WorkflowState but got {type(state)}")
        st.error("Invalid workflow state detected.")
        return False
    if state is None:
        logger.error("State was None in requirement_input.")
        st.error("Workflow state is not initialized.")
        return False
    return True


def render_requirement_input_area(container, state, handle_initial_workflow):
    with container:
        requirement = st.text_area("Requirement", value=getattr(state, "requirement", ""), height=150)
        if st.button("Generate User Stories"):
            if requirement.strip():
                try:
                    state.requirement = requirement.strip()
                    updated_state = generate_user_stories(state, handle_initial_workflow)
                    if isinstance(updated_state, str):  # OpenAI returns plain text
                        structured = [{"user_story": updated_state.strip(), "acceptance_criteria": []}]
                        state.user_stories = structured
                        updated_state.user_stories = structured  # Update the updated state as well
                    else:
                        state.user_stories = updated_state.user_stories
                    logger.info("User stories successfully generated.")
                except Exception as e:
                    logger.exception("Failed to generate user stories.")
                    st.error("Failed to generate user stories.")
                    st.exception(e)
            else:
                st.warning("Please enter a valid requirement.")


def render_user_stories_column(container, state):

    with container:
        render_section_heading("Auto-Generated User Stories")
        workflow_state = st.session_state.get("workflow_state")
        user_stories = getattr(workflow_state, "user_stories", None) if workflow_state else None

        if not user_stories:
            st.info("Enter a requirement and click 'Generate User Stories' to see output.")
        elif isinstance(user_stories, list):
            for idx, story in enumerate(user_stories):
                render_labeled_text(f"User Story {idx + 1}", story.get("user_story", ""))
                st.markdown("**Acceptance Criteria:**")
                for criterion in story.get("acceptance_criteria", []):
                    st.markdown(f"- {criterion}")
        elif isinstance(user_stories, str):
            render_labeled_text("User Story", user_stories)
        else:
            st.warning("Unrecognized format for user stories.")
