# src/llms/openai_helper.py
import os

from openai import OpenAI

from src.prompts.user_story_prompt import generate_user_story_prompt
from src.prompts.revision_prompt import generate_revision_prompt
from src.tools.logger import Logger

logger = Logger("openai_helper")

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
        try:
            logger.info(f"Generating user story for: {requirement}")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=generate_user_story_prompt(requirement),
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()
            logger.info("Received user story content from OpenAI.")
            return content

        except Exception as e:
            logger.exception(f"Failed to generate user stories from OpenAI: {e}")
            raise


    def revise_user_stories(self, requirement: str, feedback: str) -> str:
        try:
            logger.info("Sending revised prompt to OpenAI.")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=generate_revision_prompt(requirement, feedback),
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500,
            )
            content = response.choices[0].message.content.strip()
            logger.info("Received revised user story from OpenAI.")
            return content
        except Exception as e:
            logger.exception("Failed to revise user stories.")
            raise
