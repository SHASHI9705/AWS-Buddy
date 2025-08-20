
import boto3
import speech_recognition as sr
import playsound
import json
import os
from difflib import get_close_matches
## Removed threading import
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

memory = load_memory()
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize AWS Polly
polly = boto3.client("polly", region_name="ap-south-1")
recognizer = sr.Recognizer()

def speak_with_polly(text, voice="Matthew"):
    """Convert text to speech using AWS Polly"""
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice
    )
    with open("buddy_response.mp3", "wb") as f:
        f.write(response["AudioStream"].read())
    playsound.playsound("buddy_response.mp3")

# Load commands
def load_commands():
    if os.path.exists("commands.json"):
        with open("commands.json", "r") as f:
            return json.load(f)
    return {}

# Save commands
def save_commands(cmds):
    with open("commands.json", "w") as f:
        json.dump(cmds, f, indent=4)

# Fuzzy matching
def find_command(user_text, cmds):
    matches = get_close_matches(user_text.lower(), cmds.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None

commands = load_commands()

# Greet the user
intro_message = "Hey, I am your Buddy. Just tell me what to do!"
print(intro_message)
speak_with_polly(intro_message)



typing_mode = False
last_typed_sentence = ""

while True:
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # noise reduction
            print("🎙️ Listening...")
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio, language="en-IN")
        print("✅ You said:", text)

        # Memory: Save facts
        if text.lower().startswith("my name is "):
            name = text[11:].strip()
            if name:
                memory["name"] = name
                save_memory(memory)
                reply = f"Okay, I will remember your name is {name}."
                print(f"🤖 Buddy: {reply}")
                speak_with_polly(reply)
                continue

        if text.lower().startswith("my favourite colour is "):
            color = text[21:].strip()
            if color:
                memory["favorite_color"] = color
                save_memory(memory)
                reply = f"Got it, your favorite color is {color}."
                print(f"🤖 Buddy: {reply}")
                speak_with_polly(reply)
                continue

        if text.lower().startswith("my birthday is "):
            birthday = text[15:].strip()
            if birthday:
                memory["birthday"] = birthday
                save_memory(memory)
                reply = f"Okay, I will remember your birthday is {birthday}."
                print(f"🤖 Buddy: {reply}")
                speak_with_polly(reply)
                continue

        if text.lower().startswith("my favorite food is "):
            food = text[20:].strip()
            if food:
                memory["favorite_food"] = food
                save_memory(memory)
                reply = f"Got it, your favorite food is {food}."
                print(f"🤖 Buddy: {reply}")
                speak_with_polly(reply)
                continue

        if text.lower().startswith("my pet's name is "):
            pet_name = text[17:].strip()
            if pet_name:
                memory["pet_name"] = pet_name
                save_memory(memory)
                reply = f"I will remember your pet's name is {pet_name}."
                print(f"🤖 Buddy: {reply}")
                speak_with_polly(reply)
                continue

        # Memory: Recall facts
        if text.lower().strip() == "what is my name":
            name = memory.get("name")
            if name:
                reply = f"Your name is {name}."
            else:
                reply = "I don't know your name yet."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.lower().strip() == "what is my favourite colour":
            color = memory.get("favorite_color")
            if color:
                reply = f"Your favourite colour is {color}."
            else:
                reply = "I don't know your favourite colour yet."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.lower().strip() == "what is my birthday":
            birthday = memory.get("birthday")
            if birthday:
                reply = f"Your birthday is {birthday}."
            else:
                reply = "I don't know your birthday yet."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.lower().strip() == "what is my favorite food":
            food = memory.get("favorite_food")
            if food:
                reply = f"Your favorite food is {food}."
            else:
                reply = "I don't know your favorite food yet."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.lower().strip() == "what is my pet's name":
            pet_name = memory.get("pet_name")
            if pet_name:
                reply = f"Your pet's name is {pet_name}."
            else:
                reply = "I don't know your pet's name yet."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        # Volume control
        if text.lower().strip() in ["increase volume", "volume up"]:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = min(current + 0.1, 1.0)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            reply = f"Volume increased to {int(new_vol*100)}%."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.lower().strip() in ["decrease volume", "volume down"]:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = max(current - 0.1, 0.0)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            reply = f"Volume decreased to {int(new_vol*100)}%."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.lower().strip() == "mute":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)
            reply = "Volume muted."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.lower().strip() == "unmute":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)
            reply = "Volume unmuted."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        # Close current tab in Chrome
        if text.lower().strip() == "close it":
            import pyautogui
            pyautogui.hotkey('ctrl', 'w')
            continue

        # Open new tab in Chrome
        if text.lower().strip() == "open new tab":
            import pyautogui
            pyautogui.hotkey('ctrl', 't')
            continue
    
        # Open next tab in Chrome
        if text.lower().strip() == "next tab":
            import pyautogui
            pyautogui.hotkey('ctrl', 'tab')
            continue

        # Open previous tab in Chrome
        if text.lower().strip() == "previous tab":
            import pyautogui
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            continue

        # copy all
        if text.lower().strip() == "copy all":
            import pyautogui
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            continue
        # Cut all
        if text.lower().strip() == "cut all":
            import pyautogui
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('backspace')
            continue

        # Copy a line
        if text.lower().strip() == "copy this line":
            import pyautogui
            pyautogui.hotkey('ctrl', 'c')
            continue
    
        # Close this app
        if text.lower().strip() == "close this app":
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            continue

        # shutdown
        if text.lower().strip() == "shutdown":
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            continue

        # open folder
        if text.lower().strip() == "open folder":
            import pyautogui
            pyautogui.hotkey('ctrl', 'k', 'o')
            continue
    


        # Hit Enter key if user says 'enter' (works in any mode)
        if text.lower().strip() == "enter":
            import pyautogui
            pyautogui.press('enter')
            continue
    

        # Typing mode logic

        if typing_mode:
            if text.lower().strip() == "stop typing":
                typing_mode = False
                reply = "Stopped typing. Listening for other commands."
                print(f"🤖 Buddy: {reply}")
                speak_with_polly(reply)
                continue
            elif text.lower().strip() == "enter":
                import pyautogui
                pyautogui.press('enter')
                continue
            elif text.lower().strip() == "cut all":
                import pyautogui
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('backspace')
                continue
            elif text.lower().strip() == "copy all":
                import pyautogui
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                continue

            
            elif text.lower().strip() == "cut it":
                import pyautogui
                if last_typed_sentence:
                    # Select the last sentence (Shift+Left for each character)
                    for _ in range(len(last_typed_sentence)):
                        pyautogui.keyDown('backspace')
                    last_typed_sentence = ""
                continue
            else:
                import pyautogui
                words = text.strip().split()
                if len(words) > 1:
                    pyautogui.write(text + " ")
                    last_typed_sentence = text + " "
                else:
                    pyautogui.write(text)
                    last_typed_sentence = text
                continue

        # Enter typing mode
        if text.lower().startswith("type "):
            to_type = text[5:].strip()
            if to_type:
                typing_mode = True
                import pyautogui
                words = to_type.split()
                if len(words) > 1:
                    pyautogui.write(to_type + " ")
                    last_typed_sentence = to_type + " "
                else:
                    pyautogui.write(to_type)
                    last_typed_sentence = to_type
            else:
                reply = "Please say what you want me to type after the word 'type'."
                print(f"🤖 Buddy: {reply}")
                speak_with_polly(reply)
            continue


        # Search YouTube if user says 'search ... in youtube'
        if text.lower().startswith("search ") and "in youtube" in text.lower():
            query = text[7:].lower().replace("in youtube", "").strip()
            import webbrowser
            if query:
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                reply = f"Searching for '{query}' on YouTube!"
                try:
                    webbrowser.get('chrome').open(url)
                except Exception:
                    webbrowser.open(url)
                    reply = reply.replace("on YouTube", "in your default browser")
            else:
                reply = "Please say what you want to search after the word 'search'."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        text = recognizer.recognize_google(audio, language="en-IN")
        print("✅ You said:", text)

        # Play song on YouTube if user says 'play ...'
        if text.lower().startswith("play "):
            song = text[5:].strip()
            import webbrowser
            if song:
                try:
                    import requests, re
                    search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
                    response = requests.get(search_url)
                    video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
                    if video_ids:
                        video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                        reply = f"Playing '{song}' on YouTube!"
                        try:
                            webbrowser.get('chrome').open(video_url)
                        except Exception:
                            webbrowser.open(video_url)
                            reply = reply.replace("on YouTube", "in your default browser")
                    else:
                        reply = f"Couldn't find a video for '{song}'."
                except Exception as e:
                    reply = f"Error searching YouTube: {e}"
            else:
                reply = "Please say the song name after the word 'play'."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        if text.strip().lower() == "now you can stop":
            goodbye_message = "Okay, I will stop now. Goodbye!"
            print(goodbye_message)
            speak_with_polly(goodbye_message)
            break

        # Search in Chrome if user says 'search ...'
        if text.lower().startswith("search "):
            query = text[7:].strip()
            import webbrowser
            if query:
                if query.replace(' ', '').lower() == "localhost":
                    url = "http://localhost:3000"
                    reply = "Opening localhost:3000 in Chrome!"
                else:
                    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    reply = f"Searching for '{query}' in Chrome!"
                try:
                    webbrowser.get('chrome').open(url)
                except Exception:
                    webbrowser.open(url)
                    reply = reply.replace("in Chrome", "in your default browser")
            else:
                reply = "Please say what you want to search after the word 'search'."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        # Check for 'open xyz' command (no 'app' required)
        if text.lower().startswith("open "):
            import subprocess
            import os
            app_name = text.lower().replace("open ", "").strip()
            # Try default known apps first
            app_paths = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "wordpad": "write.exe",
                "file explorer": "explorer.exe"
            }
            exe = app_paths.get(app_name)
            if exe:
                try:
                    subprocess.Popen(exe)
                    reply = f"Opening {app_name.capitalize()}!"
                except Exception as e:
                    reply = f"Sorry, I couldn't open {app_name}. Error: {e}"
            else:
                # Improved Start Menu shortcut search
                import fnmatch
                start_menu_dirs = [
                    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
                    os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs")
                ]
                found = False
                for dir in start_menu_dirs:
                    for root, dirs, files in os.walk(dir):
                        for file in files:
                            if file.lower().endswith('.lnk') and app_name in file.lower():
                                shortcut_path = os.path.join(root, file)
                                try:
                                    os.startfile(shortcut_path)
                                    reply = f"Opening {file[:-4]}!"
                                    found = True
                                    break
                                except Exception as e:
                                    reply = f"Sorry, I couldn't open {file[:-4]}. Error: {e}"
                                    found = True
                                    break
                        if found:
                            break
                    if found:
                        break
                if not found:
                    reply = f"Sorry, I couldn't find {app_name} installed on your system."
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)
            continue

        # Find closest command
        matched_command = find_command(text, commands)

        if matched_command:
            reply = commands[matched_command]
            print(f"🤖 Buddy: {reply}")
            speak_with_polly(reply)

    except KeyboardInterrupt:
        print("\n👋 Exiting Buddy...")
        break
    except Exception as e:
        print("❌ Error:", e)
