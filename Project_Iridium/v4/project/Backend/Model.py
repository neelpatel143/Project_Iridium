# Model.py
import re
import ollama
from dateparser import parse

# List of supported command categories
CATEGORIES = [
    "exit", "general", "realtime", "open", "close", "play",
    "system", "reminder", "brightness", "google search", "play spotify"
]

PREAMBLE = (
    "You are a Decision-Making Model that classifies queries. "
    "Return a classification in the format '<command> <details>' where command is one of: " +
    ", ".join(CATEGORIES) +
    ". Only return the classification without additional text."
)

last_opened_app = None

def clean_text(text: str) -> str:
    """Clean and normalize the classification text."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9 %]+", " ", text)
    return text

def first_layer_dmm(prompt: str) -> str:
    """Classify the prompt using Ollama’s local Llama model."""
    global last_opened_app
    input_text = f"{PREAMBLE}\nUser: {prompt}\nClassification: "
    try:
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": input_text}])
        classification = response.get('message', {}).get('content', '').strip()
        classification = clean_text(classification)
        
        # Track last opened app for close commands
        if classification.startswith("open"):
            last_opened_app = classification.replace("open", "").strip()
        elif classification.startswith("close") and "last opened" in classification and last_opened_app:
            classification = f"close {last_opened_app}"
        
        return classification
    except Exception as e:
        print(f"Model error: {e}")
        # Provide a clearer fallback in case of an error
        return f"general {prompt}"

def parse_time_from_text(text: str) -> str:
    """Parse a time string using dateparser; defaults to 15:00 if parsing fails."""
    try:
        dt = parse(text, settings={'PREFER_DATES_FROM': 'future'})
        if dt:
            return dt.strftime("%H:%M")
        else:
            return "15:00"
    except Exception as e:
        print(f"Error parsing time: {e}")
        return "15:00"


if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        print("Classification:", first_layer_dmm(user_input))
