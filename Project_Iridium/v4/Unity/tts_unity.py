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

if __name__ == "__main__":
    while True:
        user_input = input("💬 Enter text (or 'exit' to quit): ").strip().lower()
        if user_input == "exit":
            break
        elif user_input == "yes":
            send_command("start_speaking")
        elif user_input == "no":
            send_command("stop_speaking")
        else:
            print("Error")
