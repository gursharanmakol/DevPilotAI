import json
import re

from typing import List, Union
from pydantic import ValidationError

from src.state.workflow_state import UserStoryModel
from src.utils.logger import Logger

logger = Logger(__name__)

def parse_user_stories_from_llm_response(raw_response: Union[str, dict]) -> List[UserStoryModel]:
    """
    Parses LLM response into a list of validated user stories.

    Args:
        raw_response (str | dict): JSON string, dict, or markdown response from LLM.

    Returns:
        List[UserStoryModel]: Validated list of user stories.
    """
    try:
        if isinstance(raw_response, str):
            json_block = re.search(r"```json(.*?)```", raw_response, re.DOTALL)
            clean = json_block.group(1).strip() if json_block else raw_response.strip()
            parsed = json.loads(clean)
        elif isinstance(raw_response, dict):
            parsed = raw_response
        else:
            raise ValueError("Unsupported response type from LLM.")

        stories = parsed.get("user_stories", [])
        if isinstance(stories, dict):
            stories = [stories]

        validated = [UserStoryModel(**story) for story in stories]
        return validated

    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return []
