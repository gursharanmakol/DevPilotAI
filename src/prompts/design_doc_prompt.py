# src/prompts/design_doc_prompt.py

def generate_design_doc_prompt(requirement: str, user_stories: str = "") -> list[dict]:
    """
    Returns a ChatCompletion-like prompt instructing the LLM to produce a design doc.
    We can pass user_stories in case we want to reference them in the doc.
    """
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that creates a combined functional and technical design document. "
                "Output your response in JSON format only—no markdown, no extra commentary."
            ),
        },
        {
            "role": "user",
            "content": f"""
            Create a design document that covers both functional and technical aspects,
            referencing the following requirement and user stories:

            Requirement: {requirement}
            User Stories: {user_stories}

            "Output only JSON, with keys 'functional_doc' and 'technical_doc', like this:"

            ```json
            {{
              "functional_doc": "Functional description here...",
              "technical_doc": "Technical details here..."
            }}
            ```"""
        },
    ]
