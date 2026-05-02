from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import threading
import os
import shutil
import time

# Android specific imports with safety checks
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
except ImportError:
    request_permissions = None
    primary_external_storage_path = None

class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0.5, 0.8, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])

class ProVoiceStudio(App):
    def build(self):
        Window.clearcolor = (0.02, 0.02, 0.05, 1)
        self.title = "AI Voice Studio Pro"
        self.sound = None
        self.temp_file = os.path.join(self.user_data_dir, "last_voice.mp3")
        
        # Main Scroll Container
        root = ScrollView(size_hint=(1, 1))
        self.main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20, size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        # Header Section
        header = Label(text="ULTIMATE VOICE ENGINE", font_size='28sp', bold=True, color=(0, 0.8, 1, 1), size_hint_y=None, height=80)
        self.main_layout.add_widget(header)

        # Input Section
        self.main_layout.add_widget(Label(text="Enter Your Text Below:", size_hint_y=None, height=30, halign='left'))
        self.txt_input = TextInput(
            hint_text="Type something deep...",
            multiline=True,
            size_hint_y=None,
            height=300,
            background_color=(0.1, 0.1, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[15, 15]
        )
        self.main_layout.add_widget(self.txt_input)

        # Speed Controls
        speed_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=10)
        self.speed_label = Label(text="Playback Speed: 1.0x (Normal)", color=(0.7, 0.7, 0.7, 1))
        self.speed_slider = Slider(min=0.5, max=2.0, value=1.0, step=0.1)
        self.speed_slider.bind(value=self.on_speed_update)
        speed_box.add_widget(self.speed_label)
        speed_box.add_widget(self.speed_slider)
        
        # 1.5x 2.0x Labels
        label_box = BoxLayout(size_hint_y=None, height=20)
        label_box.add_widget(Label(text="0.5x", font_size='10sp'))
        label_box.add_widget(Label(text="1.0x", font_size='10sp'))
        label_box.add_widget(Label(text="2.0x", font_size='10sp'))
        speed_box.add_widget(label_box)
        self.main_layout.add_widget(speed_box)

        # Progress Bar
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        self.main_layout.add_widget(self.progress)
        
        self.status = Label(text="System Initialized", font_size='14sp', italic=True, size_hint_y=None, height=40)
        self.main_layout.add_widget(self.status)

        # Playback Controls
        ctrl_layout = BoxLayout(size_hint_y=None, height=80, spacing=15)
        self.play_btn = ModernButton(text="PLAY PREVIEW", disabled=True)
        self.play_btn.bind(on_press=self.toggle_audio)
        self.stop_btn = ModernButton(text="STOP", disabled=True)
        self.stop_btn.bind(on_press=self.stop_audio)
        ctrl_layout.add_widget(self.play_btn)
        ctrl_layout.add_widget(self.stop_btn)
        self.main_layout.add_widget(ctrl_layout)

        # Action Buttons
        self.gen_btn = ModernButton(text="GENERATE AI VOICE", size_hint_y=None, height=100)
        self.gen_btn.bind(on_press=self.start_generation)
        self.main_layout.add_widget(self.gen_btn)

        self.save_btn = ModernButton(text="EXPORT TO DOWNLOADS", size_hint_y=None, height=80, disabled=True)
        self.save_btn.bind(on_press=self.export_file)
        self.main_layout.add_widget(self.save_btn)

        root.add_widget(self.main_layout)
        
        # Delayed permissions for safety
        Clock.schedule_once(self.check_perms, 1.5)
        return root

    def on_speed_update(self, inst, val):
        self.speed_label.text = f"Playback Speed: {round(val, 1)}x"

    def check_perms(self, dt):
        if request_permissions:
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        self.status.text = "Status: Ready to work"

    def start_generation(self, instance):
        if not self.txt_input.text.strip():
            self.status.text = "Error: Input text is empty"
            return
        
        self.gen_btn.disabled = True
        self.status.text = "Status: Connecting to AI Engine..."
        self.progress.value = 20
        threading.Thread(target=self.process_voice).start()

    def process_voice(self):
        try:
            from gtts import gTTS
            # Logic for speed
            is_slow = self.speed_slider.value < 1.0
            tts = gTTS(text=self.txt_input.text, lang='en', slow=is_slow)
            
            Clock.schedule_once(lambda dt: self.update_progress(60, "Status: Writing Audio File..."))
            tts.save(self.temp_file)
            
            Clock.schedule_once(lambda dt: self.load_finished())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.report_crash(str(e)))

    def update_progress(self, val, msg):
        self.progress.value = val
        self.status.text = msg

    def load_finished(self):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(self.temp_file)
        if self.sound:
            self.update_progress(100, f"Ready! File size: {os.path.getsize(self.temp_file)//1024} KB")
            self.play_btn.disabled = False
            self.stop_btn.disabled = False
            self.save_btn.disabled = False
        else:
            self.status.text = "Error: Audio Driver Failure"
        self.gen_btn.disabled = False

    def toggle_audio(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.sound.stop()
                self.play_btn.text = "RESUME"
            else:
                self.sound.play()
                self.play_btn.text = "PAUSE"

    def stop_audio(self, instance):
        if self.sound:
            self.sound.stop()
            self.play_btn.text = "PLAY PREVIEW"

    def export_file(self, instance):
        try:
            # Fixing the path for modern Android
            export_path = "/sdcard/Download/AI_Studio_Voice.mp3"
            shutil.copyfile(self.temp_file, export_path)
            self.status.text = f"Saved: {export_path}"
        except Exception as e:
            self.status.text = "Permission Error: Check Settings"

    def report_crash(self, msg):
        self.status.text = f"CRASH PREVENTED: {msg[:50]}"
        self.gen_btn.disabled = False

if __name__ == '__main__':
    ProVoiceStudio().run()
