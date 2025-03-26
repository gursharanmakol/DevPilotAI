# src/components/user_story_renderer.py

import json

import streamlit as st

def render_user_stories(user_stories, debug=False):
    """
    Render user stories and acceptance criteria from list[UserStoryModel] or JSON.
    """

    if debug:
        st.write("🧪 Type of user_stories:", type(user_stories))
        st.json(user_stories)

    try:
        # ✅ NEW: If user_stories is a list of UserStoryModel, convert to dicts
        if isinstance(user_stories, list) and all(hasattr(s, "user_story") for s in user_stories):
            parsed = [s.model_dump() if hasattr(s, "model_dump") else s for s in user_stories]

        # ✅ Existing path: if passed as dict
        elif isinstance(user_stories, str):
            parsed = json.loads(user_stories.strip()).get("user_stories", [])
        elif isinstance(user_stories, dict):
            parsed = user_stories.get("user_stories", [])
        else:
            st.warning("User stories are not in a recognized format.")
            return

        if isinstance(parsed, dict):
            parsed = [parsed]

        for idx, story in enumerate(parsed):
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

    except Exception as e:
        st.error(f"❌ Failed to render user stories: {e}")
