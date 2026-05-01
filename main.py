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

class ProVoiceApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#0A0E14')
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Header
        self.header = Label(text="PRO VOICE GENERATOR", font_size='28sp', bold=True, 
                            color=get_color_from_hex('#00B4D8'), size_hint=(1, 0.1))
        
        # Input Area
        self.text_input = TextInput(hint_text="Enter text to convert to voice...", multiline=True,
                                    size_hint=(1, 0.4), font_size='18sp', background_color=(1, 1, 1, 0.9))
        
        # Professional Progress Bar
        self.progress = ProgressBar(max=100, value=0, size_hint=(1, 0.1), opacity=0)
        
        # Action Button
        self.btn = Button(text="GENERATE & SAVE AUDIO", size_hint=(1, 0.15), bold=True,
                          background_normal='', background_color=get_color_from_hex('#0077B6'))
        self.btn.bind(on_press=self.start_process)
        
        self.status = Label(text="Status: Ready", font_size='14sp', color=(0.5, 0.5, 0.5, 1))

        self.layout.add_widget(self.header)
        self.layout.add_widget(self.text_input)
        self.layout.add_widget(self.progress)
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.status)
        
        return self.layout

    def start_process(self, instance):
        content = self.text_input.text.strip()
        if content:
            self.btn.disabled = True
            self.progress.opacity = 1
            self.status.text = "Initializing Engine..."
            # Background thread taake UI freeze na ho
            threading.Thread(target=self.run_engine, args=(content,)).start()

    def run_engine(self, text):
        try:
            # Step 1: Processing
            Clock.schedule_once(lambda dt: self.update_status("Converting Text...", 30))
            tts = gTTS(text=text, lang='en')
            
            # Step 2: Saving File
            Clock.schedule_once(lambda dt: self.update_status("Saving to Storage...", 70))
            filename = "generated_voice.mp3"
            tts.save(filename)
            
            # Step 3: Done
            Clock.schedule_once(lambda dt: self.finalize(filename))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.handle_error(str(e)))

    def update_status(self, msg, val):
        self.status.text = f"Status: {msg}"
        self.progress.value = val

    def finalize(self, filename):
        self.progress.value = 100
        self.status.text = f"Success! Saved as {filename}"
        self.btn.disabled = False
        # Audio automatically play karne ke liye
        os.system(f"termux-media-player play {filename}")

    def handle_error(self, err):
        self.status.text = "Error: Check Connection"
        self.btn.disabled = False
        self.progress.value = 0

if __name__ == '__main__':
    ProVoiceApp().run()
