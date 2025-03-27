import streamlit as st

def render_design_documents(functional_doc: str, technical_doc: str, debug: bool = False) -> None:
    """
    Render functional and technical design documents side by side or in sequence.
    """
    if debug:
        st.write("🔍 functional_doc:", functional_doc)
        st.write("🔍 technical_doc:", technical_doc)

    st.subheader("Functional Design Document")
    st.text_area("Functional Spec", value=functional_doc or "(empty)", disabled=True, height=180)

    st.subheader("Technical Design Document")
    st.text_area("Technical Spec", value=technical_doc or "(empty)", disabled=True, height=180)
