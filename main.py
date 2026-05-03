import os
import threading
import time
import shutil
import json

# ─── Android Detection ───────────────────────────────────────────────────────
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass
    ANDROID_ENV = True
    os.environ['KIVY_AUDIO'] = 'android'
except ImportError:
    ANDROID_ENV = False

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
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line

# ─── Language Options ─────────────────────────────────────────────────────────
LANGUAGES = {
    'English':  'en',
    'Urdu':     'ur',
    'Hindi':    'hi',
    'Arabic':   'ar',
    'French':   'fr',
    'Spanish':  'es',
    'German':   'de',
    'Turkish':  'tr',
    'Russian':  'ru',
    'Chinese':  'zh',
    'Japanese': 'ja',
    'Korean':   'ko',
}

# ─── Voice Profiles ───────────────────────────────────────────────────────────
# gTTS mein alag alag tld (server location) se voice character change hoti hai.
# Yeh proper male/female nahi hai lekin noticeable difference aata hai.
# Child = slow mode + uk accent (softer, lighter tone)
VOICE_PROFILES = {
    '👨 Male':    {'tld': 'com',    'slow': False},
    '👩 Female':  {'tld': 'com.au', 'slow': False},
    '🧒 Child':   {'tld': 'co.uk',  'slow': True },
    '🎙 News':    {'tld': 'ca',     'slow': False},
    '📻 Soft':    {'tld': 'co.in',  'slow': True },
}

# ─── Download History Helpers ─────────────────────────────────────────────────
def get_history_path():
    app = App.get_running_app()
    if app:
        return os.path.join(app.user_data_dir, "download_history.json")
    return "download_history.json"

