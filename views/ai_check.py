"""AI second opinion: the prompt, the AI's response, and what I made of it.

Content lives in dashboard/content/ so it can be pasted in without touching code:
  ai_prompt.md     the exact prompt
  ai_response.md   the AI tool's full response
  ai_takeaways.md  where we agreed, where we didn't, what I changed
"""

import streamlit as st

from common import HERE

CONTENT = HERE / "content"


def read(name):
    f = CONTENT / name
    return f.read_text().strip() if f.exists() and f.read_text().strip() else None


st.title("AI critique")

takeaways = read("ai_takeaways.md")
if takeaways:
    st.markdown(takeaways)
else:
    st.info("Takeaways coming soon.")

with st.expander("The prompt"):
    prompt = read("ai_prompt.md")
    st.markdown(f"```\n{prompt}\n```" if prompt else "_Not added yet._")
with st.expander("What it said (full response)"):
    st.markdown(read("ai_response.md") or "_Not added yet._")
