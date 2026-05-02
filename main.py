from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from android.permissions import request_permissions, Permission
import threading
from gtts import gTTS
import os
import shutil

class ProVoiceStudio(App):
    def build(self):
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        
        self.sound = None
        self.temp_path = os.path.join(self.user_data_dir, "preview.mp3")
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        layout.add_widget(Label(text="PRO AI VOICE ENGINE", font_size='24sp', bold=True, color=(0, 0.7, 1, 1)))
        
        # Text Input
        self.txt = TextInput(hint_text="Type here...", multiline=True, size_hint_y=0.3)
        layout.add_widget(self.txt)

        # 1. Speed Control with Labels
        speed_box = BoxLayout(orientation='vertical', size_hint_y=0.2)
        self.speed_label = Label(text="Voice Speed: 1.0x (Normal)")
        speed_box.add_widget(self.speed_label)
        
        self.speed_slider = Slider(min=0.5, max=2.0, value=1.0, step=0.1)
        self.speed_slider.bind(value=self.on_speed_change)
        speed_box.add_widget(self.speed_slider)
        layout.add_widget(speed_box)

        # 2. Duration & Status
        self.status = Label(text="Status: Ready", size_hint_y=0.1)
        layout.add_widget(self.status)

        # 3. Proper Playback Controls
        play_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        self.btn_p = Button(text="PLAY / PAUSE", on_press=self.toggle, disabled=True)
        self.btn_s = Button(text="STOP", on_press=self.stop, disabled=True)
        play_layout.add_widget(self.btn_p)
        play_layout.add_widget(self.btn_s)
        layout.add_widget(play_layout)

        # 4. Separate Download Button
        self.down_btn = Button(text="DOWNLOAD TO PHONE", size_hint_y=0.1, background_color=(0.1, 0.8, 0.3, 1), disabled=True)
        self.down_btn.bind(on_press=self.download_file)
        layout.add_widget(self.down_btn)

        # Generate Button
        self.gen_btn = Button(text="GENERATE PREVIEW", size_hint_y=0.15, background_color=(0, 0.4, 0.8, 1))
        self.gen_btn.bind(on_press=self.generate)
        layout.add_widget(self.gen_btn)
        
        return layout

    def on_speed_change(self, instance, value):
        self.speed_label.text = f"Voice Speed: {round(value, 1)}x"

    def generate(self, instance):
        if self.txt.text.strip():
            self.gen_btn.disabled = True
            self.status.text = "Generating..."
            threading.Thread(target=self.run_tts).start()

    def run_tts(self):
        try:
            # gTTS ki 'slow' property use kar rahe hain (Speed Logic)
            is_slow = self.speed_slider.value < 1.0
            tts = gTTS(text=self.txt.text, lang='en', slow=is_slow)
            tts.save(self.temp_path)
            Clock.schedule_once(lambda dt: self.finalize())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_status("Error: Connection Failed"))

    def finalize(self):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(self.temp_path)
        if self.sound:
            self.status.text = f"Ready! Duration: {int(self.sound.length)}s"
            self.btn_p.disabled = False
            self.btn_s.disabled = False
            self.down_btn.disabled = False
        self.gen_btn.disabled = False

    def toggle(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.sound.stop() # Pause logic ke liye seek handle karna hoga
                self.status.text = "Paused"
            else:
                self.sound.play()
                self.status.text = "Playing..."

    def stop(self, instance):
        if self.sound:
            self.sound.stop()
            self.status.text = "Stopped"

    def download_file(self, instance):
        try:
            # File ko internal cache se nikaal kar Downloads folder mein phenkna
            dest = "/sdcard/Download/AI_Voice_Export.mp3"
            shutil.copyfile(self.temp_path, dest)
            self.status.text = "Saved in Downloads!"
        except:
            self.status.text = "Permission Denied!"

    def set_status(self, msg):
        self.status.text = msg
        self.gen_btn.disabled = False
