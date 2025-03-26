# src/llms/openai_helper.py
import os

from openai import OpenAI  # type: ignore

from src.prompts.user_story_prompt import generate_user_story_prompt
from src.prompts.revision_prompt import generate_revision_prompt
from src.utils.logger import Logger

logger = Logger(__name__)

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key is not set. Please set the 'OPENAI_API_KEY' environment variable.")
            raise ValueError("Missing OpenAI API key.")
        
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.exception(f"Failed to initialize OpenAI client: {e}")
            raise

    def call_llm_for_user_stories(self, requirement: str) -> str:
        messages = generate_user_story_prompt(requirement)
        return self._call_openai_chat(messages, context="generate user stories")


    def revise_user_stories(self, requirement: str, feedback: str) -> str:
        messages = generate_revision_prompt(requirement, feedback)
        return self._call_openai_chat(messages, context="revise user stories")


    def _call_openai_chat(self, messages: list[dict], context: str) -> str:
        """
        Internal helper to call OpenAI's chat completion API.
        
        Args:
            messages (list): Chat prompt messages.
            context (str): Used for logging (e.g., "generate user story", "revise").

        Returns:
            str: Content string from OpenAI response.
        """
        try:
            logger.info(f"Calling OpenAI to {context}...")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"Received OpenAI response for {context}.")
            return content

        except Exception as e:
            logger.exception(f"Failed to {context} via OpenAI.")
            raise
