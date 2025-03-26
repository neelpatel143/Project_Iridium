import asyncio
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import text_to_speech
from Backend.Automation import (
    open_application,
    open_website,
    close_app,
    search_youtube,
    google_search,
    system_command,
    play_spotify,
)
from Backend.Chatbot import chatbot
from Backend.RealtimeSearchEngine import realtime_search_engine
from Backend.Reminders import set_reminder
from Backend.Auto import SystemControl
from Backend.CommandAliases import COMMAND_PREFIXES  # Import command aliases

# Memory for the last opened application
task_memory = {"last_opened_app": None}

def extract_command(text: str) -> (str, str):
    """
    Check the input text against all known command prefixes.
    Returns a tuple (command_type, detail). If no prefix matches, returns (None, text).
    """
    text_lower = text.lower().strip()
    for cmd_type, prefixes in COMMAND_PREFIXES.items():
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                detail = text_lower[len(prefix):].strip().strip(".")
                return cmd_type, detail
    return None, text

def execute_command(text: str) -> str:
    cmd_type, detail = extract_command(text)
    
    if cmd_type:
        print(f"Matched command: {cmd_type} with detail: '{detail}'")
    else:
        print("No specific command matched; treating as general query.")

    try:
        if cmd_type == "open_website":
            if not detail:
                return "No website specified."
            return f"Opening website {detail}." if open_website(detail) else f"Failed to open website {detail}."

        elif cmd_type == "open_app":
            if not detail:
                return "No application specified to open."
            if open_application(detail):
                task_memory["last_opened_app"] = detail  # Save last opened app
                return f"Opening {detail}."
            else:
                return f"No application found named '{detail}'."

        elif cmd_type == "close":
            # Resolve "it" or "that" to the last opened app
            if detail in ["it", "that", "that application"] and task_memory.get("last_opened_app"):
                detail = task_memory["last_opened_app"]
            
            if not detail:
                return "No application specified to close."
            return f"Closing {detail}." if close_app(detail) else f"No application found named '{detail}'."

        elif cmd_type == "play_youtube":
            if not detail:
                return "No YouTube query specified."
            return f"Opening YouTube search results for '{detail}'." if search_youtube(detail) else f"Failed to search YouTube for '{detail}'."

        elif cmd_type == "play_spotify":
            if not detail:
                return "No song specified for Spotify."
            return f"Playing {detail} on Spotify." if play_spotify(detail) else "Failed to play on Spotify."

        elif cmd_type == "system":
            if not detail:
                return "No system command specified."
            return f"System command '{detail}' executed." if system_command(detail) else f"Failed to execute system command '{detail}'."

        elif cmd_type == "brightness":
            if not detail:
                return "No brightness level specified."
            try:
                level = int(detail.replace("%", ""))
                return f"Screen brightness set to {level}%." if SystemControl.set_brightness(level) else "Failed to set brightness."
            except ValueError:
                return "Invalid brightness command."

        elif cmd_type == "reminder":
            if " at " in detail:
                parts = detail.split(" at ", 1)
                reminder_text, reminder_time = parts[0].strip(), parts[1].strip()
            else:
                reminder_text, reminder_time = detail, "15:00"

            return f"Reminder set for {reminder_time}: {reminder_text}." if set_reminder(reminder_time, reminder_text) else "Failed to set reminder."

        elif cmd_type == "google_search":
            if not detail:
                return "No Google search query specified."
            return f"Searching Google for '{detail}'." if google_search(detail) else "Failed to perform Google search."

        elif cmd_type == "exit":
            return "Exiting assistant."

        elif cmd_type == "realtime":
            return realtime_search_engine(text)

        else:
            return chatbot(text)  # Ensure unmatched phrases go to the chatbot
    except Exception as e:
        return f"Error: {e}"

def main() -> None:
    print("🎤 Voice Assistant Started! (Press Ctrl+C to exit)")
    try:
        while True:
            print("🟢 Listening...")
            recognized_text = SpeechRecognition()
            if not recognized_text:
                print("⚠️ No speech detected, try again.")
                continue
            print(f"👤 You: {recognized_text}")
            response = execute_command(recognized_text)
            print(f"🤖 Assistant: {response}")
            text_to_speech(response)
            if response.lower().startswith("exiting"):
                break
    except KeyboardInterrupt:
        print("\n🔴 Voice Assistant Stopped.")
    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
