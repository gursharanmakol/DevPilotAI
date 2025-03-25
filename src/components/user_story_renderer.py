import json

import streamlit as st

def render_user_stories(user_stories):
    """
    Render user stories and acceptance criteria from a JSON string or dict.
    """

    st.write("🧪 Type of user_stories:", type(user_stories))
    st.json(user_stories)

    try:
        if isinstance(user_stories, str):
            parsed = json.loads(user_stories.strip())
        elif isinstance(user_stories, dict):
            parsed = user_stories
        else:
            st.warning("User stories are not in a recognized format.")
            return

        stories = parsed.get("user_stories", [])

        # Normalize if single object
        if isinstance(stories, dict):
            stories = [stories]

        for idx, story in enumerate(stories):
            user_story_text = story.get("user_story", "").strip()
            st.subheader(f"User Story {idx + 1}")
            st.markdown(user_story_text)

            criteria = story.get("acceptance_criteria", [])
            if criteria:
                st.markdown("#### Acceptance Criteria")
                for criterion in criteria:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&rarr; {criterion.strip()}")
            else:
                st.markdown("_No acceptance criteria provided._")

    except json.JSONDecodeError:
        st.error("❌ Failed to parse user stories as JSON.")
