# src/graph/workflow.py

from typing import Any, Optional

from langgraph.graph import StateGraph, END # type: ignore

from src.llms.openai_helper import OpenAIService
from src.state.workflow_state import WorkflowState
from src.graph.nodes import *

from src.utils.logger import Logger

logger = Logger(__name__)

class Workflow:
    def __init__(self, requirement: str):
        self.state = WorkflowState(requirement=requirement)
        self.ai_service = OpenAIService()


    def build_workflow(self) -> StateGraph:
        builder = StateGraph(WorkflowState)
        builder.add_node("get_user_stories",  lambda s: get_user_stories(s, self.ai_service))
        builder.add_node("review_user_stories",lambda s: review_user_stories(s, self.ai_service))
        builder.add_node("generate_design_doc", lambda s :generate_design_doc(s, self.ai_service))   
        builder.add_node("generate_code",  lambda s: generate_code_files(s, self.ai_service))
        builder.add_node("review_design_doc", lambda s: review_design_doc(s, self.ai_service))
        builder.add_node("review_code", lambda s: review_code(s, self.ai_service))

        builder.set_entry_point("get_user_stories")
        builder.add_edge("get_user_stories", "review_user_stories")
        builder.add_edge("review_user_stories", "generate_design_doc")
        builder.add_edge("generate_design_doc", "review_design_doc")
        builder.add_edge("review_design_doc", "generate_code")
        builder.add_edge("generate_code", "review_code")

        builder.add_conditional_edges(
            "review_code",
            lambda state: state.next_step,
            {
                "review_code": "review_code",
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
            return get_user_stories(self.state, self.ai_service)
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
        builder.add_node("review_user_stories", lambda s: review_user_stories(s, self.ai_service))
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
