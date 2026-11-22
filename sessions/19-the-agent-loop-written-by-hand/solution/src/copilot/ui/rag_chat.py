"""Render the same citation-aware conversation in the lesson and full UI."""

import hashlib
from pathlib import PurePosixPath
from uuid import uuid4

import httpx
import streamlit as st


def show_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        for citation in message.get("citations", []):
            filename = PurePosixPath(citation["source"].replace("\\", "/")).name
            st.caption(f"Source {citation['document_id']} · {filename}")
        if "request" in message:
            request = message["request"]
            st.info(f"Request {request['id']} is {request['status']}.")


def show_chat(base: str, token: str) -> None:
    identity = hashlib.sha256(f"{base}\0{token}".encode()).hexdigest()
    if st.session_state.get("chat_connection") != identity:
        st.session_state.chat_connection = identity
        st.session_state.thread = str(uuid4())
        st.session_state.messages = []
        st.session_state.pop("approvals", None)

    for message in st.session_state.messages:
        show_message(message)
    question = st.chat_input("Describe your IT issue", disabled=not token.strip())
    if not question:
        return

    message = {"role": "user", "content": question}
    st.session_state.messages.append(message)
    show_message(message)
    try:
        response = httpx.post(
            f"{base.rstrip('/')}/ask",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": question, "thread_id": st.session_state.thread},
            timeout=40,
        )
        response.raise_for_status()
        result = response.json()
        message = {
            "role": "assistant",
            "content": result["answer"],
            "citations": result.get("citations", []),
        }
        if "request" in result:
            message["request"] = result["request"]
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            st.error("Enter a valid service access token.")
        else:
            request_id = exc.response.headers.get("X-Request-ID")
            description = "The service could not complete the request."
            if request_id:
                description += f" Request ID {request_id}."
            st.error(description)
        return
    except httpx.RequestError:
        st.error("The chat service is unreachable.")
        return
    except (KeyError, TypeError, ValueError):
        st.error("The chat service returned an invalid answer.")
        return

    st.session_state.messages.append(message)
    show_message(message)
