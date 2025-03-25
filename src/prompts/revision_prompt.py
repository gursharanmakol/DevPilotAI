def generate_revision_prompt(requirement: str, feedback: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful product owner assistant who revises user stories and acceptance criteria. "
                "Output your response in raw JSON format only — no explanations, no markdown."
            ),
        },
        {
            "role": "user",
            "content": f"""
            Revise the following user story based on the feedback.

            Requirement: {requirement}

            Feedback: {feedback}

            "Return only JSON with user stories and acceptance criteria in this structure:"

            ```json
            {{
            "user_stories": [
                {{
                "user_story": "As a ..., I want ... so that ...",
                "acceptance_criteria": [
                    "Updated Criterion 1",
                    "Updated Criterion 2"
                ]
                }}
            ]
            }}
            ```"""
        },
    ]
