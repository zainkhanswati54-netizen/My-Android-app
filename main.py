from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import threading
from gtts import gTTS
import os

class VoiceBotPro(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#0A0E14')
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Header
        header = Label(text="AI VOICE ENGINE", font_size='32sp', bold=True, 
                       color=get_color_from_hex('#00B4D8'), size_hint=(1, 0.1))
        
        # Input
        self.input_text = TextInput(hint_text="Enter text (Small or Large)...", multiline=True,
                                    size_hint=(1, 0.4), font_size='18sp', padding=[15, 15])
        
        # Progress Bar (Initially Hidden)
        self.progress = ProgressBar(max=100, value=0, size_hint=(1, 0.05))
        
        # Action Button
        self.btn = Button(text="GENERATE AUDIO", size_hint=(1, 0.15), bold=True,
                          background_normal='', background_color=get_color_from_hex('#0077B6'))
        self.btn.bind(on_press=self.start_generation)
        
        self.status = Label(text="System Ready", font_size='14sp', color=(0.4, 0.4, 0.4, 1))

        layout.add_widget(header)
        layout.add_widget(self.input_text)
        layout.add_widget(self.progress)
        layout.add_widget(self.btn)
        layout.add_widget(self.status)
        
        return layout

    def start_generation(self, instance):
        if self.input_text.text.strip():
            self.btn.disabled = True
            self.status.text = "Processing Audio..."
            self.progress.value = 10
            # Background thread taake app crash na ho
            threading.Thread(target=self.generate_audio_thread).start()

    def generate_audio_thread(self):
        try:
            text = self.input_text.text
            tts = gTTS(text=text, lang='en')
            Clock.schedule_once(lambda dt: setattr(self.progress, 'value', 50))
            
            filename = "output.mp3"
            tts.save(filename)
            
            Clock.schedule_once(lambda dt: self.finish_generation(filename))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.error_handler())

    def finish_generation(self, filename):
        self.progress.value = 100
        self.status.text = "Success: Audio Ready!"
        self.btn.disabled = False
        # Yahan hum audio play karne ka command dal sakte hain
        os.system(f"termux-media-player play {filename}") 

    def error_handler(self):
        self.status.text = "Error: Check Internet"
        self.btn.disabled = False
        self.progress.value = 0
