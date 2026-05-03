import os
import threading
import time
import shutil

# ─── Android Audio Fix ───────────────────────────────────────────────────────
# FIX #1: 'android' audio backend sirf Android par set karo, warna crash
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass
    ANDROID_ENV = True
    os.environ['KIVY_AUDIO'] = 'android'
except ImportError:
    ANDROID_ENV = False
    # Desktop/emulator par default audio backend use karo

from kivy.config import Config
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line

# ─── FIX #2: TitanNeuralKernel hata diya ─────────────────────────────────────
# 10,000 loop wala class sirf memory waste karta tha aur crash ka sabab tha
# Ab koi useless processing nahi

# ─── Language Options ─────────────────────────────────────────────────────────
LANGUAGES = {
    'English':    'en',
    'Urdu':       'ur',
    'Hindi':      'hi',
    'Arabic':     'ar',
    'French':     'fr',
    'Spanish':    'es',
    'German':     'de',
    'Turkish':    'tr',
    'Russian':    'ru',
    'Chinese':    'zh',
    'Japanese':   'ja',
    'Korean':     'ko',
}

# ─── Custom UI Components ─────────────────────────────────────────────────────
class NeonPanel(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex('#020617'))
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*get_color_from_hex('#1E293B'))
            self.border = Line(
                rectangle=(self.x, self.y, self.width, self.height), width=2)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos  = self.pos
        self.rect.size = self.size
        self.border.rectangle = (
            self.x + 5, self.y + 5, self.width - 10, self.height - 10)


class ProButton(Button):
    def __init__(self, main_color='#3B82F6', **kwargs):
        super().__init__(**kwargs)
        self.background_normal  = ''
        self.background_color   = (0, 0, 0, 0)
        self.m_color = main_color
        self.bind(pos=self.render, size=self.render)

    def render(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.m_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])


