# src/utils/design_doc_parser.py

import json
from typing import Union
from src.utils.logger import Logger

logger = Logger(__name__)

def parse_design_doc_response(raw_response: Union[str, dict]) -> dict:
    """
    Parses LLM response into a dictionary containing design docs.

    Args:
        raw_response (str | dict): JSON string or dict from LLM response.

    Returns:
        dict: { "functional_doc": str, "technical_doc": str }
    """
    try:
        if isinstance(raw_response, str):
            clean = raw_response.strip()
            if "```json" in clean:
                import re
                json_block = re.search(r"```json(.*?)```", clean, re.DOTALL)
                clean = json_block.group(1).strip() if json_block else clean
            parsed = json.loads(clean)
        elif isinstance(raw_response, dict):
            parsed = raw_response
        else:
            raise ValueError("Unsupported response type.")

        return {
            "functional_doc": parsed.get("functional_doc", ""),
            "technical_doc": parsed.get("technical_doc", "")
        }

    except Exception as e:
        logger.error(f"Failed to parse design doc response: {e}")
        return {"functional_doc": "", "technical_doc": ""}
