import ollama
import os
import subprocess
import requests
import asyncio
import re
import time
import psutil
import pyttsx3
import schedule
import threading
import pyautogui
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from bs4 import BeautifulSoup
from rich import print
from dotenv import dotenv_values
from email.mime.text import MIMEText
import smtplib
from pygame import mixer
from ctypes import cast, POINTER
from Backend.Model import first_layer_dmm
import screen_brightness_control as sbc

# --- Configuration ---
env_vars = dotenv_values(".env")
VOLUME_STEP = 2  # Default volume step percentage

# Initialize Text-to-Speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# --- Enhanced Functions ---
class SystemControl:
    @staticmethod
    def force_kill_app(app_name: str):
        """Forcefully kill an application."""
        try:
            if os.name == "nt":  # Windows
                subprocess.run(["taskkill", "/IM", f"{app_name}.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:  # Linux/Mac
                subprocess.run(["pkill", "-9", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error closing {app_name}: {e}")

    @staticmethod
    def volume_up():
        """Simulate pressing volume up key."""
        for _ in range(3):  # Press volume up key 3 times for better effect
            pyautogui.press("volumeup")
    

    @staticmethod
    def set_brightness(level: int):
        """Set screen brightness (0-100)"""
        try:
            sbc.set_brightness(level)
            return True
        except Exception as e:
            print(f"Brightness error: {e}")
            return False

    @staticmethod
    def get_battery_status():
        """Get battery percentage"""
        battery = psutil.sensors_battery()
        return f"Battery at {battery.percent}%"

# --- Enhanced Application Control ---
def OpenWebsite(app):
    try:
        appopen(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception:
        try:
            webopen(f"https://{app}.com")
            return True
        except:
            return False

def CloseApp(app):
    sanitized = app.rstrip('.').strip().lower()
    SystemControl.force_kill_app(sanitized)
    return True

# --- Command Execution ---
def execute_command(classification: str):
    if classification.startswith("close"):
        app = classification.replace("close ", "").strip()
        CloseApp(app)
    elif "system volume up" in classification:
        SystemControl.volume_up()
    elif classification.startswith("open"):
        app = classification.replace("open ", "").strip()
        OpenWebsite(app)
    else:
        print(f"Executing: {classification}")

# --- Main Execution ---
if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        classification = first_layer_dmm(user_input)  # Now correctly imported
        execute_command(classification)