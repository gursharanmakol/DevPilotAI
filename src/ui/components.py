import streamlit as st

def render_heading(title: str, level: int = 3) -> None:
    level = min(max(level, 1), 6)  # Clamp level between 1 and 6
    st.markdown(f"{'#' * level} {title}")

def render_section_heading(title: str) -> None:
    st.markdown(f"### {title}")

def render_divider() -> None:
    st.markdown("---")

def render_labeled_text(label: str, content: str) -> None:
    st.markdown(f"**{label}**  \n{content}")



