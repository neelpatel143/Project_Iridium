# Reminders.py
import schedule
import time
import threading
from Backend.TextToSpeech import text_to_speech

reminders = []

def check_reminders() -> None:
    """Continuously check and run pending reminders."""
    while True:
        schedule.run_pending()
        time.sleep(1)

def set_reminder(reminder_time: str, message: str) -> bool:
    """Set a daily reminder at the given time (HH:MM) with the specified message."""
    def trigger():
        text_to_speech(f"Reminder: {message}")
    try:
        schedule.every().day.at(reminder_time).do(trigger)
        reminders.append((reminder_time, message))
        return True
    except Exception as e:
        print(f"Error setting reminder: {e}")
        return False

# Start the reminder thread
threading.Thread(target=check_reminders, daemon=True).start()

if __name__ == "__main__":
    # Test reminder (adjust time as needed)
    set_reminder("15:00", "Time to take a break!")
    while True:
        time.sleep(1)
