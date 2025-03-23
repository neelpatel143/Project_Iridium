import asyncio
import os
import pygame
import edge_tts
import re
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
ASSISTANT_VOICE = env_vars.get("AssistantVoice", "en-US-AriaNeural")

def sanitize_text(text: str) -> str:
    """Removes asterisks and unwanted characters from text."""
    return re.sub(r"\*", "", text)

async def generate_audio(text: str, output_file: str) -> None:
    """Generates speech audio asynchronously."""
    communicator = edge_tts.Communicate(text, ASSISTANT_VOICE, pitch="+0Hz", rate="+10%")
    await communicator.save(output_file)

async def text_to_speech(text: str) -> None:
    """Handles TTS playback asynchronously."""
    text = sanitize_text(text)
    output_file = os.path.join("Data", "speech.mp3")

    if os.path.exists(output_file):
        os.remove(output_file)

    try:
        await generate_audio(text, output_file)
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
        asyncio.run(text_to_speech(text))
