"""Video walkthrough of the dashboard."""

import streamlit as st

from common import ASSETS

st.title("Video walkthrough")
st.video(str(ASSETS / "walkthrough.mp4"))