def load_history():
    path = get_history_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_to_history(entry):
    history = load_history()
    history.insert(0, entry)
    history = history[:50]  # Max 50 records
    try:
        with open(get_history_path(), 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass

# ─── UI Helpers ───────────────────────────────────────────────────────────────
class NeonPanel(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex('#020617'))
            self.rect   = Rectangle(pos=self.pos, size=self.size)
            Color(*get_color_from_hex('#1E293B'))
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos   = self.pos
        self.rect.size  = self.size
        self.border.rectangle = (self.x+5, self.y+5, self.width-10, self.height-10)


class ProButton(Button):
    def __init__(self, main_color='#3B82F6', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color  = (0, 0, 0, 0)
        self.m_color = main_color
        self.bind(pos=self.render, size=self.render)

    def render(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.m_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])


# ─── Splash Screen ────────────────────────────────────────────────────────────
class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = NeonPanel()
        self.logo = Label(
            text="TITAN AI", font_size='50sp', bold=True,
            color=get_color_from_hex('#38BDF8'),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        layout.add_widget(self.logo)
        self.load_label = Label(
            text="Initializing...",
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            color=get_color_from_hex('#94A3B8')
        )
        layout.add_widget(self.load_label)
        self.pb = ProgressBar(
            max=100, size_hint=(0.6, None), height=20,
            pos_hint={'center_x': 0.5, 'center_y': 0.38}
        )
        layout.add_widget(self.pb)
        self.add_widget(layout)

    def on_enter(self):
        self._ev = Clock.schedule_interval(self._tick, 0.04)

    def on_leave(self):
        if hasattr(self, '_ev'):
            self._ev.cancel()

    def _tick(self, dt):
        if self.pb.value < 100:
            self.pb.value += 2
            if self.pb.value == 30:   self.load_label.text = "Loading Audio Engines..."
            elif self.pb.value == 60: self.load_label.text = "Loading Voice Profiles..."
            elif self.pb.value == 90: self.load_label.text = "Ready!"
        else:
            self.manager.current = 'studio'


# ─── History Screen ───────────────────────────────────────────────────────────
class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        panel = NeonPanel()
        outer = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Header
        header = BoxLayout(size_hint_y=None, height=70, spacing=10)
        back_btn = ProButton(text="← Back", main_color='#475569', size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'studio'))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text="[b]📂 Download History[/b]", markup=True,
            font_size='22sp', color=get_color_from_hex('#22D3EE')
        ))
        outer.add_widget(header)

        self.scroll = ScrollView()
        self.list_layout = BoxLayout(
            orientation='vertical', spacing=10,
            size_hint_y=None, padding=[0, 10]
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        outer.add_widget(self.scroll)

        clr_btn = ProButton(
            text="🗑  Clear All History", main_color='#7F1D1D',
            size_hint_y=None, height=60
        )
        clr_btn.bind(on_press=self._clear_all)
        outer.add_widget(clr_btn)

        panel.add_widget(outer)
        self.add_widget(panel)

    def on_enter(self):
        self._refresh()

    def _refresh(self):
        self.list_layout.clear_widgets()
        history = load_history()
        if not history:
            self.list_layout.add_widget(Label(
                text="Abhi tak koi download nahi hua.",
                color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=60
            ))
            return

        for entry in history:
            row = BoxLayout(size_hint_y=None, height=95, spacing=10, padding=[10, 5])
            with row.canvas.before:
                Color(*get_color_from_hex('#0F172A'))
                self._rr = RoundedRectangle(pos=row.pos, size=row.size, radius=[10])

            info = BoxLayout(orientation='vertical', size_hint_x=0.75)
            info.add_widget(Label(
                text=f"[b]{entry.get('filename','Unknown')}[/b]",
                markup=True, font_size='14sp',
                color=get_color_from_hex('#E2E8F0'),
                halign='left', size_hint_y=None, height=35
            ))
            info.add_widget(Label(
                text=f"🌐 {entry.get('lang','')}  🎙 {entry.get('voice','')}  🕐 {entry.get('time','')}",
                font_size='12sp', color=(0.5, 0.8, 0.5, 1),
                halign='left', size_hint_y=None, height=30
            ))
            row.add_widget(info)

            file_path = entry.get('path', '')
            if os.path.exists(file_path):
                pb = ProButton(text="▶", main_color='#10B981',
                               size_hint_x=None, width=55)
                pb.bind(on_press=lambda x, p=file_path: self._replay(p))
                row.add_widget(pb)

            self.list_layout.add_widget(row)

    def _replay(self, path):
        snd = SoundLoader.load(path)
        if snd:
            snd.play()

    def _clear_all(self, *args):
        try:
            with open(get_history_path(), 'w') as f:
                json.dump([], f)
        except:
            pass
        self._refresh()


# ─── Studio Screen ────────────────────────────────────────────────────────────
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.audio_handler = None
        self.out_file      = None
        self.speed_mode    = "🚶 Normal"
        self.selected_voice = '👨 Male'
        self._build()

    def _lbl(self, txt):
        return Label(
            text=txt, bold=True,
            color=(0.6, 0.8, 1, 1),
            size_hint_y=None, height=38
        )

    def _build(self):
        panel   = NeonPanel()
        scroll  = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical', padding=30, spacing=18,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Title
        content.add_widget(Label(
            text="[b]🎙 TITAN AI STUDIO PRO[/b]", markup=True,
            font_size='32sp', color=get_color_from_hex('#22D3EE'),
            size_hint_y=None, height=90
        ))

        # Language
        content.add_widget(self._lbl("🌐  Language:"))
        self.lang_spinner = Spinner(
            text='English', values=list(LANGUAGES.keys()),
            size_hint_y=None, height=60,
            background_color=get_color_from_hex('#1E3A5F'),
            color=(1, 1, 1, 1), font_size='17sp'
        )
        content.add_widget(self.lang_spinner)

        # Voice Profile
        content.add_widget(self._lbl("🎭  Voice Type:"))
        voice_row = GridLayout(cols=3, size_hint_y=None, height=130, spacing=8)
        self.voice_btns = {}
        for vname in VOICE_PROFILES:
            btn = ProButton(text=vname, main_color='#1E3A5F', font_size='13sp')
            btn.bind(on_press=lambda x, n=vname: self._select_voice(n))
            voice_row.add_widget(btn)
            self.voice_btns[vname] = btn
        content.add_widget(voice_row)
        self._select_voice('👨 Male')

        # Text Input
        content.add_widget(self._lbl("📝  Script:"))
        self.text_input = TextInput(
            hint_text="Yahan apna text likho...",
            multiline=True, size_hint_y=None, height=280,
            background_color=get_color_from_hex('#0F172A'),
            foreground_color=(1, 1, 1, 1),
            font_size='18sp', padding=[20, 20],
            cursor_color=get_color_from_hex('#22D3EE')
        )
        self.text_input.bind(text=self._update_count)
        content.add_widget(self.text_input)

        self.word_count = Label(
            text="Words: 0  |  Chars: 0",
            color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=35
        )
        content.add_widget(self.word_count)

        # Speed (3 buttons — FIXED)
        self.speed_label = Label(
            text="⚡  Speed: 🚶 Normal",
            color=(0.8, 0.8, 0.8, 1), size_hint_y=None, height=38
        )
        content.add_widget(self.speed_label)
        self.speed_btns = {}
        speed_row = BoxLayout(size_hint_y=None, height=65, spacing=10)
        for spd, col in [("🐢 Slow", "#6366F1"), ("🚶 Normal", "#10B981"), ("🚀 Fast", "#F59E0B")]:
            b = ProButton(text=spd, main_color=col)
            b.bind(on_press=lambda x, s=spd: self._set_speed(s))
            speed_row.add_widget(b)
            self.speed_btns[spd] = b
        content.add_widget(speed_row)

        # Status + Progress
        self.status = Label(
            text="🟡  Ready",
            italic=True, color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=45
        )
        content.add_widget(self.status)
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=18)
        content.add_widget(self.progress)

        # Generate
        self.gen_btn = ProButton(
            text="🚀  GENERATE SPEECH", main_color='#2563EB',
            size_hint_y=None, height=95, font_size='19sp', bold=True
        )
        self.gen_btn.bind(on_press=self._start_tts)
        content.add_widget(self.gen_btn)

        # Play / Stop
        ps_row = BoxLayout(size_hint_y=None, height=85, spacing=15)
        self.play_btn = ProButton(text="▶  PLAY",  main_color='#10B981', disabled=True)
        self.stop_btn = ProButton(text="⏹  STOP",  main_color='#EF4444', disabled=True)
        self.play_btn.bind(on_press=self._handle_play)
        self.stop_btn.bind(on_press=self._handle_stop)
        ps_row.add_widget(self.play_btn)
        ps_row.add_widget(self.stop_btn)
        content.add_widget(ps_row)

        # Download Button
        self.dl_btn = ProButton(
            text="⬇  DOWNLOAD AUDIO", main_color='#0EA5E9',
            size_hint_y=None, height=90, font_size='18sp', disabled=True
        )
        self.dl_btn.bind(on_press=self._handle_download)
        content.add_widget(self.dl_btn)

        # History Button
        hist_btn = ProButton(
            text="📂  DOWNLOAD HISTORY", main_color='#7C3AED',
            size_hint_y=None, height=80
        )
        hist_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'history'))
        content.add_widget(hist_btn)

        # Clear
        ProButton(text="🗑  CLEAR TEXT", main_color='#475569', size_hint_y=None, height=70)
        clr_btn = ProButton(text="🗑  CLEAR TEXT", main_color='#475569', size_hint_y=None, height=70)
        clr_btn.bind(on_press=lambda x: setattr(self.text_input, 'text', ''))
        content.add_widget(clr_btn)

        scroll.add_widget(content)
        panel.add_widget(scroll)
        self.add_widget(panel)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _select_voice(self, name):
        self.selected_voice = name
        for n, btn in self.voice_btns.items():
            btn.m_color = '#22C55E' if n == name else '#1E3A5F'
            btn.render()

    def _set_speed(self, mode):
        self.speed_mode = mode
        self.speed_label.text = f"⚡  Speed: {mode}"

    def _update_count(self, inst, val):
        words = len(val.split()) if val.strip() else 0
        self.word_count.text = f"Words: {words}  |  Chars: {len(val)}"

    # ── TTS ───────────────────────────────────────────────────────────────────

    def _start_tts(self, *args):
        text = self.text_input.text.strip()
        if not text:
            self.status.text = "❌  Text khaali hai!"
            return
        self.gen_btn.disabled  = True
        self.play_btn.disabled = True
        self.stop_btn.disabled = True
        self.dl_btn.disabled   = True
        self.progress.value    = 0
        self.status.text       = "⏳  Generating..."
        threading.Thread(target=self._tts_worker, daemon=True).start()

    def _tts_worker(self):
        try:
            from gtts import gTTS
            Clock.schedule_once(lambda dt: self._set_ui(25, "⏳  Connecting to server..."))

            lang    = LANGUAGES.get(self.lang_spinner.text, 'en')
            profile = VOICE_PROFILES.get(self.selected_voice, VOICE_PROFILES['👨 Male'])
            tld     = profile['tld']

            # Speed fix:
            # Slow  → slow=True
            # Normal/Fast → slow=False
            # (gTTS does not support faster than normal natively)
            use_slow = (self.speed_mode == "🐢 Slow") or profile['slow']

            Clock.schedule_once(lambda dt: self._set_ui(55, "⏳  Synthesizing voice..."))

            tts = gTTS(text=self.text_input.text, lang=lang, tld=tld, slow=use_slow)

            out = os.path.join(App.get_running_app().user_data_dir, "titan_output.mp3")
            tts.save(out)
            self.out_file = out

            Clock.schedule_once(lambda dt: self._on_done())

        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._on_error(err))

    def _set_ui(self, val, msg):
        self.progress.value = val
        self.status.text    = msg

    def _on_done(self):
        if self.audio_handler:
            self.audio_handler.stop()
            self.audio_handler.unload()
            self.audio_handler = None
        self.audio_handler     = SoundLoader.load(self.out_file)
        self.progress.value    = 100
        self.status.text       = "✅  Ready! Play ya Download karo."
        self.gen_btn.disabled  = False
        self.play_btn.disabled = False
        self.stop_btn.disabled = False
        self.dl_btn.disabled   = False

    def _on_error(self, err):
        if any(k in err.lower() for k in ["network","connection","gaierror","timeout"]):
            msg = "❌  Internet nahi hai! gTTS ke liye internet chahiye."
        elif "lang" in err.lower():
            msg = "❌  Is language ke saath yeh voice support nahi."
        else:
            msg = f"❌  Error: {err[:55]}"
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

    # ── Download ──────────────────────────────────────────────────────────────

    def _handle_download(self, *args):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status.text = "❌  Pehle speech generate karo!"
            return

        timestamp = int(time.time())
        fname     = f"Titan_{self.lang_spinner.text}_{timestamp}.mp3"

        dest_dir = "/sdcard/Download" if ANDROID_ENV else os.path.expanduser("~")
        dest     = os.path.join(dest_dir, fname)

        try:
            shutil.copyfile(self.out_file, dest)
            self.status.text = f"✅  Downloaded: {fname}"

            save_to_history({
                "filename": fname,
                "path":     dest,
                "lang":     self.lang_spinner.text,
                "voice":    self.selected_voice,
                "speed":    self.speed_mode,
                "time":     time.strftime("%Y-%m-%d %H:%M"),
            })

            self._popup("✅ Download Complete!", f"File save ho gayi:\n{fname}\n\n📂 {dest_dir}")

        except Exception as e:
            self.status.text = f"❌  Download failed: {str(e)[:45]}"

    def _popup(self, title, msg):
        box = BoxLayout(orientation='vertical', padding=20, spacing=15)
        box.add_widget(Label(text=msg, color=(1,1,1,1), font_size='15sp'))
        ok  = ProButton(text="OK ✓", main_color='#10B981', size_hint_y=None, height=60)
        box.add_widget(ok)
        p = Popup(
            title=title, content=box,
            size_hint=(0.85, 0.5),
            background_color=get_color_from_hex('#0F172A')
        )
