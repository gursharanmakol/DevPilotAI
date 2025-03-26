# src/ui/requirement_input_ui.py

import streamlit as st

from src.state.workflow_state import WorkflowState
from src.ui.components import render_section_heading, render_divider, render_labeled_text
from src.utils.logger import Logger
from src.handlers.requirement_service import handle_user_story_generation
from src.components.user_story_renderer import render_user_stories

logger = Logger(__name__)

def requirement_input(state: WorkflowState, handle_initial_workflow) -> WorkflowState | None:
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


def validate_state(state: WorkflowState | None) -> bool:
    if not isinstance(state, WorkflowState):
        logger.error(f"Expected WorkflowState but got {type(state)}")
        st.error("Invalid workflow state detected.")
        return False
    if state is None:
        logger.error("State was None in requirement_input.")
        st.error("Workflow state is not initialized.")
        return False
    return True


def render_requirement_input_area(container, state: WorkflowState, handle_initial_workflow) -> None:
    with container:
        requirement = st.text_area("Requirement", value=state.requirement or "", height=150)
        if st.button("Generate User Stories", key="generate_button"):
            if requirement.strip():
                try:
                    state.requirement = requirement.strip()
                    with st.spinner("Generating user stories..."):
                        updated_state = handle_user_story_generation(state, handle_initial_workflow)

                    state.user_stories = updated_state.user_stories
                    logger.info("User stories successfully generated.")
                except Exception as e:
                    logger.exception("Failed to generate user stories.")
                    st.error("Failed to generate user stories.")
                    st.exception(e)
            else:
                st.warning("Please enter a valid requirement.")


def render_user_stories_column(container, state: WorkflowState) -> None:
    with container:
        render_section_heading("Auto-Generated User Stories")
        user_stories = getattr(state, "user_stories", None)

        if not user_stories:
            st.info("Enter a requirement and click 'Generate User Stories' to see output.")
        
        else:
            render_user_stories(user_stories)
