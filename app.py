"""Consumer product safety dashboard (DESIGNTK530 Project 1).

Run from this folder:  streamlit run app.py
"""

import streamlit as st

from common import inject_css

st.set_page_config(page_title="Know the Landmines", page_icon="🛡️", layout="wide")
inject_css()

pages = [
    st.Page("views/story.py", title="The story", default=True),
    st.Page("views/check_product.py", title="Check your product"),
    st.Page("views/whats_next.py", title="What I'd test next"),
    st.Page("views/ai_check.py", title="AI critique"),
    st.Page("views/appendix.py", title="Appendix"),
]
st.navigation(pages, position="top").run()