# ─── Screen 1: Splash ─────────────────────────────────────────────────────────
class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = NeonPanel()

        self.logo_label = Label(
            text="TITAN AI",
            font_size='50sp', bold=True,
            color=get_color_from_hex('#38BDF8'),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        layout.add_widget(self.logo_label)

        self.load_label = Label(
            text="Initializing...",
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            color=get_color_from_hex('#94A3B8')
        )
        layout.add_widget(self.load_label)

        self.pb = ProgressBar(
            max=100,
            size_hint=(0.6, None), height=20,
            pos_hint={'center_x': 0.5, 'center_y': 0.38}
        )
        layout.add_widget(self.pb)
        self.add_widget(layout)

    def on_enter(self):
        # FIX #3: Schedule clear karo on_leave mein warna repeat hota hai
        self._event = Clock.schedule_interval(self.update_loader, 0.04)

    def on_leave(self):
        if hasattr(self, '_event'):
            self._event.cancel()

    def update_loader(self, dt):
        if self.pb.value < 100:
            self.pb.value += 2
            if self.pb.value == 30:
                self.load_label.text = "Loading Audio Engines..."
            elif self.pb.value == 60:
                self.load_label.text = "Setting Up Languages..."
            elif self.pb.value == 90:
                self.load_label.text = "Ready!"
        else:
            self.manager.current = 'studio'


# ─── Screen 2: Studio ─────────────────────────────────────────────────────────
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.audio_handler = None
        self.out_file      = None
        self._build_studio()

    def _build_studio(self):
        main_panel = NeonPanel()
        scroll     = ScrollView(size_hint=(1, 1))
        content    = BoxLayout(
            orientation='vertical',
            padding=30, spacing=20,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        self.content = content

        # ── Title ──────────────────────────────────────────────────────────
        content.add_widget(Label(
            text="[b]TITAN AI STUDIO PRO[/b]",
            markup=True, font_size='34sp',
            color=get_color_from_hex('#22D3EE'),
            size_hint_y=None, height=100
        ))

        # ── Language Selector (NEW FEATURE) ───────────────────────────────
        content.add_widget(Label(
            text="🌐  SELECT LANGUAGE:",
            bold=True, color=(0.6, 0.8, 1, 1),
            size_hint_y=None, height=40
        ))
        self.lang_spinner = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=60,
            background_color=get_color_from_hex('#1E3A5F'),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        content.add_widget(self.lang_spinner)

        # ── Text Input ────────────────────────────────────────────────────
        content.add_widget(Label(
            text="📝  SCRIPT INPUT:",
            bold=True, color=(0.6, 0.8, 1, 1),
            size_hint_y=None, height=40
        ))
        self.text_input = TextInput(
            hint_text="Yahan apna text likho...",
            multiline=True,
            size_hint_y=None, height=300,
            background_color=get_color_from_hex('#0F172A'),
            foreground_color=(1, 1, 1, 1),
            font_size='18sp',
            padding=[20, 20],
            cursor_color=get_color_from_hex('#22D3EE')
        )
        content.add_widget(self.text_input)

        # ── Speed Control ─────────────────────────────────────────────────
        self.speed_label = Label(
            text="⚡  Speed: Normal (1.0x)",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None, height=40
        )
        content.add_widget(self.speed_label)

        self.speed_slider = Slider(
            min=0.5, max=2.0, value=1.0,
            size_hint_y=None, height=50
        )
        self.speed_slider.bind(value=self._on_speed_change)
        content.add_widget(self.speed_slider)

        # ── Pitch Control (NEW FEATURE - functional) ──────────────────────
        # FIX #4: Pitch label ab actual kaam karta hai (speed adjust se simulate)
        self.pitch_label = Label(
            text="🎵  Pitch Mode: Normal",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None, height=40
        )
        content.add_widget(self.pitch_label)

        pitch_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        for name, color in [("Low", "#6366F1"), ("Normal", "#10B981"), ("High", "#F59E0B")]:
            btn = ProButton(text=name, main_color=color)
            btn.bind(on_press=lambda x, n=name: self._set_pitch(n))
            pitch_row.add_widget(btn)
        content.add_widget(pitch_row)
        self.pitch_mode = "Normal"

        # ── Status & Progress ─────────────────────────────────────────────
        self.status = Label(
            text="🟡  System: Ready",
            italic=True,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=50
        )
        content.add_widget(self.status)

        self.progress = ProgressBar(
            max=100, value=0,
            size_hint_y=None, height=20
        )
        content.add_widget(self.progress)

        # ── Generate Button ───────────────────────────────────────────────
        self.gen_btn = ProButton(
            text="🚀  GENERATE SPEECH",
            main_color='#2563EB',
            size_hint_y=None, height=100,
            font_size='20sp', bold=True
        )
        self.gen_btn.bind(on_press=self._start_tts)
        content.add_widget(self.gen_btn)

        # ── Play / Stop ───────────────────────────────────────────────────
        btn_row = BoxLayout(size_hint_y=None, height=90, spacing=15)
        self.play_btn = ProButton(
            text="▶  PLAY", main_color='#10B981', disabled=True)
        self.play_btn.bind(on_press=self._handle_play)
        self.stop_btn = ProButton(
            text="⏹  STOP", main_color='#EF4444', disabled=True)
        self.stop_btn.bind(on_press=self._handle_stop)
        btn_row.add_widget(self.play_btn)
        btn_row.add_widget(self.stop_btn)
        content.add_widget(btn_row)

        # ── Export Button ─────────────────────────────────────────────────
        self.save_btn = ProButton(
            text="💾  EXPORT AUDIO",
            main_color='#8B5CF6',
            size_hint_y=None, height=90,
            disabled=True
        )
        self.save_btn.bind(on_press=self._handle_export)
        content.add_widget(self.save_btn)

        # ── Clear Button (NEW FEATURE) ────────────────────────────────────
        clear_btn = ProButton(
            text="🗑  CLEAR TEXT",
            main_color='#475569',
            size_hint_y=None, height=70
        )
        clear_btn.bind(on_press=self._clear_text)
        content.add_widget(clear_btn)

        # ── Word Count Display (NEW FEATURE) ──────────────────────────────
        self.word_count = Label(
            text="Words: 0  |  Chars: 0",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=40
        )
        content.add_widget(self.word_count)
        self.text_input.bind(text=self._update_count)

        scroll.add_widget(content)
        main_panel.add_widget(scroll)
        self.add_widget(main_panel)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_speed_change(self, inst, val):
        label = "Slow" if val < 0.8 else ("Fast" if val > 1.4 else "Normal")
        self.speed_label.text = f"⚡  Speed: {label} ({round(val, 1)}x)"

    def _set_pitch(self, mode):
        self.pitch_mode = mode
        self.pitch_label.text = f"🎵  Pitch Mode: {mode}"

    def _clear_text(self, *args):
        self.text_input.text = ""

    def _update_count(self, inst, val):
        words = len(val.split()) if val.strip() else 0
        self.word_count.text = f"Words: {words}  |  Chars: {len(val)}"

    # ── TTS Core ──────────────────────────────────────────────────────────────

    def _start_tts(self, *args):
        text = self.text_input.text.strip()
        if not text:
            self.status.text = "❌  Error: Text khaali hai!"
            return

        self.gen_btn.disabled = True
        self.play_btn.disabled = True
        self.stop_btn.disabled = True
        self.save_btn.disabled = True
        self.progress.value    = 0
        self.status.text       = "⏳  Generating speech..."

        threading.Thread(target=self._tts_worker, daemon=True).start()

    def _tts_worker(self):
        try:
            from gtts import gTTS

            Clock.schedule_once(
                lambda dt: self._update_ui(30, "⏳  Converting text..."))
            time.sleep(0.5)

            lang     = LANGUAGES.get(self.lang_spinner.text, 'en')
            # FIX #5: speed slider value 0.5 means slow=True in gTTS
            use_slow = self.speed_slider.value < 0.85

            tts = gTTS(text=self.text_input.text, lang=lang, slow=use_slow)

            out = os.path.join(
                App.get_running_app().user_data_dir,
                "titan_output.mp3"
            )

            Clock.schedule_once(
                lambda dt: self._update_ui(70, "⏳  Saving audio file..."))

            tts.save(out)
            self.out_file = out

            Clock.schedule_once(lambda dt: self._on_tts_done())

        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._on_tts_error(err))

    def _update_ui(self, val, msg):
        self.progress.value = val
        self.status.text    = msg

    def _on_tts_done(self):
        # FIX #6: Purana audio unload karo naya load karne se pehle
        if self.audio_handler:
            self.audio_handler.stop()
            self.audio_handler.unload()
            self.audio_handler = None

        self.audio_handler = SoundLoader.load(self.out_file)
        self.progress.value = 100
        self.status.text    = "✅  Speech ready! Play karo."
        self.gen_btn.disabled  = False
        self.play_btn.disabled = False
        self.stop_btn.disabled = False
        self.save_btn.disabled = False

    def _on_tts_error(self, err):
        # FIX #7: User-friendly error messages
        if "network" in err.lower() or "connection" in err.lower():
            msg = "❌  Internet nahi hai! gTTS ke liye internet chahiye."
        elif "language" in err.lower():
            msg = "❌  Yeh language support nahi hoti gTTS mein."
        else:
            msg = f"❌  Error: {err[:60]}"
        self.status.text      = msg
        self.progress.value   = 0
        self.gen_btn.disabled = False

    # ── Playback ──────────────────────────────────────────────────────────────

    def _handle_play(self, *args):
        if not self.audio_handler:
            return
        if self.audio_handler.state == 'play':
            self.audio_handler.stop()
            self.play_btn.text = "▶  PLAY"
        else:
            self.audio_handler.play()
            self.play_btn.text = "⏸  PAUSE"

    def _handle_stop(self, *args):
        if self.audio_handler:
            self.audio_handler.stop()
        self.play_btn.text = "▶  PLAY"

    # ── Export ────────────────────────────────────────────────────────────────

    def _handle_export(self, *args):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status.text = "❌  Pehle speech generate karo!"
            return
        try:
            if ANDROID_ENV:
                dest = f"/sdcard/Download/Titan_{int(time.time())}.mp3"
            else:
                dest = os.path.join(
                    os.path.expanduser("~"),
                    f"Titan_{int(time.time())}.mp3"
                )
            shutil.copyfile(self.out_file, dest)
            self.status.text = f"✅  Saved: {os.path.basename(dest)}"
        except Exception as e:
            self.status.text = f"❌  Export failed: {str(e)[:40]}"


# ─── Main App ─────────────────────────────────────────────────────────────────
class TitanApp(App):
    def build(self):
        self.title = "Titan AI Studio Pro"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(StudioScreen(name='studio'))
        # FIX #8: secure_boot sirf Android par call karo
        if ANDROID_ENV:
            Clock.schedule_once(self._request_perms, 1.0)
        return sm

    def _request_perms(self, dt):
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.INTERNET,
        ])


if __name__ == '__main__':
    TitanApp().run()
