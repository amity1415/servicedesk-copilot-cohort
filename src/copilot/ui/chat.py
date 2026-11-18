"""Run with streamlit run src/copilot/ui/chat.py."""

import os
import uuid

import httpx
import streamlit as st

st.set_page_config(page_title="Larkhaven IT", page_icon="🛠")
st.title("Larkhaven IT Service Desk")
base = st.sidebar.text_input("API URL", os.getenv("COPILOT_UI_API_URL", "http://localhost:8082"))
token = st.sidebar.text_input("Your access token", type="password")
headers = {"Authorization": f"Bearer {token}"}
if "thread" not in st.session_state:
    st.session_state.thread = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
query = st.chat_input("Describe your IT issue")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    try:
        response = httpx.post(
            base + "/ask",
            headers=headers,
            json={"question": query, "thread_id": st.session_state.thread},
            timeout=40,
        )
        response.raise_for_status()
        result = response.json()
        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
        st.write(result["answer"])
        st.json(result.get("citations", []))
        if "request" in result:
            st.info(f"Request {result['request']['id']}: {result['request']['status']}")
    except httpx.HTTPError as exc:
        st.error(str(exc))
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
