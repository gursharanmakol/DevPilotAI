# src/prompts/code_generation_prompt.py

def generate_code_generation_prompt(design_doc: str) -> list[dict]:
    """
    Returns messages instructing the LLM to create multi-file code based on a design doc.
    """
    return [
        {
            "role": "system",
            "content": (
                "You are a code-generating assistant that produces Python code across multiple files. "
                "Output only valid JSON with a 'files' object containing {filename: file_content}."
            ),
        },
        {
            "role": "user",
            "content": f"""
            Generate code based on this design document:

            {design_doc}

            "Return only JSON with the following structure:"

            ```json
            {{
                "files": {{
                    "main.py": "... code for main ...",
                    "utils.py": "... code for utilities ..."
                }}
            }}
            ``` 
            """
        }
    ]
