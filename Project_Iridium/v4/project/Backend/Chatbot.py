# Chatbot.py
import os
import json
import datetime
from dotenv import dotenv_values
import ollama

env_vars = dotenv_values(".env")
ASSISTANT_NAME = env_vars.get("Assistantname", "IRIDIUM")  # Defaults to IRIDIUM
USER_NAME = env_vars.get("Username", "User")

CHAT_LOG_PATH = os.path.join("Data", "ChatLog.json")
os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)

# Initialize the chat log if it doesn't exist
if not os.path.exists(CHAT_LOG_PATH):
    with open(CHAT_LOG_PATH, "w") as f:
        json.dump([], f)

SYSTEM_PROMPT = f"You are an AI assistant named {ASSISTANT_NAME}. Answer professionally and accurately."

def get_current_datetime() -> str:
    return datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")

def load_chat_log() -> list:
    try:
        with open(CHAT_LOG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading chat log: {e}")
        return []

def save_chat_log(log: list) -> None:
    try:
        with open(CHAT_LOG_PATH, "w") as f:
            json.dump(log, f, indent=4)
    except Exception as e:
        print(f"Error saving chat log: {e}")

def answer_modifier(answer: str) -> str:
    # Remove empty lines and unwanted characters like asterisks
    modified = "\n".join(line.strip() for line in answer.split("\n") if line.strip())
    modified = modified.replace("*", "")
    return modified

def chatbot(query: str, retry=False) -> str:
    try:
        chat_log = load_chat_log()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Current time: {get_current_datetime()}"}
        ]
        # Append the user's query
        messages.append({"role": "user", "content": query})

        # Call the AI model via ollama
        response = ollama.chat(model="llama3.2", messages=messages)
        answer = response.get('message', {}).get('content', '').strip()
        answer = answer_modifier(answer)

        # Log the exchange
        chat_log.append({"query": query, "answer": answer, "timestamp": get_current_datetime()})
        save_chat_log(chat_log)

        return answer
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return "I'm sorry, something went wrong processing your request."


if __name__ == "__main__":
    while True:
        query = input("Enter your question: ")
        if query.lower() in ["exit", "quit"]:
            break
        print("Assistant:", chatbot(query))
