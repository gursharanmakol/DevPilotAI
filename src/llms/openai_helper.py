# src/llms/openai_helper.py

import os
from openai import OpenAI
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

    def generate_user_stories(self, requirement: str) -> str:
        try:
            logger.info(f"Generating user story for: {requirement}")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful product owner assistant who writes user stories and acceptance criteria."
                    },
                    {
                        "role": "user",
                        "content": f"Generate user story and acceptance criteria for this requirement: {requirement}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You're a product owner updating user stories."},
                    {"role": "user", "content": f"Original:\n{requirement}\n\nFeedback:\n{feedback}\n\nPlease revise."},
                ],
                temperature=0.7,
                max_tokens=500
            )
            content = response.choices[0].message.content.strip()
            logger.info("Received revised user story from OpenAI.")
            return content
        except Exception as e:
            logger.exception("Failed to revise user stories.")
            raise
