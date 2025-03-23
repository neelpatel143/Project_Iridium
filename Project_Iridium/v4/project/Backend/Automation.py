# Automation.py
import os
import subprocess
import time
import pyautogui
import webbrowser
from pywhatkit import search
import requests
from AppOpener import open as appopen
from pywhatkit.core.exceptions import InternetException
import psutil
import pygetwindow as gw

# --- Functions to Open/Close Apps/Websites ---

def open_application(app: str) -> bool:
    """
    Open a Windows application using AppOpener.
    This function launches the closest matching Windows application.
    """
    try:
        appopen(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as e:
        print(f"Error opening application '{app}': {e}")
        return False

def open_website(website: str) -> bool:
    """
    Open a website using the default web browser.
    """
    try:
        # If website does not start with http, assume it's a domain name.
        if not website.startswith("http"):
            url = f"https://{website}.com"
        else:
            url = website
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Error opening website '{website}': {e}")
        return False

def close_app(app: str) -> bool:
    """Close an application using system commands."""
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/IM", f"{app}.exe", "/F"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.run(["pkill", "-9", app],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        print(f"Error closing {app}: {e}")
        return False

def search_youtube(query: str) -> bool:
    """Open YouTube search results for the given query."""
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return True
    except InternetException:
        print("⚠️ No internet connection. Cannot search YouTube.")
        return False
    except Exception as e:
        print(f"⚠️ Error searching YouTube: {e}")
        return False

def google_search(query: str) -> bool:
    """Perform a Google search for the given query."""
    try:
        search(query)  # This triggers an internet connection check.
        return True
    except InternetException:
        print("⚠️ No internet connection. Cannot perform Google search.")
        return False
    except Exception as e:
        print(f"⚠️ Error performing Google search: {e}")
        return False

def is_spotify_running():
    """Check if Spotify is already running in the background."""
    for process in psutil.process_iter(["name"]):
        if "spotify" in process.info["name"].lower():
            return True
    return False

def bring_spotify_to_front():
    """Bring Spotify to the front if it's running."""
    try:
        for window in gw.getWindowsWithTitle("Spotify"):
            window.activate()  # ✅ Bring Spotify to the front
            print("🎵 Bringing Spotify to the front...")
            time.sleep(1)  # Small delay to ensure it's focused
            return True
    except Exception as e:
        print(f"⚠️ Could not bring Spotify to the front: {e}")
    return False

def play_spotify(song: str) -> bool:
    """
    Open Spotify and play a song automatically.
    If Spotify is running → Bring it to the front and play.
    If Spotify is NOT running → Open it, then play.
    """
    try:
        if is_spotify_running():
            print("✅ Spotify is already running, bringing it to focus...")
            if not bring_spotify_to_front():
                print("⚠️ Couldn't focus Spotify, trying anyway...")
        else:
            try:
                subprocess.run(["spotify"], check=True)  # Open Spotify app
                time.sleep(5)  # Wait for Spotify to open
            except Exception:
                print("Spotify app not found, opening web player...")
                webbrowser.open("https://open.spotify.com/")
                time.sleep(6)  # Wait for Web Spotify to load
                print("Please make sure you're logged into Spotify Web.")
                return False  

        # ✅ Ensure Spotify is in focus before sending commands
        time.sleep(2)

        # ✅ Search for the song
        pyautogui.hotkey("ctrl", "l")  # Focus on search bar
        time.sleep(1)
        pyautogui.write(song, interval=0.1)
        time.sleep(1)
        pyautogui.press("enter")  # Search for the song

        # ✅ Play the first song in the search results
        time.sleep(2)  # Wait for search results
        pyautogui.press("tab", presses=3)  # Navigate to the first song
        pyautogui.press("enter")  # Play the song
        
        print(f"🎵 Now playing: {song}")

        return True  # Successfully played the song

    except Exception as e:
        print(f"❌ Error playing Spotify: {e}")
        return False
    

# --- Windows Volume Control Helpers ---

if os.name == 'nt':
    import ctypes

    def win_volume_up(presses=1):
        """Simulate pressing the Windows Volume Up key using the Windows API."""
        VK_VOLUME_UP = 0xAF
        for _ in range(presses):
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
            time.sleep(0.05)

    def win_volume_down(presses=1):
        """Simulate pressing the Windows Volume Down key using the Windows API."""
        VK_VOLUME_DOWN = 0xAE
        for _ in range(presses):
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
            time.sleep(0.05)

    def win_volume_mute():
        """Simulate pressing the Windows Mute key using the Windows API."""
        VK_VOLUME_MUTE = 0xAD
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
        time.sleep(0.05)

# --- System Command Function ---

def system_command(command: str) -> bool:
    """
    Execute a system command (e.g., volume up/down, mute).
    This function parses commands such as "volume up 10%" or "vol down 5%"
    and simulates repeated key presses.
    """
    try:
        command = command.lower().strip()
        # On Windows, use the Windows API for volume keys.
        if os.name == 'nt':
            import re
            if "volume up" in command or "vol up" in command:
                match = re.search(r'(\d+)', command)
                if match:
                    num = int(match.group(1))
                    # Assuming each key press changes volume by roughly 2%.
                    presses = max(1, round(num / 2))
                else:
                    presses = 1
                win_volume_up(presses)
                return True
            elif "volume down" in command or "vol down" in command:
                match = re.search(r'(\d+)', command)
                if match:
                    num = int(match.group(1))
                    presses = max(1, round(num / 2))
                else:
                    presses = 1
                win_volume_down(presses)
                return True
            elif "mute" in command:
                win_volume_mute()
                return True
            else:
                print(f"Command '{command}' not recognized.")
                return False
        else:
            # Fallback for non-Windows systems using the keyboard library.
            import keyboard
            if "volume up" in command or "vol up" in command:
                import re
                match = re.search(r'(\d+)', command)
                if match:
                    num = int(match.group(1))
                    presses = max(1, round(num / 2))
                else:
                    presses = 1
                for _ in range(presses):
                    keyboard.press_and_release("volume up")
                return True
            elif "volume down" in command or "vol down" in command:
                import re
                match = re.search(r'(\d+)', command)
                if match:
                    num = int(match.group(1))
                    presses = max(1, round(num / 2))
                else:
                    presses = 1
                for _ in range(presses):
                    keyboard.press_and_release("volume down")
                return True
            elif "mute" in command:
                keyboard.press_and_release("volumemute")
                return True
            else:
                print(f"Command '{command}' not recognized.")
                return False
    except Exception as e:
        print(f"Error executing system command: {e}")
        return False

# --- Asynchronous Task Executor ---

import asyncio

async def automation_task(commands: list) -> list:
    """
    Execute a list of automation commands asynchronously.
    Supported commands:
      - "open <app>"              : Opens a Windows application.
      - "open website <site>"     : Opens a website in the browser.
      - "close <app>"             : Closes an application.
      - "play youtube <query>"    : Opens YouTube search results for a query.
      - "google search <query>"   : Performs a Google search.
      - "system <command>"        : Executes a system command (e.g., "volume up 10%").
      - "play spotify <song>"     : Opens Spotify and searches for a song.
    """
    loop = asyncio.get_event_loop()
    tasks = []
    for command in commands:
        if command.startswith("open website "):
            website = command.replace("open website ", "").strip()
            tasks.append(loop.run_in_executor(None, open_website, website))
        elif command.startswith("open "):
            app = command.replace("open ", "").strip()
            tasks.append(loop.run_in_executor(None, open_application, app))
        elif command.startswith("close "):
            app = command.replace("close ", "").strip()
            tasks.append(loop.run_in_executor(None, close_app, app))
        elif command.startswith("play youtube "):
            query = command.replace("play youtube ", "").strip()
            tasks.append(loop.run_in_executor(None, search_youtube, query))
        elif command.startswith("google search "):
            query = command.replace("google search ", "").strip()
            tasks.append(loop.run_in_executor(None, google_search, query))
        elif command.startswith("system "):
            cmd = command.replace("system ", "").strip()
            tasks.append(loop.run_in_executor(None, system_command, cmd))
        elif command.startswith("play spotify "):
            song = command.replace("play spotify ", "").strip()
            tasks.append(loop.run_in_executor(None, play_spotify, song))
        else:
            print(f"No function found for command: {command}")
    results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    # Testing some automation functions.
    print("Testing Automation functions...")
    
    # Test opening a website (e.g., "open website youtube")
    open_website("youtube")
    
    # Test opening a Windows application (e.g., "open notepad")
    open_application("notepad")
    
    # Test YouTube search results (instead of playing a video)
    search_youtube("funny cats")
    
    # Test Google search
    google_search("latest news")
    
    # Test Spotify: should open the Spotify app (or fallback to website) and search for the song.
    play_spotify("your favorite song")
    
    # Test system command: "volume up 10%" should simulate multiple key presses.
    system_command("volume up 10%")
