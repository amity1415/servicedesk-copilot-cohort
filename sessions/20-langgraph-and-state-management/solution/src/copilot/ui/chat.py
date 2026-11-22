"""Run with streamlit run src/copilot/ui/chat.py from the learner project."""

import os

import streamlit as st

from copilot.ui.rag_chat import show_chat

st.set_page_config(page_title="Larkhaven IT", page_icon="🛠")
st.title("Larkhaven IT Service Desk")
base = st.sidebar.text_input("API URL", os.getenv("COPILOT_UI_API_URL", "http://localhost:8082"))
token = st.sidebar.text_input("Your access token", type="password")
show_chat(base, token)
