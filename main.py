from dotenv import load_dotenv
from db_chatbot import DatabaseChatbot


load_dotenv()

def main() -> None:
    try:
        chatbot = DatabaseChatbot.from_env()
    except Exception as error:
        print("Configuration error:", error)
        return

    print("Database chatbot is ready. Ask questions about product_demo_db.")
    print("Type 'exit' or 'quit' to stop.\n")

    try:
        while True:
            question = input("Question> ").strip()
            if not question:
                continue
            if question.lower() in {"exit", "quit", "bye"}:
                break

            try:
                answer = chatbot.answer_question(question)
                print(answer)
            except Exception as error:
                print("Error answering question:", error)
    finally:
        chatbot.close()


if __name__ == "__main__":
    main()
