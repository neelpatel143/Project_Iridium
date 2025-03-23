from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables with error handling
try:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_vars = dotenv_values(env_path)
    if not env_vars:
        raise ValueError("Empty .env file")
    InputLanguage = env_vars.get("InputLanguage", "en-US")
except Exception as e:
    print(f"Error loading .env file: {str(e)}")
    print("Using default language: en-US")
    InputLanguage = "en-US"

# Define the HTML code for the speech recognition interface
HtmlCode = '''<html>
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file
html_path = os.path.join(os.path.dirname(__file__), "..", "Data", "Voice.html")
os.makedirs(os.path.dirname(html_path), exist_ok=True)
with open(html_path, "w", encoding='utf-8') as f:
    f.write(HtmlCode)

# Generate the file path for the HTML file
Link = html_path.replace("\\", "/")

def find_chrome_binary():
    """Find Chrome binary in common installation locations"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# Set Chrome options for the WebDriver
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Find and set Chrome binary location
chrome_path = find_chrome_binary()
if chrome_path:
    chrome_options.binary_location = chrome_path
else:
    raise Exception("Chrome browser not found. Please install Google Chrome.")

# Initialize the Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)  # 10 second timeout

# Define the path for temporary files
current_dir = os.path.dirname(__file__)
TempDirPath = os.path.join(current_dir, "..", "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    """Set the assistant's status by writing it to a file"""
    status_path = os.path.join(TempDirPath, "Status.data")
    with open(status_path, "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    """Modify a query to ensure proper punctuation and formatting"""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "when", "where", "why", "who", "which", "whose", 
                     "whom", "can you", "what's", "where's", "who's", "how's", "when's", 
                     "why's", "what're"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def UniversalTranslator(Text):
    """Translate text into English"""
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()


def SpeechRecognition():
    """Convert speech to text using Chrome WebDriver"""
    try:
        # Open the HTML file in the browser
        driver.get("file:///" + Link)
        
        # Wait for start button and click it
        start_button = wait.until(EC.element_to_be_clickable((By.ID, "start")))
        start_button.click()
        
        while True:
            try:
                # Wait for output element with text
                output_element = wait.until(EC.presence_of_element_located((By.ID, "output")))
                Text = output_element.text
                
                if Text:
                    # Wait for end button and click it
                    end_button = wait.until(EC.element_to_be_clickable((By.ID, "end")))
                    end_button.click()
                    
                    if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                        return QueryModifier(Text)
                    else:
                        SetAssistantStatus("Translating ...")
                        return QueryModifier(UniversalTranslator(Text))
                        
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
            except TimeoutException:
                continue
            except Exception as e:
                print(f"Error during recognition: {str(e)}")
                continue
                
    except WebDriverException as e:
        print(f"WebDriver error: {str(e)}")
        driver.quit()
        return None
    except Exception as e:
        print(f"Error initializing speech recognition: {str(e)}")
        driver.quit()
        return None
    


if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            if Text:
                print(Text)
    except KeyboardInterrupt:
        print("\nStopping speech recognition...")
    finally:
        driver.quit()