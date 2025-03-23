# src/graph/workflow.py

from langgraph.graph import StateGraph, END
from src.state.workflow_state import WorkflowState
from src.llms.openai_helper import OpenAIService
from src.tools.logger import Logger
from src.tools.decorators import log_node
from src.graph.user_story import get_user_stories

logger = Logger("workflow")


class Workflow:
    def __init__(self, requirement: str):
        self.state = WorkflowState(requirement=requirement)
        self.ai_service = OpenAIService()

    @log_node
    def get_user_stories(self, state: WorkflowState) -> WorkflowState:
        try:
            if not hasattr(state, "requirement") or not state.requirement:
                logger.error("State missing 'requirement'.")
                return state

            user_stories = get_user_stories(state.requirement)
            state.user_stories = user_stories
            state.user_story_status = "Pending Review"
            state.next_step = "review_user_stories"
            logger.info(f"User stories generated for: {state.requirement[:60]}...")
            return state

        except Exception as e:
            logger.exception("Failed in get_user_stories node.")
            state.next_step = "end"
            return state

    @log_node
    def review_user_stories(self, state: WorkflowState) -> WorkflowState:
        try:
            logger.info("Reviewing user stories...")

            if state.user_story_status == "Approved":
                logger.info("User stories approved. Workflow complete.")
                state.next_step = "end"

            elif state.feedback:
                logger.info("Feedback received. Regenerating user stories...")
                state.feedback_history.append(state.feedback)
                state.revisions.append(state.user_stories)

                revised = self.ai_service.revise_user_stories(
                    feedback= state.feedback,
                    requirement= state.requirement,
                )
                state.user_stories = revised
                state.feedback = ""

                logger.info(f"[review_user_stories] Setting state.user_stories = {revised}")

                # Exit the loop if no more feedback expected
                if not revised or not revised.strip():
                    logger.warning("No revised user stories received. Ending workflow.")
                    state.next_step = "end"
                else:
                    state.next_step = "review_user_stories"
            else:
                state.review_attempts += 1
                if state.review_attempts >= 2:
                    logger.warning("Max feedback attempts exceeded. Ending workflow.")
                    state.next_step = "end"
                else:
                    logger.info("Waiting for feedback...")
                    state.next_step = "review_user_stories"

            return state

        except Exception as e:
            logger.exception("Error in review_user_stories node.")
            state.next_step = "end"
            return state

    def build_workflow(self) -> StateGraph:
        builder = StateGraph(WorkflowState)
        builder.add_node("get_user_stories", self.get_user_stories)
        builder.add_node("review_user_stories", self.review_user_stories)

        builder.set_entry_point("get_user_stories")
        builder.add_edge("get_user_stories", "review_user_stories")
        builder.add_conditional_edges(
            "review_user_stories",
            lambda state: state.next_step,
            {
                "review_user_stories": "review_user_stories",
                "end": END,
            },
        )
        return builder.compile()

    def run_workflow(self) -> WorkflowState:
        try:
            graph = self.build_workflow()
            final_state = graph.invoke(self.state)
            return final_state
        except Exception as e:
            logger.exception("Error running full workflow.")
            return self.state

    def run_initial_only(self) -> WorkflowState:
        try:
            return self.get_user_stories(self.state)
        except Exception as e:
            logger.exception("Error running initial step.")
            return self.state


    def run_review_only(self, feedback: str = "") -> WorkflowState:
        try:
            if feedback:
                trimmed_feedback = feedback.strip()
                logger.info(f"run_review_only: Received feedback = {trimmed_feedback}")
                self.state.feedback = trimmed_feedback
                self.state.feedback_history.append(trimmed_feedback)
                self.state.revisions.append(self.state.user_stories)
                self.state.user_story_status = "Pending"
                self.state.requirement = f"{self.state.requirement.strip()}. {trimmed_feedback}"
                logger.info(f"run_review_only: Updated requirement = {self.state.requirement}")

            builder = StateGraph(WorkflowState)
            builder.add_node("review_user_stories", self.review_user_stories)

            builder.set_entry_point("review_user_stories")
            builder.add_conditional_edges(
                "review_user_stories",
                lambda state: state.next_step,
                {
                    "review_user_stories": "review_user_stories",
                    "end": END,
                },
            )

            graph = builder.compile()
            logger.info(f"run_review_only: Invoking review_user_stories with state = {self.state}")
            result_state = graph.invoke(self.state)
            logger.info(f"run_review_only: Final state after review = {dict(result_state)}")
            return result_state
        except Exception as e:
            logger.exception(f"Error in run_review_only workflow: {e}")
            raise
