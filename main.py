from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import os
import shutil

# Android specific imports ko try-except mein rakhein taake PC par bhi crash na ho
try:
    from android.permissions import request_permissions, Permission
except ImportError:
    request_permissions = None

class ProVoiceStudio(App):
    def build(self):
        self.sound = None
        self.temp_path = os.path.join(self.user_data_dir, "preview.mp3")
        
        # Main Layout ko simple rakhein start mein
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        self.layout.add_widget(Label(text="PRO AI VOICE ENGINE", font_size='24sp', bold=True, color=(0, 0.7, 1, 1)))
        
        # Text Input
        self.txt = TextInput(hint_text="Yahan likhein...", multiline=True, size_hint_y=0.3)
        self.layout.add_widget(self.txt)

        # Speed Control
        self.speed_label = Label(text="Voice Speed: 1.0x", size_hint_y=0.05)
        self.layout.add_widget(self.speed_label)
        self.speed_slider = Slider(min=0.5, max=2.0, value=1.0, step=0.1, size_hint_y=0.1)
        self.speed_slider.bind(value=self.on_speed_change)
        self.layout.add_widget(self.speed_slider)

        # Status
        self.status = Label(text="System: Loading...", size_hint_y=0.1)
        self.layout.add_widget(self.status)

        # Buttons
        self.gen_btn = Button(text="GENERATE PREVIEW", size_hint_y=0.15, background_color=(0, 0.4, 0.8, 1))
        self.gen_btn.bind(on_press=self.generate)
        self.layout.add_widget(self.gen_btn)

        # Permission ko 1 second baad maangein taake UI load ho jaye
        Clock.schedule_once(self.ask_permissions, 1)
        
        return self.layout

    def ask_permissions(self, dt):
        if request_permissions:
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        self.status.text = "System: Ready"

    def on_speed_change(self, instance, value):
        self.speed_label.text = f"Voice Speed: {round(value, 1)}x"

    def generate(self, instance):
        # Yahan threading use karein taake UI freeze na ho
        import threading
        self.status.text = "Generating..."
        threading.Thread(target=self.run_tts).start()

    def run_tts(self):
        from gtts import gTTS
        try:
            # Speed logic: gTTS sirf slow (True/False) samajhta hai
            tts = gTTS(text=self.txt.text, lang='en', slow=(self.speed_slider.value < 1.0))
            tts.save(self.temp_path)
            Clock.schedule_once(lambda dt: self.finalize())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_error(str(e)))

    def finalize(self):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(self.temp_path)
        if self.sound:
            self.status.text = f"Ready! Length: {int(self.sound.length)}s"
            self.sound.play() # Foran play karein check karne ke liye
        self.status.text = "Voice Engine Ready!"

    def set_error(self, err):
        self.status.text = f"Error: Check Internet"
