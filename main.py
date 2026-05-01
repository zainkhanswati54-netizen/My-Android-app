from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import threading
from gtts import gTTS
import os

class ProVoiceApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#0A0E14')
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        self.sound = None
        
        # Header
        self.layout.add_widget(Label(text="PRO VOICE GENERATOR", font_size='28sp', bold=True, 
                                     color=get_color_from_hex('#00B4D8'), size_hint=(1, 0.1)))
        
        # Input
        self.text_input = TextInput(hint_text="Enter text...", multiline=True,
                                    size_hint=(1, 0.3), font_size='18sp')
        self.layout.add_widget(self.text_input)
        
        # Progress & Info
        self.progress = ProgressBar(max=100, value=0, size_hint=(1, 0.05))
        self.status = Label(text="Status: Ready", font_size='14sp', color=(0.5, 0.5, 0.5, 1))
        self.duration_label = Label(text="Duration: 00:00", font_size='14sp')
        
        self.layout.add_widget(self.progress)
        self.layout.add_widget(self.status)
        self.layout.add_widget(self.duration_label)
        
        # Audio Controls
        ctrl_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.play_btn = Button(text="PLAY", on_press=self.play_audio, disabled=True)
        self.stop_btn = Button(text="STOP", on_press=self.stop_audio, disabled=True)
        ctrl_layout.add_widget(self.play_btn)
        ctrl_layout.add_widget(self.stop_btn)
        self.layout.add_widget(ctrl_layout)
        
        # Generate Button
        self.gen_btn = Button(text="GENERATE AUDIO", size_hint=(1, 0.15), bold=True,
                              background_color=get_color_from_hex('#0077B6'))
        self.gen_btn.bind(on_press=self.start_process)
        self.layout.add_widget(self.gen_btn)
        
        return self.layout

    def start_process(self, instance):
        content = self.text_input.text.strip()
        if content:
            self.gen_btn.disabled = True
            self.status.text = "Converting..."
            threading.Thread(target=self.run_engine, args=(content,)).start()

    def run_engine(self, text):
        try:
            filename = "generated_voice.mp3"
            tts = gTTS(text=text, lang='en')
            tts.save(filename)
            Clock.schedule_once(lambda dt: self.finalize(filename))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.handle_error())

    def finalize(self, filename):
        self.status.text = f"Saved: {filename}"
        self.gen_btn.disabled = False
        self.sound = SoundLoader.load(filename)
        if self.sound:
            # Duration calculate karna
            mins, secs = divmod(int(self.sound.length), 60)
            self.duration_label.text = f"Duration: {mins:02d}:{secs:02d}"
            self.play_btn.disabled = False
            self.stop_btn.disabled = False

    def play_audio(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.sound.stop()
                self.play_btn.text = "PLAY"
            else:
                self.sound.play()
                self.play_btn.text = "PAUSE"

    def stop_audio(self, instance):
        if self.sound:
            self.sound.stop()
            self.play_btn.text = "PLAY"

    def handle_error(self):
        self.status.text = "Error in Generation"
        self.gen_btn.disabled = False
