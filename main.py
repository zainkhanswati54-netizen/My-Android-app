from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from android.permissions import request_permissions, Permission
import threading
from gtts import gTTS
import os

# App ka background color set kar rahe hain
Window.clearcolor = (0.05, 0.05, 0.1, 1)

class ProVoiceStudio(App):
    def build(self):
        # Android Permission Request
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.INTERNET])
        
        self.sound = None
        self.last_pos = 0
        
        # Main Layout
        self.main_layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # Header Section
        self.header = Label(text="PRO AI VOICE ENGINE", font_size='26sp', bold=True, color=(0, 0.7, 1, 1), size_hint_y=0.1)
        self.main_layout.add_widget(self.header)

        # Text Input Area
        self.txt_input = TextInput(
            hint_text="Apna message yahan type karein...",
            multiline=True,
            size_hint_y=0.35,
            background_color=(0.1, 0.1, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='18sp',
            cursor_color=(0, 0.7, 1, 1)
        )
        self.main_layout.add_widget(self.txt_input)

        # Settings Section (Sliders for Voice)
        settings_box = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=5)
        
        settings_box.add_widget(Label(text="Voice Speed Control", font_size='14sp', color=(0.8, 0.8, 0.8, 1)))
        self.speed_slider = Slider(min=0.5, max=2.0, value=1.0, step=0.1)
        settings_box.add_widget(self.speed_slider)
        
        self.main_layout.add_widget(settings_box)

        # Progress and Status
        self.status_label = Label(text="System: Waiting for command", font_size='14sp', size_hint_y=0.05)
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=0.05)
        self.main_layout.add_widget(self.status_label)
        self.main_layout.add_widget(self.progress_bar)

        # Playback Controls
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        self.play_btn = Button(text="PLAY / PAUSE", on_press=self.toggle_voice, disabled=True, background_color=(0.2, 0.6, 0.2, 1))
        self.stop_btn = Button(text="STOP", on_press=self.stop_voice, disabled=True, background_color=(0.8, 0.2, 0.2, 1))
        btn_layout.add_widget(self.play_btn)
        btn_layout.add_widget(self.stop_btn)
        self.main_layout.add_widget(btn_layout)

        # Main Action Button
        self.generate_btn = Button(
            text="GENERATE & SAVE AUDIO",
            size_hint_y=0.15,
            bold=True,
            font_size='20sp',
            background_color=(0, 0.4, 0.9, 1)
        )
        self.generate_btn.bind(on_press=self.start_conversion)
        self.main_layout.add_widget(self.generate_btn)

        return self.main_layout

    def start_conversion(self, instance):
        if self.txt_input.text.strip():
            self.generate_btn.disabled = True
            self.update_ui(25, "Status: Connecting to AI Server...")
            threading.Thread(target=self.process_voice).start()

    def process_voice(self):
        try:
            # Use internal path to avoid "No such file" errors
            audio_path = os.path.join(self.user_data_dir, "studio_output.mp3")
            
            Clock.schedule_once(lambda dt: self.update_ui(60, "Status: Synthesizing Voice..."))
            tts = gTTS(text=self.txt_input.text, lang='en', slow=(self.speed_slider.value < 1.0))
            tts.save(audio_path)
            
            Clock.schedule_once(lambda dt: self.load_audio_file(audio_path))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.handle_error(str(e)))

    def update_ui(self, val, msg):
        self.progress_bar.value = val
        self.status_label.text = msg

    def load_audio_file(self, path):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(path)
        if self.sound:
            self.update_ui(100, "Status: Voice Engine Ready!")
            self.play_btn.disabled = False
            self.stop_btn.disabled = False
        else:
            self.status_label.text = "Error: Audio Driver not found"
        self.generate_btn.disabled = False

    def toggle_voice(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.last_pos = self.sound.get_pos()
                self.sound.stop()
                self.status_label.text = "Status: Paused"
            else:
                self.sound.play()
                if self.last_pos > 0: self.sound.seek(self.last_pos)
                self.status_label.text = "Status: Playing..."

    def stop_voice(self, instance):
        if self.sound:
            self.sound.stop()
            self.last_pos = 0
            self.status_label.text = "Status: Stopped"

    def handle_error(self, error):
        self.status_label.text = f"Error: {error[:30]}"
        self.generate_btn.disabled = False
        self.progress_bar.value = 0

if __name__ == '__main__':
    ProVoiceStudio().run()
