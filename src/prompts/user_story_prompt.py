def generate_user_story_prompt(requirement: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful product owner assistant who writes user stories and acceptance criteria. "
                "Output your response in raw JSON format only — no explanations, no markdown."
            ),
        },
        {
            "role": "user",
            "content": f"""
            Generate user stories and acceptance criteria for this requirement:

            Requirement: {requirement}

            "Return only JSON with user stories and acceptance criteria in this structure:"

            ```json
            {{
            "user_stories": [
                {{
                "user_story": "As a ..., I want ... so that ...",
                "acceptance_criteria": [
                    "Criterion 1",
                    "Criterion 2"
                ]
                }}
            ]
            }}
            ```""",
        },
    ]
