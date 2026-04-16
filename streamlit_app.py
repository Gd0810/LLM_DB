from typing import List, Dict, Any

import streamlit as st
from dotenv import load_dotenv

from db_chatbot import DatabaseChatbot


load_dotenv()


@st.cache_resource
def get_chatbot() -> DatabaseChatbot:
    return DatabaseChatbot.from_env()


def render_sidebar_chat(chatbot: DatabaseChatbot) -> None:
    st.sidebar.header("Working Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        if role == "user":
            st.sidebar.markdown(f"**You:** {content}")
        else:
            st.sidebar.markdown(f"**Bot:** {content}")

    with st.sidebar.form("chat_form", clear_on_submit=True):
        user_text = st.text_input("Ask database question")
        submitted = st.form_submit_button("Send")

    if submitted and user_text.strip():
        question = user_text.strip()
        st.session_state.chat_history.append({"role": "user", "content": question})
        try:
            answer = chatbot.answer_question(question)
        except Exception as error:
            answer = f"Error answering question: {error}"
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


def render_tables(chatbot: DatabaseChatbot, preview_limit: int) -> None:
    tables = chatbot.list_tables()
    if not tables:
        st.info("No tables found in this database.")
        return

    st.subheader("All Tables")
    for table_name in tables:
        try:
            rows: List[Dict[str, Any]] = chatbot.get_table_data(table_name, limit=preview_limit)
        except Exception as error:
            st.error(f"Failed to load table '{table_name}': {error}")
            continue

        with st.expander(f"{table_name} (showing up to {preview_limit} rows)", expanded=False):
            if not rows:
                st.write("No records found.")
            else:
                st.dataframe(rows, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="LLM DB Chatbot", layout="wide")
    st.title("Database Control Panel")

    try:
        chatbot = get_chatbot()
    except Exception as error:
        st.error(f"Configuration error: {error}")
        st.stop()

    st.caption(f"Connected database: {chatbot.mysql_database}")

    preview_limit = st.sidebar.slider(
        "Table preview rows",
        min_value=5,
        max_value=min(500, chatbot.max_read_rows),
        value=min(50, chatbot.max_read_rows),
        step=5,
    )

    render_sidebar_chat(chatbot)
    render_tables(chatbot, preview_limit)


if __name__ == "__main__":
    main()
