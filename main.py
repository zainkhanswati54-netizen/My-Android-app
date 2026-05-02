import os
import threading
import time
import shutil

# Kivy configurations to prevent startup crashes
os.environ['KIVY_AUDIO'] = 'android' 

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle

# --- Safety Check for Android ---
try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except ImportError:
    ANDROID = False

# --- Custom UI Elements ---
class StyledButton(Button):
    def __init__(self, bg_color='#0078D7', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color_hex = bg_color
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.color_hex))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

class VoiceStudioPro(App):
    def build(self):
        # 1. Base Setup
        self.title = "AI Voice Studio Elite"
        Window.clearcolor = get_color_from_hex('#0A0E14')
        self.sound = None
        self.is_generating = False
        self.temp_path = os.path.join(self.user_data_dir, "output_audio.mp3")
        
        # 2. Layout Structure
        self.root_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Scrollable Content
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20, padding=[10, 20])
        content.bind(minimum_height=content.setter('height'))

        # Header
        header = Label(
            text="[b]AI VOICE STUDIO ELITE[/b]", 
            markup=True, font_size='32sp', 
            color=get_color_from_hex('#00CCFF'),
            size_hint_y=None, height=100
        )
        content.add_widget(header)

        # Text Area
        content.add_widget(Label(text="Input Script:", size_hint_y=None, height=40, halign='left'))
        self.text_input = TextInput(
            hint_text="Write your script here...",
            multiline=True, size_hint_y=None, height=400,
            background_color=get_color_from_hex('#1A1F26'),
            foreground_color=(1, 1, 1, 1),
            cursor_color=get_color_from_hex('#00CCFF'),
            font_size='18sp', padding=[15, 15]
        )
        content.add_widget(self.text_input)

        # Control Panel (Grid)
        controls = GridLayout(cols=1, spacing=15, size_hint_y=None, height=250)
        
        # Speed Slider
        self.speed_label = Label(text="Voice Speed: 1.0x (Normal)", color=get_color_from_hex('#BBBBBB'))
        self.speed_slider = Slider(min=0.5, max=2.0, value=1.0, step=0.1)
        self.speed_slider.bind(value=self.update_speed_text)
        
        controls.add_widget(self.speed_label)
        controls.add_widget(self.speed_slider)
        
        # Progress Tracking
        self.status_label = Label(text="Status: System Idle", font_size='14sp', color=(0.5, 0.5, 0.5, 1))
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        controls.add_widget(self.status_label)
        controls.add_widget(self.progress_bar)
        
        content.add_widget(controls)

        # Playback Buttons
        play_box = BoxLayout(size_hint_y=None, height=80, spacing=15)
        self.btn_play = StyledButton(text="PLAY PREVIEW", bg_color='#28A745', disabled=True)
        self.btn_play.bind(on_press=self.play_audio)
        self.btn_stop = StyledButton(text="STOP", bg_color='#DC3545', disabled=True)
        self.btn_stop.bind(on_press=self.stop_audio)
        play_box.add_widget(self.btn_play)
        play_box.add_widget(self.btn_stop)
        content.add_widget(play_box)

        # Action Buttons
        self.btn_gen = StyledButton(text="GENERATE VOICE", bg_color='#0078D7', height=100, size_hint_y=None)
        self.btn_gen.bind(on_press=self.start_voice_thread)
        content.add_widget(self.btn_gen)

        self.btn_export = StyledButton(text="SAVE TO DOWNLOADS", bg_color='#6F42C1', height=80, size_hint_y=None, disabled=True)
        self.btn_export.bind(on_press=self.export_to_phone)
        content.add_widget(self.btn_export)

        scroll.add_widget(content)
        self.root_layout.add_widget(scroll)

        # Final Initialization delay to prevent crash
        Clock.schedule_once(self.late_init, 1.0)
        
        return self.root_layout

    def update_speed_text(self, instance, value):
        self.speed_label.text = f"Voice Speed: {round(value, 1)}x"

    def late_init(self, dt):
        if ANDROID:
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        self.status_label.text = "Status: Ready"

    def start_voice_thread(self, instance):
        if not self.text_input.text.strip():
            self.status_label.text = "Status: Error - Text Empty!"
            return
        
        self.is_generating = True
        self.btn_gen.disabled = True
        self.progress_bar.value = 10
        self.status_label.text = "Status: Initializing AI..."
        threading.Thread(target=self.generate_voice_logic).start()

    def generate_voice_logic(self):
        try:
            from gtts import gTTS
            Clock.schedule_once(lambda dt: self.update_ui(40, "Status: Synthesizing..."))
            
            # Speed logic: slow if slider < 1.0
            tts = gTTS(text=self.text_input.text, lang='en', slow=(self.speed_slider.value < 1.0))
            
            Clock.schedule_once(lambda dt: self.update_ui(70, "Status: Saving Audio..."))
            tts.save(self.temp_path)
            
            Clock.schedule_once(lambda dt: self.finish_generation())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.handle_error(str(e)))

    def update_ui(self, progress, status):
        self.progress_bar.value = progress
        self.status_label.text = status

    def finish_generation(self):
        if self.sound: self.sound.unload()
        self.sound = SoundLoader.load(self.temp_path)
        
        self.progress_bar.value = 100
        self.status_label.text = "Status: Voice Ready!"
        self.btn_play.disabled = False
        self.btn_stop.disabled = False
        self.btn_export.disabled = False
        self.btn_gen.disabled = False

    def play_audio(self, instance):
        if self.sound:
            if self.sound.state == 'play':
                self.sound.stop()
                self.btn_play.text = "PLAY PREVIEW"
            else:
                self.sound.play()
                self.btn_play.text = "PAUSE"

    def stop_audio(self, instance):
        if self.sound:
            self.sound.stop()
            self.btn_play.text = "PLAY PREVIEW"

    def export_to_phone(self, instance):
        try:
            # Standard Download Path
            target = "/sdcard/Download/AI_Voice_Studio.mp3"
            shutil.copyfile(self.temp_path, target)
            self.status_label.text = f"Status: Exported to {target}"
        except Exception as e:
            self.status_label.text = f"Status: Export Failed - {str(e)[:20]}"

    def handle_error(self, err):
        self.status_label.text = f"CRITICAL ERROR: {err[:50]}"
        self.btn_gen.disabled = False
        self.progress_bar.value = 0

if __name__ == '__main__':
    try:
        VoiceStudioPro().run()
    except Exception as e:
        print(f"App level crash: {e}")
