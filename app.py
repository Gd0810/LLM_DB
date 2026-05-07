from __future__ import annotations

import atexit
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from db_chatbot import DatabaseChatbot


load_dotenv()

app = Flask(__name__)
_chatbot: Optional[DatabaseChatbot] = None


def get_chatbot() -> DatabaseChatbot:
    global _chatbot
    if _chatbot is None:
        _chatbot = DatabaseChatbot.from_env()
    return _chatbot


@app.route("/")
def index():
    chatbot = get_chatbot()
    return render_template(
        "index.html",
        database_name=chatbot.mysql_database,
        max_read_rows=chatbot.max_read_rows,
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    chatbot = get_chatbot()
    return jsonify({"ok": True, "database": chatbot.mysql_database})


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Question is required."}), 400

    try:
        answer = get_chatbot().answer_question(question)
        return jsonify({"answer": answer})
    except Exception as error:
        return jsonify({"error": f"Error answering question: {error}"}), 500


@app.route("/api/tables", methods=["GET"])
def list_tables():
    chatbot = get_chatbot()
    return jsonify({"tables": chatbot.list_tables()})


@app.route("/api/table/<table_name>", methods=["GET"])
def get_table(table_name: str):
    chatbot = get_chatbot()
    limit_raw = request.args.get("limit", "50")

    try:
        limit = int(limit_raw)
    except ValueError:
        return jsonify({"error": "limit must be a valid integer."}), 400

    try:
        rows = chatbot.get_table_data(table_name, limit=limit)
        return jsonify({"table": table_name, "rows": rows, "limit": min(max(1, limit), chatbot.max_read_rows)})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/summary", methods=["GET"])
def summary():
    try:
        return jsonify({"summary": get_chatbot().show_available_data()})
    except Exception as error:
        return jsonify({"error": str(error)}), 500


def shutdown_chatbot():
    global _chatbot
    if _chatbot is not None:
        try:
            _chatbot.close()
        finally:
            _chatbot = None

atexit.register(shutdown_chatbot)


if __name__ == "__main__":
    app.run(debug=True)
