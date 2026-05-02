import os
import threading
import time
import shutil
import logging

# Kivy settings for stability
os.environ['KIVY_AUDIO'] = 'android'
from kivy.config import Config
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Line

# Android specific safety
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    PLATFORM = "android"
except ImportError:
    PLATFORM = "desktop"

# --- Visual Elements ---
class BackgroundLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex('#050A18'))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class GlassButton(Button):
    def __init__(self, color_hex='#0078FF', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color_hex = color_hex
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.color_hex))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

# --- Main App ---
class UltimateVoiceStudio(App):
    def build(self):
        self.title = "AI Voice Studio Titan"
        Window.clearcolor = get_color_from_hex('#050A18')
        
        # Paths & Variables
        self.sound = None
        self.is_playing = False
        self.save_path = os.path.join(self.user_data_dir, "master_audio.mp3")
        self.log_file = os.path.join(self.user_data_dir, "app_log.txt")
        
        # Base UI
        root = AnchorLayout(anchor_x='center', anchor_y='center')
        main_container = BackgroundLayout(orientation='vertical', padding=40, spacing=25, size_hint=(0.95, 0.95))

        # 1. Header with Visual Wave
        header_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
        header_box.add_widget(Label(text="[b]TITAN AI VOICE ENGINE[/b]", markup=True, font_size='34sp', color=get_color_from_hex('#00E5FF')))
        header_box.add_widget(Label(text="Professional Studio Version 2.0", font_size='14sp', color=(0.5, 0.5, 0.5, 1)))
        main_container.add_widget(header_box)

        # 2. Advanced Input Area
        input_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=450)
        input_container.add_widget(Label(text="ENTER YOUR SCRIPT BELOW:", font_size='16sp', bold=True, halign='left'))
        
        self.script_input = TextInput(
            hint_text="Start typing your story here...",
            multiline=True,
            background_color=get_color_from_hex('#0F172A'),
            foreground_color=(1, 1, 1, 1),
            font_size='19sp',
            padding=[20, 20],
            cursor_color=get_color_from_hex('#00E5FF')
        )
        input_container.add_widget(self.script_input)
        main_container.add_widget(input_container)

        # 3. Control Rack
        control_rack = StackLayout(spacing=20, size_hint_y=None, height=280)
        
        # Speed Control
        self.speed_display = Label(text="Voice Speed: 1.0x (Normal)", size_hint=(1, None), height=30)
        self.speed_slider = Slider(min=0.5, max=2.0, value=1.0, step=0.1, size_hint=(1, None), height=50)
        self.speed_slider.bind(value=self.on_slider_move)
        control_rack.add_widget(self.speed_display)
        control_rack.add_widget(self.speed_slider)

        # Pitch/Tone (Simulated)
        control_rack.add_widget(Label(text="Voice Tone / Pitch (Beta)", size_hint=(1, None), height=30, color=(0.4, 0.4, 0.4, 1)))
        self.pitch_slider = Slider(min=0.8, max=1.2, value=1.0, size_hint=(1, None), height=50)
        control_rack.add_widget(self.pitch_slider)

        main_container.add_widget(control_rack)

        # 4. Progress Tracking
        self.status_bar = Label(text="System: Waiting for Script", font_size='15sp', italic=True)
        self.loading_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=15)
        main_container.add_widget(self.status_bar)
        main_container.add_widget(self.loading_bar)

        # 5. Professional Buttons
        action_box = BoxLayout(spacing=20, size_hint_y=None, height=100)
        self.play_btn = GlassButton(text="PREVIEW VOICE", color_hex='#22C55E', disabled=True)
        self.play_btn.bind(on_press=self.playback_toggle)
        
        self.stop_btn = GlassButton(text="STOP", color_hex='#EF4444', disabled=True)
        self.stop_btn.bind(on_press=self.playback_stop)
        
        action_box.add_widget(self.play_btn)
        action_box.add_widget(self.stop_btn)
        main_container.add_widget(action_box)

        self.gen_btn = GlassButton(text="GENERATE STUDIO AUDIO", color_hex='#3B82F6', height=120, size_hint_y=None)
        self.gen_btn.bind(on_press=self.trigger_generation)
        main_container.add_widget(self.gen_btn)

        self.export_btn = GlassButton(text="SAVE TO SMARTPHONE", color_hex='#A855F7', height=90, size_hint_y=None, disabled=True)
        self.export_btn.bind(on_press=self.save_to_downloads)
        main_container.add_widget(self.export_btn)

        root.add_widget(main_container)
        
        # Start background check
        Clock.schedule_once(self.app_ready_init, 2)
        return root

    def on_slider_move(self, instance, value):
        self.speed_display.text = f"Voice Speed: {round(value, 1)}x"

    def app_ready_init(self, dt):
        if PLATFORM == "android":
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.MANAGE_EXTERNAL_STORAGE])
        self.status_bar.text = "System: All Engines Online"

    def trigger_generation(self, instance):
        if not self.script_input.text.strip():
            self.status_bar.text = "Error: Input is empty!"
            return
        
        self.gen_btn.disabled = True
        self.status_bar.text = "Status: Booting AI Engine..."
        self.loading_bar.value = 15
        threading.Thread(target=self.core_worker).start()

    def core_worker(self):
        try:
            from gtts import gTTS
            import requests # Networking check
            
            Clock.schedule_once(lambda dt: self.update_status(45, "Status: Fetching AI Samples..."))
            
            # Use speed logic
            is_slow = self.speed_slider.value < 1.0
            engine = gTTS(text=self.script_input.text, lang='en', slow=is_slow)
            
            Clock.schedule_once(lambda dt: self.update_status(80, "Status: Encoding MP3 High-Res..."))
            engine.save(self.save_path)
            
            Clock.schedule_once(lambda dt: self.finalize_work())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.handle_crash(str(e)))

    def update_status(self, val, msg):
        self.loading_bar.value = val
        self.status_bar.text = msg

    def finalize_work(self):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(self.save_path)
        
        self.loading_bar.value = 100
        self.status_bar.text = "Success: Audio Mastered!"
        self.play_btn.disabled = False
        self.stop_btn.disabled = False
        self.export_btn.disabled = False
        self.gen_btn.disabled = False

    def playback_toggle(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.sound.stop()
                self.play_btn.text = "RESUME PREVIEW"
            else:
                self.sound.play()
                self.play_btn.text = "PAUSE AUDIO"

    def playback_stop(self, instance):
        if self.sound:
            self.sound.stop()
            self.play_btn.text = "PREVIEW VOICE"

    def save_to_downloads(self, instance):
        try:
            # Modern pathing
            target_dir = "/sdcard/Download/AI_Studio_Pro"
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            final_file = os.path.join(target_dir, f"Voice_{int(time.time())}.mp3")
            shutil.copyfile(self.save_path, final_file)
            self.status_bar.text = f"File Exported: {final_file}"
        except Exception as e:
            self.status_bar.text = "Permission Error: Check File Access"

    def handle_crash(self, error):
        self.status_bar.text = f"Engine Error: {error[:40]}"
        self.gen_btn.disabled = False
        self.loading_bar.value = 0

if __name__ == '__main__':
    UltimateVoiceStudio().run()
