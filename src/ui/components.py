import streamlit as st

def render_section_heading(title: str):
    st.markdown(f"### {title}")

def render_divider():
    st.markdown("---")

def render_labeled_text(label: str, content: str):
    st.markdown(f"**{label}**  \n{content}")
