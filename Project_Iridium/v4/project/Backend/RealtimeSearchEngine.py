# RealtimeSearchEngine.py
import datetime
import os
import json
from googlesearch import search
import ollama

CHAT_LOG_PATH = os.path.join("Data", "ChatLog.json")
if not os.path.exists("Data"):
    os.makedirs("Data")

SYSTEM_PROMPT = "You are an AI assistant that provides real-time information based on search results."

def get_current_info() -> str:
    return datetime.datetime.now().strftime("Date: %A, %B %d, %Y | Time: %H:%M:%S")

def google_search_results(query: str, num_results: int = 5) -> str:
    try:
        results = list(search(query, num_results=num_results))
        if results:
            result_text = "\n".join(results)
            return f"Search results for '{query}':\n{result_text}"
        else:
            return "No search results found."
    except Exception as e:
        return f"Error during Google search: {e}"

def realtime_search_engine(prompt: str) -> str:
    try:
        search_results = google_search_results(prompt)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": get_current_info()},
            {"role": "user", "content": search_results}
        ]
        response = ollama.chat(model="llama3.2", messages=messages)
        answer = response['message']['content'].strip()
        return answer
    except Exception as e:
        return f"Error in realtime search engine: {e}"

if __name__ == "__main__":
    while True:
        query = input("Enter your query: ")
        print(realtime_search_engine(query))
