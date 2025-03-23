# src/graph/user_story.py
import json
import re

from src.llms.openai_helper import OpenAIService
from src.tools.logger import Logger

logger = Logger("user_story")


def get_user_stories(requirement: str) -> str:
    try:
        ai_service = OpenAIService()
        story = ai_service.generate_user_stories(requirement)
        logger.info("AI-generated user story successfully.")
        return story

    except Exception as e:
        logger.warning("Falling back to default user story template.")
        return f"""
                **User Story:** As a user, I want to use an AI solution for {requirement}.

                **Acceptance Criteria:**
                - Accepts user queries
                - Provides contextual answers
                - Escalates when unsure
                """

def parse_user_story_response(response: str):
    """
    Attempts to parse the OpenAI user story response.
    If it contains structured JSON, return that.
    Otherwise, return raw string.
    """
    try:
        json_block = re.search(r"```json(.*?)```", response, re.DOTALL)
        if json_block:
            return json.loads(json_block.group(1).strip())
        return response.strip()
    except Exception as e:
        logger.warning(f"Failed to parse user story JSON: {e}")
        return response.strip()