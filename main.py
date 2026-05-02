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
        self.save_path = ""
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        # Header - Professional Look
        layout.add_widget(Label(text="PRO VOICE STUDIO", font_size='24sp', bold=True, color=(0, 0.7, 1, 1)))
        
        self.txt = TextInput(hint_text="Apna text yahan likhein...", multiline=True, size_hint=(1, 0.4))
        layout.add_widget(self.txt)

        # Progress Section (% Loading)
        self.progress_label = Label(text="System Ready: 0%", size_hint=(1, 0.05))
        self.bar = ProgressBar(max=100, value=0, size_hint=(1, 0.05))
        layout.add_widget(self.progress_label)
        layout.add_widget(self.bar)

        # Playback Controls (Play/Pause/Stop)
        ctrls = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.btn_play = Button(text="PLAY", on_press=self.toggle_audio, disabled=True)
        self.btn_stop = Button(text="STOP", on_press=self.stop_audio, disabled=True)
        ctrls.add_widget(self.btn_play)
        ctrls.add_widget(self.btn_stop)
        layout.add_widget(ctrls)

        # Convert Button
        self.gen_btn = Button(text="CONVERT TO SPEECH", size_hint=(1, 0.2), background_color=(0, 0.4, 0.8, 1), bold=True)
        self.gen_btn.bind(on_press=self.start_generation)
        layout.add_widget(self.gen_btn)

        return layout

    def start_generation(self, instance):
        if self.txt.text.strip():
            self.gen_btn.disabled = True
            self.btn_play.disabled = True
            self.update_progress(10, "Initializing...")
            threading.Thread(target=self.process_audio).start()

    def process_audio(self):
        try:
            Clock.schedule_once(lambda dt: self.update_progress(40, "Converting Text..."))
            tts = gTTS(text=self.txt.text, lang='en')
            
            Clock.schedule_once(lambda dt: self.update_progress(70, "Saving to Storage..."))
            # Internal app storage is safest to avoid immediate crashes
            self.save_path = os.path.join(self.user_data_dir, "voice_output.mp3")
            tts.save(self.save_path)
            
            Clock.schedule_once(lambda dt: self.load_audio())
        except:
            Clock.schedule_once(lambda dt: self.update_progress(0, "Error: Check Internet"))
            Clock.schedule_once(lambda dt: setattr(self.gen_btn, 'disabled', False))

    def update_progress(self, val, msg):
        self.bar.value = val
        self.progress_label.text = f"{msg} ({val}%)"

    def load_audio(self):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(self.save_path)
        if self.sound:
            self.update_progress(100, "Voice Ready!")
            self.btn_play.disabled = False
            self.btn_stop.disabled = False
        self.gen_btn.disabled = False

    def toggle_audio(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.last_pos = self.sound.get_pos()
                self.sound.stop()
                self.btn_play.text = "RESUME"
                self.progress_label.text = "Paused"
            else:
                self.sound.play()
                if self.last_pos > 0: self.sound.seek(self.last_pos)
                self.btn_play.text = "PAUSE"
                self.progress_label.text = "Playing..."

    def stop_audio(self, instance):
        if self.sound:
            self.sound.stop()
            self.last_pos = 0
            self.btn_play.text = "PLAY"
            self.progress_label.text = "Stopped"

if __name__ == '__main__':
    VoicemakerApp().run()
