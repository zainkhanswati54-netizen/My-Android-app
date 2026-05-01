from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import threading
from gtts import gTTS
import os

class ProVoiceApp(App):
    def build(self):
        self.sound = None
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        self.txt = TextInput(hint_text="Enter text...", size_hint=(1, 0.4))
        self.status = Label(text="Ready", size_hint=(1, 0.1))
        self.info = Label(text="Length: --", size_hint=(1, 0.1))
        
        # Controls
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        self.p_btn = Button(text="PLAY/PAUSE", on_press=self.toggle_audio, disabled=True)
        self.s_btn = Button(text="STOP", on_press=self.stop_audio, disabled=True)
        btn_layout.add_widget(self.p_btn)
        btn_layout.add_widget(self.s_btn)
        
        gen_btn = Button(text="GENERATE", size_hint=(1, 0.2), background_color=(0, 0.5, 0.8, 1))
        gen_btn.bind(on_press=self.generate)
        
        layout.add_widget(self.txt)
        layout.add_widget(self.status)
        layout.add_widget(self.info)
        layout.add_widget(btn_layout)
        layout.add_widget(gen_btn)
        return layout

    def generate(self, instance):
        self.status.text = "Processing..."
        threading.Thread(target=self.worker).start()

    def worker(self):
        try:
            path = "voice.mp3"
            tts = gTTS(text=self.txt.text, lang='en')
            tts.save(path)
            Clock.schedule_once(lambda dt: self.load_sound(path))
        except:
            Clock.schedule_once(lambda dt: setattr(self.status, 'text', "Internet Error!"))

    def load_sound(self, path):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(path)
        if self.sound:
            self.status.text = "Voice Ready!"
            self.info.text = f"Length: {int(self.sound.length)}s"
            self.p_btn.disabled = False
            self.s_btn.disabled = False
        else:
            self.status.text = "Audio Error (Try Again)"

    def toggle_audio(self, instance):
        if self.sound.state == 'play':
            self.sound.stop()
            self.p_btn.text = "PLAY"
        else:
            self.sound.play()
            self.p_btn.text = "PAUSE"

    def stop_audio(self, instance):
        if self.sound: self.sound.stop()
        self.p_btn.text = "PLAY"

if __name__ == '__main__':
    ProVoiceApp().run()
