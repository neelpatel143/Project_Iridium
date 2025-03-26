# TextToSpeech.py
import asyncio
import os
import pygame
import edge_tts
import re
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
ASSISTANT_VOICE = env_vars.get("AssistantVoice", "en-US-AriaNeural")

def sanitize_text(text: str) -> str:
    # Remove asterisks and any other unwanted characters
    text = re.sub(r"\*", "", text)
    return text

async def generate_audio(text: str, output_file: str) -> None:
    # Adjusting pitch and rate to reduce long pauses and prevent cutoffs
    communicator = edge_tts.Communicate(text, ASSISTANT_VOICE, pitch="+0Hz", rate="+10%")
    await communicator.save(output_file)

def text_to_speech(text: str) -> None:
    text = sanitize_text(text)
    output_file = os.path.join("Data", "speech.mp3")
    if os.path.exists(output_file):
        os.remove(output_file)
    try:
        asyncio.run(generate_audio(text, output_file))
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        # Wait until playback is complete
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        pygame.mixer.quit()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

if __name__ == "__main__":
    while True:
        text = input("Enter text to speak: ")
        text_to_speech(text)
