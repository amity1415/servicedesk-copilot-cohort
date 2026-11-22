"""Run with streamlit run src/copilot/ui/chat.py."""

import os

import httpx
import streamlit as st

from copilot.ui.rag_chat import show_chat

st.set_page_config(page_title="Larkhaven IT", page_icon="🛠")
st.title("Larkhaven IT Service Desk")
base = st.sidebar.text_input("API URL", os.getenv("COPILOT_UI_API_URL", "http://localhost:8082"))
token = st.sidebar.text_input("Your access token", type="password")
headers = {"Authorization": f"Bearer {token}"}
show_chat(base, token)
with st.expander("Manager approvals"):
    if st.button("Load my pending requests"):
        response = httpx.get(base + "/approvals", headers=headers, timeout=10)
        if response.is_success:
            st.session_state.approvals = response.json()
        else:
            st.error(response.text)
    for approval in st.session_state.get("approvals", []):
        st.json(approval)
        choice = st.selectbox("Decision", ["approve", "reject"], key=f"choice-{approval['id']}")
        if st.button("Submit decision", key=f"decision-{approval['id']}"):
            response = httpx.post(
                f"{base}/approvals/{approval['id']}",
                headers=headers,
                json={"decision": choice},
                timeout=10,
            )
            st.write(response.json())
rating = st.radio("Was this useful?", [1, -1], horizontal=True)
if st.button("Send feedback"):
    response = httpx.post(base + "/feedback", headers=headers, json={"rating": rating}, timeout=10)
    st.write("Recorded" if response.is_success else response.text)
