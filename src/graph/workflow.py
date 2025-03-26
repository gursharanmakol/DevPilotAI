# src/graph/workflow.py

from typing import Any, Optional

from langgraph.graph import StateGraph, END # type: ignore

from src.llms.openai_helper import OpenAIService
from src.state.workflow_state import WorkflowState
from src.utils.logger import Logger
from src.utils.decorators import log_node
from src.utils.user_story_parser import parse_user_stories_from_llm_response
from src.graph.user_story import get_user_stories

logger = Logger(__name__)

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

            user_stories_response = get_user_stories(state.requirement)
            state.user_stories = parse_user_stories_from_llm_response(user_stories_response)
            state.user_story_status = "Pending Review"
            state.next_step = "review_user_stories"
            logger.info(f"Parsed {len(state.user_stories)} user stories.")
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
                if state.user_stories is not None:
                    state.revisions.append(state.user_stories)

                revised_response = self.ai_service.revise_user_stories(
                    feedback=state.feedback,
                    requirement=state.requirement or "",
                )
                state.user_stories = parse_user_stories_from_llm_response(revised_response)
                state.feedback = ""

                logger.info(f"[review_user_stories] Updated user stories: {revised_response}")

                state.next_step = "review_user_stories" if state.user_stories else "end"
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

        return  builder.compile()

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


    def run_review_only(self, feedback: Optional[str] = "") -> WorkflowState:
        try:
            if feedback:
                self._apply_feedback(feedback)

            review_graph = self._build_review_graph()
            logger.info("Invoking review_user_stories with updated state.")
            result_state = review_graph.invoke(self.state)
            logger.info(f"Final state after review = {dict(result_state)}")
            return result_state

        except Exception as e:
            logger.exception("Error in run_review_only workflow.")
            raise


    def _apply_feedback(self, feedback: str) -> None:
        """Applies feedback to the current state."""
        trimmed = feedback.strip()
        self.state.feedback = trimmed
        self.state.feedback_history.append(trimmed)
        if self.state.user_stories is not None:
            self.state.revisions.append(self.state.user_stories)
        self.state.user_story_status = "Pending"
        self.state.requirement = f"{(self.state.requirement or "").strip()}. {trimmed}"
        logger.info(f"Feedback applied. Updated requirement: {self.state.requirement}")


    def _build_review_graph(self) ->StateGraph:  
        """Creates a LangGraph for the review flow only."""
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

        return builder.compile()
