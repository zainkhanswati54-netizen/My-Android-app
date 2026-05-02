from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import threading
from gtts import gTTS
import os

class VoicemakerApp(App):
    def build(self):
        self.sound = None
        self.last_pos = 0
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # UI jaise aapne Voicemaker ka mangi thi
        layout.add_widget(Label(text="AI VOICE STUDIO PRO", font_size='22sp', bold=True, color=(0, 0.6, 1, 1)))
        
        self.txt = TextInput(hint_text="Enter text here...", multiline=True, size_hint=(1, 0.4), font_size='18sp')
        layout.add_widget(self.txt)

        self.status = Label(text="System: Waiting for input", size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.bar = ProgressBar(max=100, value=0, size_hint=(1, 0.1), opacity=0)
        layout.add_widget(self.status)
        layout.add_widget(self.bar)

        # Controls
        ctrl_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.btn_p = Button(text="PLAY/PAUSE", on_press=self.toggle, disabled=True)
        self.btn_s = Button(text="STOP", on_press=self.stop, disabled=True)
        ctrl_layout.add_widget(self.btn_p)
        ctrl_layout.add_widget(self.btn_s)
        layout.add_widget(ctrl_layout)

        self.gen_btn = Button(text="CONVERT & SAVE", size_hint=(1, 0.2), background_color=(0, 0.5, 0.8, 1), bold=True)
        self.gen_btn.bind(on_press=self.start_work)
        layout.add_widget(self.gen_btn)
        
        return layout

    def start_work(self, instance):
        if self.txt.text.strip():
            self.gen_btn.disabled = True
            self.bar.opacity = 1
            self.status.text = "Status: Connecting to Server (20%)..."
            self.bar.value = 20
            threading.Thread(target=self.run_tts).start()

    def run_tts(self):
        try:
            # Internal storage use karenge taake permission ka masla shuru mein na aaye
            save_dir = self.user_data_dir
            path = os.path.join(save_dir, "voice.mp3")
            
            Clock.schedule_once(lambda dt: self.update_ui(50, "Generating Audio..."))
            tts = gTTS(text=self.txt.text, lang='en')
            tts.save(path)
            
            Clock.schedule_once(lambda dt: self.update_ui(90, "Loading Sound Driver..."))
            Clock.schedule_once(lambda dt: self.finalize(path))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.error_ui(str(e)))

    def update_ui(self, val, msg):
        self.bar.value = val
        self.status.text = f"Status: {msg}"

    def finalize(self, path):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(path)
        if self.sound:
            self.update_ui(100, "Ready! Voice Saved Internally")
            self.btn_p.disabled = False
            self.btn_s.disabled = False
        else:
            self.status.text = "Driver Error: Audio Not Supported"
        self.gen_btn.disabled = False

    def toggle(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.last_pos = self.sound.get_pos()
                self.sound.stop()
                self.btn_p.text = "RESUME"
            else:
                self.sound.play()
                if self.last_pos > 0: self.sound.seek(self.last_pos)
                self.btn_p.text = "PAUSE"

    def stop(self, instance):
        if self.sound:
            self.sound.stop()
            self.last_pos = 0
            self.btn_p.text = "PLAY"

    def error_ui(self, err):
        self.status.text = "Check Internet / Server Busy"
        self.gen_btn.disabled = False
        self.bar.opacity = 0
