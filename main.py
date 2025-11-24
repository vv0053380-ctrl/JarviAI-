from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
import threading
import json
import requests
import webbrowser
import os
import time
from gtts import gTTS
from kivy.core.audio import SoundLoader

# --- CONFIGURATION ---
API_KEY = "AIzaSyCR25wftYhpZWtV5R8OSRhpCLuQCRUoKwQ"
MEMORY_FILE = "jarvis_memory.json"

# --- ANDROID NATIVE ---
if platform == 'android':
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    CurrentActivity = cast('android.app.Activity', PythonActivity.mActivity)
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')

# --- KV DESIGN (HIGH TECH HUD) ---
KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: "main"
    MDFloatLayout:
        md_bg_color: 0, 0, 0, 1
        
        # Arc Reactor Background
        MDIconButton:
            icon: "robot"
            icon_size: "120sp"
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 0.8
            
        MDLabel:
            text: "JARVIS SYSTEM ACTIVE"
            halign: "center"
            pos_hint: {"top": 0.95}
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 1
            bold: True
            font_style: "H5"

        MDLabel:
            id: chat_display
            text: "Waiting for command..."
            halign: "center"
            pos_hint: {"center_y": 0.4}
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H6"
            size_hint_x: 0.9

        MDFloatingActionButton:
            icon: "microphone"
            icon_size: "40sp"
            md_bg_color: 1, 0, 0, 1
            pos_hint: {"center_x": 0.5, "y": 0.08}
            on_release: app.start_listening()
'''

class JarvisApp(MDApp):
    data = {"contacts": {}}

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def on_start(self):
        if platform == 'android':
            request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET, Permission.CALL_PHONE])
        self.load_memory()

    # --- MEMORY SYSTEM ---
    def load_memory(self):
        path = os.path.join(self.user_data_dir, MEMORY_FILE)
        if os.path.exists(path):
            with open(path, 'r') as f: self.data = json.load(f)
    
    def save_memory(self):
        path = os.path.join(self.user_data_dir, MEMORY_FILE)
        with open(path, 'w') as f: json.dump(self.data, f)

    # --- VOICE ENGINE ---
    def start_listening(self):
        if platform == 'android':
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "hi-IN")
            try: CurrentActivity.startActivityForResult(intent, 100)
            except: self.root.get_screen('main').ids.chat_display.text = "Mic Error"
        else:
            self.process_command("whatsapp par raj ko message karo hello bhai")

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 100:
            matches = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if matches and matches.size() > 0:
                text = matches.get(0)
                self.root.get_screen('main').ids.chat_display.text = f"You: {text}"
                self.process_command(text)

    # --- THE MASTER BRAIN ---
    def process_command(self, text):
        text = text.lower()
        
        # 1. WHATSAPP AUTOMATION (The Killer Feature)
        if "whatsapp" in text and "message" in text:
            self.handle_whatsapp(text)
            return

        # 2. CALLING SYSTEM
        if "call" in text:
            self.handle_call(text)
            return

        # 3. APP OPENER
        if "open youtube" in text:
            self.speak("Opening YouTube")
            webbrowser.open("https://youtube.com")
            return
        
        # 4. GEMINI AI (General)
        threading.Thread(target=self.ask_gemini, args=(text,)).start()

    # --- WHATSAPP HANDLER ---
    def handle_whatsapp(self, text):
        # Logic: "Whatsapp par [Name] ko message karo [Message]"
        words = text.split()
        try:
            # Extract Name (Simple Logic)
            name_index = words.index("par") + 1
            name = words[name_index]
            
            # Check if contact saved
            if name in self.data["contacts"]:
                number = self.data["contacts"][name]
                msg_start = text.find("bolo") + 5 # "Ko bolo" ke baad ka text
                if msg_start < 5: msg_start = text.find("karo") + 5
                
                message = text[msg_start:] if msg_start > 5 else "Hello"
                
                self.speak(f"Sending message to {name}")
                # WhatsApp API link opens App directly
                url = f"https://api.whatsapp.com/send?phone=+91{number}&text={message}"
                webbrowser.open(url)
            else:
                self.speak(f"{name} ka number save nahi hai. Please number bole.")
                # Yahan user se number lene ka logic add karna padega agle version mein
                # Abhi ke liye hum demo number use karenge ya user ko bolenge save karne
                self.root.get_screen('main').ids.chat_display.text = f"Save {name}'s number in memory first."
        except:
            self.speak("Command samajh nahi aaya.")

    def ask_gemini(self, text):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
            payload = {"contents": [{"parts": [{"text": text}]}]}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                reply = response.json()['candidates'][0]['content']['parts'][0]['text'].replace("*", "")
                Clock.schedule_once(lambda dt: self.update_ui(reply))
                self.speak(reply)
        except: pass

    def update_ui(self, text):
        self.root.get_screen('main').ids.chat_display.text = text

    def speak(self, text):
        threading.Thread(target=self._speak_thread, args=(text,)).start()

    def _speak_thread(self, text):
        try:
            path = os.path.join(self.user_data_dir, 'speech.mp3')
            if os.path.exists(path): os.remove(path)
            tts = gTTS(text=text[:200], lang='hi')
            tts.save(path)
            SoundLoader.load(path).play()
        except: pass

if __name__ == "__main__":
    if platform == 'android':
        from android import activity
        activity.bind(on_activity_result=JarvisApp().on_activity_result)
    JarvisApp().run()
