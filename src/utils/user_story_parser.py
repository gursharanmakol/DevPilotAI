import json
from typing import List, Union
from pydantic import ValidationError
from src.state.workflow_state import UserStoryModel

import logging

logger = logging.getLogger(__name__)

def parse_user_stories_from_llm_response(raw_response: Union[str, dict]) -> List[dict]:
    """
    Parses LLM response into a list of validated user stories.

    Args:
        raw_response (str | dict): JSON string, dict, or markdown response from LLM.

    Returns:
        List[dict]: Validated list of user stories.
    """
    try:
        if isinstance(raw_response, str):
            parsed = json.loads(raw_response.strip())
        elif isinstance(raw_response, dict):
            parsed = raw_response
        else:
            raise ValueError("Unsupported response type from LLM.")

        stories = parsed.get("user_stories", [])
        if isinstance(stories, dict):
            stories = [stories]

        validated = [UserStoryModel(**story).model_dump() for story in stories]
        return validated

    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return []

    except ValidationError as ve:
        logger.error("Validation failed for LLM user stories: {ve}")
        raise ve
