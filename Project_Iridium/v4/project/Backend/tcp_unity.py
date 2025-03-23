import pyttsx3  # Text-to-Speech
import socket   # TCP Communication

def send_command(command):
    """Send animation command to Unity via TCP"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 5000))  # Connect to Unity TCP Listener
        client.send(command.encode())  # Send command
        client.close()
        print(f"📤 Sent: {command}")
    except ConnectionRefusedError:
        print("⚠️ Unity is not running or the TCP listener is not active!")
