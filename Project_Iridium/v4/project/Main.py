import asyncio
import threading
from Backend.gestures import start_gesture_detection
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import text_to_speech
from Backend.Automation import (
    open_application, open_website, close_app, search_youtube,
    google_search, system_command, play_spotify
)
from Backend.Chatbot import chatbot
from Backend.RealtimeSearchEngine import realtime_search_engine
from Backend.Reminders import set_reminder
from Backend.Auto import SystemControl
from Backend.CommandAliases import COMMAND_PREFIXES
from Backend.tcp_unity import send_command

# Memory for last opened application
task_memory = {"last_opened_app": None}

def extract_command(text: str) -> (str, str):
    """Extracts command type and details from user input."""
    text_lower = text.lower().strip()
    for cmd_type, prefixes in COMMAND_PREFIXES.items():
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                detail = text_lower[len(prefix):].strip().strip(".")
                return cmd_type, detail
    return None, text

def execute_command(text: str) -> str:
    """Executes commands based on recognized input."""
    cmd_type, detail = extract_command(text)

    if cmd_type:
        print(f"Matched command: {cmd_type} with detail: '{detail}'")
    else:
        print("No specific command matched; treating as general query.")

    try:
        if cmd_type == "open_website":
            return f"Opening website {detail}." if open_website(detail) else f"Failed to open website {detail}."

        elif cmd_type == "open_app":
            if open_application(detail):
                task_memory["last_opened_app"] = detail
                return f"Opening {detail}."
            return f"No application found named '{detail}'."

        elif cmd_type == "close":
            if detail in ["it", "that"] and task_memory.get("last_opened_app"):
                detail = task_memory["last_opened_app"]
            return f"Closing {detail}." if close_app(detail) else f"No application found named '{detail}'."

        elif cmd_type == "play_youtube":
            return f"Opening YouTube search results for '{detail}'." if search_youtube(detail) else f"Failed to search YouTube for '{detail}'."

        elif cmd_type == "play_spotify":
            return f"Playing {detail} on Spotify." if play_spotify(detail) else "Failed to play on Spotify."

        elif cmd_type == "system":
            return f"System command '{detail}' executed." if system_command(detail) else f"Failed to execute system command '{detail}'."

        elif cmd_type == "brightness":
            try:
                level = int(detail.replace("%", ""))
                return f"Screen brightness set to {level}%." if SystemControl.set_brightness(level) else "Failed to set brightness."
            except ValueError:
                return "Invalid brightness command."

        elif cmd_type == "reminder":
            reminder_text, reminder_time = (detail.split(" at ", 1) + ["15:00"])[:2]
            return f"Reminder set for {reminder_time}: {reminder_text}." if set_reminder(reminder_time, reminder_text) else "Failed to set reminder."

        elif cmd_type == "google_search":
            return f"Searching Google for '{detail}'." if google_search(detail) else "Failed to perform Google search."

        elif cmd_type == "exit":
            return "Exiting assistant."

        elif cmd_type == "realtime":
            return realtime_search_engine(text)

        else:
            return chatbot(text)  # Unrecognized queries go to chatbot
    except Exception as e:
        return f"Error: {e}"

async def voice_assistant():
    """Runs the voice assistant asynchronously."""
    print("🎤 Voice Assistant Started! (Press Ctrl+C to exit)")
    send_command("isIdle")
    try:
        while True:
            send_command("isListening")
            print("🟢 Listening...")
            recognized_text = SpeechRecognition()
            if not recognized_text:
                print("⚠️ No speech detected, try again.")
                continue

            print(f"👤 You: {recognized_text}")
            response = execute_command(recognized_text)
            print(f"🤖 Assistant: {response}")

            send_command("isSpeaking")
            await text_to_speech(response)  # Ensure async execution of TTS

            if response.lower().startswith("exiting"):
                break
    except KeyboardInterrupt:
        print("\n🔴 Voice Assistant Stopped.")
    except Exception as e:
        print(f"Error in main loop: {e}")

def start_gesture_thread():
    """Runs the gesture detection in a separate thread to avoid blocking."""
    try:
        gesture_thread = threading.Thread(target=start_gesture_detection, daemon=True)
        gesture_thread.start()
        print("🖐️ Gesture detection running in the background...")
    except Exception as e:
        print(f"Error starting gesture detection: {e}")

if __name__ == "__main__":
    start_gesture_thread()  # Start gesture recognition
    asyncio.run(voice_assistant())  # Start AI assistant
