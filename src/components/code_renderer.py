import streamlit as st

def render_generated_code(code_files: dict[str, str], debug: bool = False) -> None:
    """
    Render generated code files using collapsible blocks.
    """
    if debug:
        st.write("🧠 code_files type:", type(code_files))
        st.json(code_files)

    if not code_files:
        st.info("No code has been generated yet.")
        return

    for filename, content in code_files.items():
        with st.expander(f"📄 {filename}", expanded=False):
            st.code(content or "(empty)", language="python")
