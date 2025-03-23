import streamlit as st
from src.state.workflow_state import WorkflowState
from src.tools.logger import Logger

logger = Logger("components")

def requirement_input(state: WorkflowState, handle_initial_workflow):
    if not isinstance(state, WorkflowState):
        logger.error(f"Expected WorkflowState but got {type(state)}")
        st.error("Invalid workflow state detected.")
        return None

    if state is None:
        logger.error("State was None in requirement_input.")
        st.error("Workflow state is not initialized.")
        return None

    with st.expander("Requirement Gathering", expanded=True):
        st.write("📦 Debug: Current State", state)
       
        st.subheader("Step 1: Enter Software Requirement")
        col1, col2 = st.columns(2)

        with col1:
            requirement = st.text_area("Requirement", value=getattr(state, "requirement", ""), height=150)
            if st.button("Generate User Stories"):
                if requirement.strip():
                    try:
                        state.requirement = requirement.strip()
                        updated_state = handle_initial_workflow(state)
                        if updated_state:
                            st.session_state.workflow_state = updated_state
                            logger.info("User stories successfully generated.")
                            state = st.session_state.workflow_state
                    except Exception as e:
                        logger.exception("Failed to generate user stories.")
                        st.error("Failed to generate user stories.")
                        st.exception(e)
                        return None
                else:
                    st.warning("Please enter a valid requirement.")
                    return None

        with col2:
            st.subheader("Auto-Generated User Stories")
            st.info(state.user_stories)
            workflow_state = st.session_state.get("workflow_state")
            user_stories = getattr(workflow_state, "user_stories", None) if workflow_state else None

            if not user_stories:
                st.info("Enter a requirement and click 'Generate User Stories' to see output.")
            elif isinstance(user_stories, list):
                for idx, story in enumerate(user_stories):
                    st.markdown(f"**User Story {idx + 1}:** {story.get('user_story', '')}")
                    st.markdown("**Acceptance Criteria:**")
                    for criterion in story.get("acceptance_criteria", []):
                        st.markdown(f"- {criterion}")
            elif isinstance(user_stories, str):
                st.markdown(f"**User Story:** {user_stories}")
            else:
                st.warning("Unrecognized format for user stories.")

        st.session_state.workflow_state = state 
        st.divider()
        logger.info(f"[requirement_input] Final state: {state.__dict__}")
        return state


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

        st.subheader("Step 2: Product Owner Review")
        st.markdown("### Approve or Provide Feedback")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Approve User Stories"):
                try:
                    updated_state = handle_approval(st.session_state.workflow_state)
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
                    feedback_text = feedback.strip() if isinstance(feedback, str) else ""
                    if feedback_text:
                        state.feedback = feedback_text

                        logger.info(f"[feedback_button] Submitting feedback = {feedback_text}")
                        updated_state = handle_feedback(state)

                        # Confirm state is valid
                        logger.info(f"[feedback_button] Updated state user stories = {updated_state.get('user_stories')}")

                        if isinstance(updated_state, WorkflowState):
                            st.session_state.workflow_state = updated_state
                            st.session_state.workflow_state.feedback = ""
                            st.rerun()
                        else:
                            st.error("Workflow state update failed. Unexpected return type.")

                except Exception as e:
                    st.error("Feedback submission failed.")
                    st.exception(e)

        st.divider()
        logger.info(f"[product_owner_review] Final state: {state.__dict__}")
        return state