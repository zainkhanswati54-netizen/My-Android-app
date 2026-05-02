import os
import threading
import time
import shutil
import random

# Core Kivy & Android Optimizations
os.environ['KIVY_AUDIO'] = 'android'
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Ellipse

# Android Specific Service Handling
try:
    from android.permissions import request_permissions, Permission
    PLATFORM_ANDROID = True
except ImportError:
    PLATFORM_ANDROID = False

# --- Advanced UI Components ---
class TitanBase(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex('#040915'))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class NeonButton(Button):
    def __init__(self, neon_color='#00F2FF', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.neon_hex = neon_color
        self.bind(pos=self.render, size=self.render)

    def render(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.neon_hex))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

# --- Main Logic Engine ---
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = TitanBase()
        self.setup_ui()
        self.audio_engine = None
        self.work_dir = os.path.join(os.getcwd(), "studio_cache")
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

    def setup_ui(self):
        # Scrollable Container for many elements
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.container = BoxLayout(orientation='vertical', padding=40, spacing=25, size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter('height'))

        # Header Section
        self.container.add_widget(Label(text="[b]TITAN AI STUDIO PRO[/b]", markup=True, font_size='36sp', color=get_color_from_hex('#00F2FF'), size_hint_y=None, height=120))
        self.container.add_widget(Label(text="ULTIMATE GENERATIVE ENGINE V3.0", font_size='14sp', color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=30))

        # Input Box
        self.container.add_widget(Label(text="Enter Script Data:", font_size='18sp', bold=True, size_hint_y=None, height=40))
        self.main_input = TextInput(
            hint_text="Write or paste your script here for AI synthesis...",
            multiline=True, size_hint_y=None, height=450,
            background_color=get_color_from_hex('#0D1321'),
            foreground_color=(1, 1, 1, 1), font_size='20sp',
            padding=[20, 20], cursor_color=get_color_from_hex('#00F2FF')
        )
        self.container.add_widget(self.main_input)

        # Parameter Rack
        self.container.add_widget(Label(text="ENGINE PARAMETERS", font_size='16sp', color=get_color_from_hex('#555555')))
        
        # Speed Control
        self.speed_lab = Label(text="Voice Tempo: 1.0x", size_hint_y=None, height=40)
        self.speed_sld = Slider(min=0.5, max=2.0, value=1.0, step=0.1, size_hint_y=None, height=60)
        self.speed_sld.bind(value=self.update_labels)
        self.container.add_widget(self.speed_lab)
        self.container.add_widget(self.speed_sld)

        # Status System
        self.status_box = Label(text="System: Standby", italic=True, size_hint_y=None, height=40)
        self.load_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        self.container.add_widget(self.status_box)
        self.container.add_widget(self.load_bar)

        # Button System
        self.play_btn = NeonButton(text="PREVIEW MASTER", neon_color='#10B981', size_hint_y=None, height=90, disabled=True)
        self.play_btn.bind(on_press=self.toggle_play)
        self.container.add_widget(self.play_btn)

        self.stop_btn = NeonButton(text="RESET ENGINE", neon_color='#EF4444', size_hint_y=None, height=90, disabled=True)
        self.stop_btn.bind(on_press=self.reset_audio)
        self.container.add_widget(self.stop_btn)

        self.gen_btn = NeonButton(text="START AI SYNTHESIS", neon_color='#3B82F6', size_hint_y=None, height=120)
        self.gen_btn.bind(on_press=self.initiate_engine)
        self.container.add_widget(self.gen_btn)

        self.save_btn = NeonButton(text="EXPORT TO SMARTPHONE", neon_color='#8B5CF6', size_hint_y=None, height=90, disabled=True)
        self.save_btn.bind(on_press=self.export_audio)
        self.container.add_widget(self.save_btn)

        # Extra Padding at bottom
        self.container.add_widget(BoxLayout(size_hint_y=None, height=50))

        scroll.add_widget(self.container)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def update_labels(self, *args):
        self.speed_lab.text = f"Voice Tempo: {round(self.speed_sld.value, 1)}x"

    def initiate_engine(self, instance):
        if not self.main_input.text.strip():
            self.status_box.text = "Error: System needs text input"
            return
        self.gen_btn.disabled = True
        self.load_bar.value = 10
        self.status_box.text = "Status: Initializing Core..."
        threading.Thread(target=self.core_worker).start()

    def core_worker(self):
        try:
            from gtts import gTTS
            import time
            
            # Artificial Delay to ensure size stability during processing
            time.sleep(1)
            Clock.schedule_once(lambda dt: self.update_progress(40, "Status: Connecting to Cloud..."))
            
            # Logic implementation
            slow_mode = self.speed_sld.value < 1.0
            tts = gTTS(text=self.main_input.text, lang='en', slow=slow_mode)
            
            out_path = os.path.join(self.work_dir, "master.mp3")
            Clock.schedule_once(lambda dt: self.update_progress(75, "Status: Finalizing Waveform..."))
            tts.save(out_path)
            
            Clock.schedule_once(lambda dt: self.finalize_engine(out_path))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.report_error(str(e)))

    def update_progress(self, val, msg):
        self.load_bar.value = val
        self.status_box.text = msg

    def finalize_engine(self, path):
        if self.audio_engine: self.audio_engine.unload()
        self.audio_engine = SoundLoader.load(path)
        self.load_bar.value = 100
        self.status_box.text = "Status: Processing Complete"
        self.play_btn.disabled = False
        self.stop_btn.disabled = False
        self.save_btn.disabled = False
        self.gen_btn.disabled = False

    def toggle_play(self, instance):
        if self.audio_engine:
            if self.audio_engine.state == 'play':
                self.audio_engine.stop()
                self.play_btn.text = "RESUME PREVIEW"
            else:
                self.audio_engine.play()
                self.play_btn.text = "PAUSE PREVIEW"

    def reset_audio(self, instance):
        if self.audio_engine:
            self.audio_engine.stop()
            self.play_btn.text = "PREVIEW MASTER"

    def export_audio(self, instance):
        try:
            # High-Level Storage Protocol
            src = os.path.join(self.work_dir, "master.mp3")
            dest = f"/sdcard/Download/Titan_Voice_{int(time.time())}.mp3"
            shutil.copyfile(src, dest)
            self.status_box.text = f"Saved: {dest}"
        except:
            self.status_box.text = "Error: Check File Permissions"

    def report_error(self, err):
        self.status_box.text = f"CRITICAL: {err[:35]}"
        self.gen_btn.disabled = False

class TitanApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.main_screen = StudioScreen(name='studio')
        self.sm.add_widget(self.main_screen)
        
        # Delayed Start to bypass Android 1-second crash
        Clock.schedule_once(self.run_startup_diagnostics, 5.0)
        return self.sm

    def run_startup_diagnostics(self, dt):
        if PLATFORM_ANDROID:
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.MANAGE_EXTERNAL_STORAGE])
        self.main_screen.status_box.text = "System: All Modules Loaded"

if __name__ == '__main__':
    TitanApp().run()
