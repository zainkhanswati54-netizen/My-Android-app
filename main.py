from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform
import threading
from gtts import gTTS
import os

class ProVoiceApp(App):
    def build(self):
        self.sound = None
        self.last_pos = 0  # Pause position yaad rakhne ke liye
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        
        self.txt = TextInput(hint_text="Enter text here...", size_hint=(1, 0.3))
        
        # Loading Line (Progress Bar)
        self.loading_bar = ProgressBar(max=100, value=0, size_hint=(1, 0.05), opacity=0)
        self.status = Label(text="System Ready", size_hint=(1, 0.05))
        
        # Audio Info
        self.info = Label(text="Length: -- | Status: Stopped", size_hint=(1, 0.1))
        
        # Controls Layout
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.p_btn = Button(text="PLAY", on_press=self.toggle_audio, disabled=True)
        self.s_btn = Button(text="STOP", on_press=self.stop_audio, disabled=True)
        btn_layout.add_widget(self.p_btn)
        btn_layout.add_widget(self.s_btn)
        
        # Main Actions
        self.gen_btn = Button(text="GENERATE & SAVE", size_hint=(1, 0.15), background_color=(0, 0.4, 0.7, 1))
        self.gen_btn.bind(on_press=self.generate)
        
        layout.add_widget(self.txt)
        layout.add_widget(self.loading_bar)
        layout.add_widget(self.status)
        layout.add_widget(self.info)
        layout.add_widget(btn_layout)
        layout.add_widget(self.gen_btn)
        
        # Permissions request for Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            
        return layout

    def generate(self, instance):
        if self.txt.text.strip():
            self.gen_btn.disabled = True
            self.loading_bar.opacity = 1
            self.loading_bar.value = 20
            self.status.text = "Processing..."
            threading.Thread(target=self.worker).start()

    def worker(self):
        try:
            # Saving to a public folder for File Manager access
            save_path = "/sdcard/Download/VoiceGenerator_Output.mp3" if platform == 'android' else "voice.mp3"
            tts = gTTS(text=self.txt.text, lang='en')
            tts.save(save_path)
            Clock.schedule_once(lambda dt: self.load_sound(save_path))
        except:
            Clock.schedule_once(lambda dt: self.handle_error())

    def load_sound(self, path):
        self.loading_bar.value = 100
        self.status.text = "Voice Ready & Saved in Downloads!"
        self.sound = SoundLoader.load(path)
        if self.sound:
            self.info.text = f"Length: {int(self.sound.length)}s | Saved to Downloads"
            self.p_btn.disabled = False
            self.s_btn.disabled = False
        self.gen_btn.disabled = False

    def toggle_audio(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.last_pos = self.sound.get_pos() # Position save karna
                self.sound.stop()
                self.p_btn.text = "RESUME"
                self.info.text = f"Status: Paused at {int(self.last_pos)}s"
            else:
                self.sound.play()
                if self.last_pos > 0:
                    self.sound.seek(self.last_pos) # Wahi se shuru karna
                self.p_btn.text = "PAUSE"
                self.info.text = "Status: Playing"

    def stop_audio(self, instance):
        if self.sound:
            self.sound.stop()
            self.last_pos = 0
            self.p_btn.text = "PLAY"
            self.info.text = "Status: Stopped"

    def handle_error(self):
        self.status.text = "Error! Check Internet/Permissions"
        self.gen_btn.disabled = False
        self.loading_bar.opacity = 0
