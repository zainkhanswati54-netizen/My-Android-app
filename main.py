import os
import threading
import time
import shutil
import json

# ─── Android Detection ───────────────────────────────────────────────────────
try:
    from android.permissions import request_permissions, Permission
    ANDROID_ENV = True
    os.environ['KIVY_AUDIO'] = 'android'
except ImportError:
    ANDROID_ENV = False

# ─── Kivy Config (imports se PEHLE) ──────────────────────────────────────────
from kivy.config import Config
Config.set('graphics', 'resizable', '0')
# FIX #1: Android par OpenGL ES 2 force karo — warna black screen / crash
Config.set('graphics', 'multisamples', '0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line

# ─── Languages ────────────────────────────────────────────────────────────────
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
VOICE_PROFILES = {
    'Male':    {'tld': 'com',    'slow': False},
    'Female':  {'tld': 'com.au', 'slow': False},
    'Child':   {'tld': 'co.uk',  'slow': True },
    'News':    {'tld': 'ca',     'slow': False},
    'Soft':    {'tld': 'co.in',  'slow': True },
}

# ─── History Helpers ──────────────────────────────────────────────────────────
def get_history_path():
    app = App.get_running_app()
    base = app.user_data_dir if app else '.'
    return os.path.join(base, 'download_history.json')

def load_history():
    try:
        with open(get_history_path(), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_to_history(entry):
    history = load_history()
    history.insert(0, entry)
    try:
        with open(get_history_path(), 'w', encoding='utf-8') as f:
            json.dump(history[:50], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ─── UI Components ────────────────────────────────────────────────────────────
class NeonPanel(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex('#020617'))
            self.rect   = Rectangle(pos=self.pos, size=self.size)
            Color(*get_color_from_hex('#1E293B'))
            self.border = Line(
                rectangle=(self.x, self.y, self.width, self.height), width=2)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self.rect.pos   = self.pos
        self.rect.size  = self.size
        self.border.rectangle = (
            self.x+5, self.y+5, self.width-10, self.height-10)


class ProButton(Button):
    def __init__(self, main_color='#3B82F6', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color  = (0, 0, 0, 0)
        self.m_color = main_color
        self.color   = (1, 1, 1, 1)
        self.bind(pos=self.render, size=self.render)

    def render(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.m_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[14])


# ─── Splash Screen ────────────────────────────────────────────────────────────
class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = NeonPanel()
        layout.add_widget(Label(
            text='TITAN AI', font_size='50sp', bold=True,
            color=get_color_from_hex('#38BDF8'),
            pos_hint={'center_x': 0.5, 'center_y': 0.62}
        ))
        self.lbl = Label(
            text='Initializing...',
            color=get_color_from_hex('#94A3B8'),
            pos_hint={'center_x': 0.5, 'center_y': 0.47}
        )
        layout.add_widget(self.lbl)
        self.pb = ProgressBar(
            max=100, size_hint=(0.65, None), height=22,
            pos_hint={'center_x': 0.5, 'center_y': 0.40}
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
            v = self.pb.value
            if v == 30:  self.lbl.text = 'Loading Audio Engines...'
            elif v == 60: self.lbl.text = 'Loading Voice Profiles...'
            elif v == 90: self.lbl.text = 'Almost Ready!'
        else:
            self.manager.current = 'studio'


# ─── History Screen ───────────────────────────────────────────────────────────
class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._active_sounds = []
        self._build()

    def _build(self):
        panel = NeonPanel()
        outer = BoxLayout(orientation='vertical', padding=15, spacing=12)

        # Header
        hdr = BoxLayout(size_hint_y=None, height=65, spacing=10)
        back = ProButton(text='<- Back', main_color='#475569', size_hint_x=0.3)
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'studio'))
        hdr.add_widget(back)
        hdr.add_widget(Label(
            text='[b]Download History[/b]', markup=True,
            font_size='20sp', color=get_color_from_hex('#22D3EE')
        ))
        outer.add_widget(hdr)

        scroll = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical', spacing=8,
            size_hint_y=None, padding=[0, 5]
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        scroll.add_widget(self.list_box)
        outer.add_widget(scroll)

        clr = ProButton(
            text='Clear All History', main_color='#7F1D1D',
            size_hint_y=None, height=58
        )
        clr.bind(on_press=self._clear_all)
        outer.add_widget(clr)

        # FIX #2: outer ko NeonPanel ke andar daalo, phir screen mein add karo
        panel.add_widget(outer)
        self.add_widget(panel)

    def on_enter(self):
        self._refresh()

    def _refresh(self):
        self.list_box.clear_widgets()
        history = load_history()
        if not history:
            self.list_box.add_widget(Label(
                text='Abhi tak koi download nahi hua.',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None, height=60
            ))
            return

        for entry in history:
            # FIX #3: canvas.before mein bind karo pos/size ke saath
            # warna RoundedRectangle galat jagah render hoti thi (crash / glitch)
            row = BoxLayout(
                size_hint_y=None, height=88,
                spacing=10, padding=[10, 4]
            )

            def _draw_row(widget, *a):
                widget.canvas.before.clear()
                with widget.canvas.before:
                    Color(*get_color_from_hex('#0F172A'))
                    RoundedRectangle(
                        pos=widget.pos, size=widget.size, radius=[10])

            row.bind(pos=_draw_row, size=_draw_row)

            info = BoxLayout(orientation='vertical', size_hint_x=0.78)
            info.add_widget(Label(
                text='[b]' + entry.get('filename', 'Unknown') + '[/b]',
                markup=True, font_size='13sp',
                color=get_color_from_hex('#E2E8F0'),
                halign='left', valign='middle',
                size_hint_y=None, height=34,
                text_size=(None, None)
            ))
            info.add_widget(Label(
                text=(entry.get('lang', '') + '  ' +
                      entry.get('voice', '') + '  ' +
                      entry.get('time', '')),
                font_size='11sp', color=(0.4, 0.8, 0.4, 1),
                halign='left', valign='middle',
                size_hint_y=None, height=28,
                text_size=(None, None)
            ))
            row.add_widget(info)

            fpath = entry.get('path', '')
            if os.path.exists(fpath):
                pb2 = ProButton(
                    text='PLAY', main_color='#10B981',
                    size_hint_x=None, width=62, font_size='12sp'
                )
                pb2.bind(on_press=lambda x, p=fpath: self._replay(p))
                row.add_widget(pb2)

            self.list_box.add_widget(row)

    def _replay(self, path):
        snd = SoundLoader.load(path)
        if snd:
            self._active_sounds.append(snd)
            snd.play()

    def _clear_all(self, *a):
        try:
            with open(get_history_path(), 'w') as f:
                json.dump([], f)
        except Exception:
            pass
        self._refresh()


# ─── Studio Screen ────────────────────────────────────────────────────────────
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.audio_handler  = None
        self.out_file       = None
        self.speed_mode     = 'Normal'
        self.selected_voice = 'Male'
        self._build()

    # ── small helper ──────────────────────────────────────────────────────────
    def _lbl(self, txt):
        return Label(
            text=txt, bold=True,
            color=(0.6, 0.8, 1, 1),
            size_hint_y=None, height=36
        )

    def _build(self):
        panel   = NeonPanel()
        scroll  = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical', padding=28, spacing=16,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Title
        content.add_widget(Label(
            text='[b]TITAN AI STUDIO PRO[/b]', markup=True,
            font_size='30sp', color=get_color_from_hex('#22D3EE'),
            size_hint_y=None, height=85
        ))

        # Language spinner
        content.add_widget(self._lbl('Language:'))
        self.lang_spinner = Spinner(
            text='English', values=list(LANGUAGES.keys()),
            size_hint_y=None, height=58,
            background_color=get_color_from_hex('#1E3A5F'),
            color=(1, 1, 1, 1), font_size='16sp'
        )
        content.add_widget(self.lang_spinner)

        # Voice type
        content.add_widget(self._lbl('Voice Type:'))
        # FIX #4: Emoji characters removed from button text —
        # Android par kuch fonts mein emoji crash karta tha
        vgrid = GridLayout(cols=3, size_hint_y=None, height=120, spacing=8)
        self.voice_btns = {}
        for vname in VOICE_PROFILES:
            btn = ProButton(text=vname, main_color='#1E3A5F', font_size='14sp')
            btn.bind(on_press=lambda x, n=vname: self._sel_voice(n))
            vgrid.add_widget(btn)
            self.voice_btns[vname] = btn
        content.add_widget(vgrid)
        self._sel_voice('Male')

        # Text input
        content.add_widget(self._lbl('Script:'))
        self.text_input = TextInput(
            hint_text='Yahan apna text likho...',
            multiline=True, size_hint_y=None, height=260,
            background_color=get_color_from_hex('#0F172A'),
            foreground_color=(1, 1, 1, 1),
            font_size='17sp', padding=[18, 18],
            cursor_color=get_color_from_hex('#22D3EE')
        )
        self.text_input.bind(text=self._upd_count)
        content.add_widget(self.text_input)

        self.wc_label = Label(
            text='Words: 0  |  Chars: 0',
            color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=32
        )
        content.add_widget(self.wc_label)

        # Speed
        content.add_widget(self._lbl('Speed:'))
        self.speed_label = Label(
            text='Selected: Normal',
            color=(0.7, 0.9, 0.7, 1), size_hint_y=None, height=34
        )
        content.add_widget(self.speed_label)
        spd_row = BoxLayout(size_hint_y=None, height=62, spacing=10)
        self.speed_btns = {}
        for spd, col in [('Slow', '#6366F1'), ('Normal', '#10B981'), ('Fast', '#F59E0B')]:
            b = ProButton(text=spd, main_color=col)
            b.bind(on_press=lambda x, s=spd: self._set_speed(s))
            spd_row.add_widget(b)
            self.speed_btns[spd] = b
        content.add_widget(spd_row)
        self._set_speed('Normal')

        # Status + Progress
        self.status = Label(
            text='Ready',
            italic=True, color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=42
        )
        content.add_widget(self.status)
        self.progress = ProgressBar(
            max=100, value=0, size_hint_y=None, height=16)
        content.add_widget(self.progress)

        # Generate button
        self.gen_btn = ProButton(
            text='GENERATE SPEECH', main_color='#2563EB',
            size_hint_y=None, height=90, font_size='18sp', bold=True
        )
        self.gen_btn.bind(on_press=self._start_tts)
        content.add_widget(self.gen_btn)

        # Play / Stop
        ps = BoxLayout(size_hint_y=None, height=80, spacing=14)
        self.play_btn = ProButton(
            text='PLAY', main_color='#10B981', disabled=True)
        self.stop_btn = ProButton(
            text='STOP', main_color='#EF4444', disabled=True)
        self.play_btn.bind(on_press=self._play)
        self.stop_btn.bind(on_press=self._stop)
        ps.add_widget(self.play_btn)
        ps.add_widget(self.stop_btn)
        content.add_widget(ps)

        # Download
        self.dl_btn = ProButton(
            text='DOWNLOAD AUDIO', main_color='#0EA5E9',
            size_hint_y=None, height=85, font_size='17sp', disabled=True
        )
        self.dl_btn.bind(on_press=self._download)
        content.add_widget(self.dl_btn)

        # History
        hist = ProButton(
            text='DOWNLOAD HISTORY', main_color='#7C3AED',
            size_hint_y=None, height=75
        )
        hist.bind(on_press=lambda x: setattr(self.manager, 'current', 'history'))
        content.add_widget(hist)

        # Clear text
        clr = ProButton(
            text='CLEAR TEXT', main_color='#475569',
            size_hint_y=None, height=65
        )
        clr.bind(on_press=lambda x: setattr(self.text_input, 'text', ''))
        content.add_widget(clr)

        scroll.add_widget(content)
        panel.add_widget(scroll)
        self.add_widget(panel)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _sel_voice(self, name):
        self.selected_voice = name
        for n, btn in self.voice_btns.items():
            btn.m_color = '#22C55E' if n == name else '#1E3A5F'
            btn.render()

    def _set_speed(self, mode):
        self.speed_mode = mode
        self.speed_label.text = f'Selected: {mode}'
        for n, btn in self.speed_btns.items():
            btn.m_color = ('#22C55E' if n == mode
                           else ('#6366F1' if n == 'Slow'
                                 else ('#10B981' if n == 'Normal'
                                       else '#F59E0B')))
            btn.render()

    def _upd_count(self, inst, val):
        w = len(val.split()) if val.strip() else 0
        self.wc_label.text = f'Words: {w}  |  Chars: {len(val)}'

    # ── TTS ───────────────────────────────────────────────────────────────────

    def _start_tts(self, *a):
        text = self.text_input.text.strip()
        if not text:
            self.status.text = 'Error: Text khaali hai!'
            return
        self._lock_ui(True)
        self.progress.value = 0
        self.status.text    = 'Generating...'
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            from gtts import gTTS
            Clock.schedule_once(
                lambda dt: self._set_ui(25, 'Connecting to server...'))

            lang    = LANGUAGES.get(self.lang_spinner.text, 'en')
            profile = VOICE_PROFILES.get(
                self.selected_voice, VOICE_PROFILES['Male'])
            tld      = profile['tld']
            use_slow = (self.speed_mode == 'Slow') or profile['slow']

            Clock.schedule_once(
                lambda dt: self._set_ui(55, 'Synthesizing voice...'))

            tts = gTTS(
                text=self.text_input.text,
                lang=lang, tld=tld, slow=use_slow
            )
            out = os.path.join(
                App.get_running_app().user_data_dir, 'titan_out.mp3')
            tts.save(out)
            self.out_file = out

            Clock.schedule_once(lambda dt: self._done())

        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._err(err))

    def _set_ui(self, val, msg):
        self.progress.value = val
        self.status.text    = msg

    def _done(self):
        # Safe audio reload
        if self.audio_handler:
            try:
                self.audio_handler.stop()
                self.audio_handler.unload()
            except Exception:
                pass
            self.audio_handler = None

        self.audio_handler = SoundLoader.load(self.out_file)
        self.progress.value = 100
        self.status.text    = 'Ready! Play ya Download karo.'
        self._lock_ui(False)

    def _err(self, err):
        e = err.lower()
        if any(k in e for k in ['network', 'connection', 'gaierror', 'timeout']):
            msg = 'Error: Internet nahi hai!'
        elif 'lang' in e:
            msg = 'Error: Is language ke saath yeh voice nahi chalti.'
        else:
            msg = f'Error: {err[:50]}'
        self.status.text    = msg
        self.progress.value = 0
        self._lock_ui(False, audio_ready=False)

    def _lock_ui(self, locked, audio_ready=True):
        self.gen_btn.disabled  = locked
        self.play_btn.disabled = locked or not audio_ready
        self.stop_btn.disabled = locked or not audio_ready
        self.dl_btn.disabled   = locked or not audio_ready

    # ── Playback ──────────────────────────────────────────────────────────────

    def _play(self, *a):
        if not self.audio_handler:
            return
        if self.audio_handler.state == 'play':
            self.audio_handler.stop()
            self.play_btn.text = 'PLAY'
        else:
            self.audio_handler.play()
            self.play_btn.text = 'PAUSE'

    def _stop(self, *a):
        if self.audio_handler:
            self.audio_handler.stop()
        self.play_btn.text = 'PLAY'

    # ── Download ──────────────────────────────────────────────────────────────

    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status.text = 'Error: Pehle speech generate karo!'
            return

        ts    = int(time.time())
        fname = f"Titan_{self.lang_spinner.text}_{ts}.mp3"
        ddir  = '/sdcard/Download' if ANDROID_ENV else os.path.expanduser('~')
        dest  = os.path.join(ddir, fname)

        try:
            os.makedirs(ddir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self.status.text = f'Downloaded: {fname}'

            save_to_history({
                'filename': fname,
                'path':     dest,
                'lang':     self.lang_spinner.text,
                'voice':    self.selected_voice,
