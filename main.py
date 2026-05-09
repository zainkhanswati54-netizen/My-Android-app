# ============================================================
#  Titan AI Studio Pro  –  main.py
#  Version 6.0.0  |  Industry-Grade Rewrite
#  Fixes: Logo image, storage, animations, UI scale,
#         gender bug, language validation, history polish
# ============================================================

import os
import threading
import time
import shutil
import json
import re

# ── Android detection ─────────────────────────────────────
try:
    from android.permissions import (
        request_permissions, Permission, check_permission
    )
    from android.storage import primary_external_storage_path
    ANDROID_ENV = True
except Exception:
    ANDROID_ENV = False

# ── Kivy low-level config (must come before kivy imports) ──
from kivy.config import Config
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle,
    Line, Ellipse, StencilPush, StencilUse,
    StencilPop, StencilUnUse,
)
from kivy.metrics import dp, sp
from kivy.properties import (
    StringProperty, BooleanProperty,
    NumericProperty, ListProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import (
    ScreenManager, Screen, SlideTransition, FadeTransition
)
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

# ═══════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ═══════════════════════════════════════════════════════════
C_BG      = '#020817'
C_CARD    = '#0F172A'
C_CARD2   = '#1E293B'
C_BLUE    = '#2563EB'
C_BLUE2   = '#3B82F6'
C_ACCENT  = '#38BDF8'
C_GREEN   = '#22C55E'
C_RED     = '#EF4444'
C_PURPLE  = '#7C3AED'
C_CYAN    = '#0EA5E9'
C_GRAY    = '#475569'
C_WHITE   = '#F1F5F9'
C_MUTED   = '#64748B'
C_AMBER   = '#F59E0B'
C_DARK_RED= '#7F1D1D'
C_SURFACE = '#152032'

# ═══════════════════════════════════════════════════════════
#  LANGUAGE & VOICE DATA
# ═══════════════════════════════════════════════════════════
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
    'Chinese':  'zh-TW',
    'Japanese': 'ja',
    'Korean':   'ko',
}

# gTTS tld controls accent/voice slightly; slow flag simulates speed
VOICE_TLD = {
    'Male':   'com',
    'Female': 'co.uk',
}

LATIN_ONLY_LANGS = {'English', 'French', 'Spanish', 'German', 'Turkish'}

LANG_SCRIPTS = {
    'Chinese':  (lambda t: any('\u4e00' <= c <= '\u9fff' for c in t),
                 'Chinese selected!\nPlease write in Chinese characters (汉字).'),
    'Japanese': (lambda t: any('\u3040' <= c <= '\u30ff' for c in t)
                           or any('\u4e00' <= c <= '\u9fff' for c in t),
                 'Japanese selected!\nPlease write in Japanese (Hiragana/Katakana/Kanji).'),
    'Korean':   (lambda t: any('\uac00' <= c <= '\ud7a3' for c in t),
                 'Korean selected!\nPlease write in Korean (Hangul).'),
    'Arabic':   (lambda t: any('\u0600' <= c <= '\u06ff' for c in t),
                 'Arabic selected!\nPlease write in Arabic script.'),
    'Urdu':     (lambda t: any('\u0600' <= c <= '\u06ff' for c in t),
                 'Urdu selected!\nPlease write in Urdu script.'),
    'Hindi':    (lambda t: any('\u0900' <= c <= '\u097f' for c in t),
                 'Hindi selected!\nPlease write in Devanagari script.'),
    'Russian':  (lambda t: any('\u0400' <= c <= '\u04ff' for c in t),
                 'Russian selected!\nPlease write in Cyrillic script.'),
}


def check_lang_text(text, lang):
    """Returns (ok:bool, error_msg:str)"""
    if lang in LATIN_ONLY_LANGS:
        return True, ''
    has_latin = any(c.isalpha() and ord(c) < 128 for c in text)
    if not has_latin:
        return True, ''
    if lang in LANG_SCRIPTS:
        fn, msg = LANG_SCRIPTS[lang]
        if not fn(text):
            return False, msg
    return True, ''


# ═══════════════════════════════════════════════════════════
#  STORAGE HELPERS
# ═══════════════════════════════════════════════════════════
def get_internal_storage_path():
    """Return best internal storage root available."""
    if ANDROID_ENV:
        # Try common Android internal paths
        for p in ['/storage/emulated/0', '/sdcard', '/mnt/sdcard']:
            if os.path.exists(p):
                return p
    return os.path.expanduser('~')


def get_save_dirs():
    """
    Return list of (label, path) tuples.
    Always includes internal storage options.
    SD card options added only when a real physical SD card exists.
    """
    dirs = []
    if ANDROID_ENV:
        internal = get_internal_storage_path()
        dirs.append(('Internal Storage\n' + internal, internal))
        dl = os.path.join(internal, 'Download')
        dirs.append(('Downloads Folder\n' + dl, dl))
        music = os.path.join(internal, 'Music')
        dirs.append(('Music Folder\n' + music, music))
        docs = os.path.join(internal, 'Documents')
        dirs.append(('Documents Folder\n' + docs, docs))

        # Physical SD card – only when different from internal
        try:
            ext = primary_external_storage_path()
            if ext and ext not in (internal, '/sdcard',
                                    '/storage/emulated/0'):
                dirs.append(('SD Card\n' + ext, ext))
                dirs.append(('SD Card Downloads\n' + ext + '/Download',
                              ext + '/Download'))
        except Exception:
            pass
    else:
        home = os.path.expanduser('~')
        dirs.append(('Home Folder\n' + home, home))
        for name in ['Downloads', 'Desktop', 'Documents', 'Music']:
            p = os.path.join(home, name)
            dirs.append((name + '\n' + p, p))
    return dirs


# ═══════════════════════════════════════════════════════════
#  HISTORY PERSISTENCE
# ═══════════════════════════════════════════════════════════
def history_path():
    app = App.get_running_app()
    d = app.user_data_dir if app else '.'
    return os.path.join(d, 'history.json')


def history_load():
    try:
        with open(history_path(), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def history_save(entry):
    data = history_load()
    data.insert(0, entry)
    try:
        with open(history_path(), 'w', encoding='utf-8') as f:
            json.dump(data[:200], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def history_clear():
    try:
        with open(history_path(), 'w') as f:
            json.dump([], f)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════
#  FILE READERS
# ═══════════════════════════════════════════════════════════
def read_txt(path):
    for enc in ['utf-8', 'utf-16', 'latin-1']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    return ''


def read_pdf(path):
    try:
        with open(path, 'rb') as f:
            raw = f.read().decode('latin-1', errors='ignore')
        parts = re.findall(r'BT(.*?)ET', raw, re.DOTALL)
        text = []
        for p in parts:
            for m in re.findall(r'\((.*?)\)', p):
                text.append(m)
        result = ' '.join(text).replace('\\n', '\n').strip()
        return result if len(result) > 5 else ''
    except Exception:
        return ''


def read_docx(path):
    try:
        import zipfile
        with zipfile.ZipFile(path) as z:
            if 'word/document.xml' in z.namelist():
                xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
                return ' '.join(re.sub(r'<[^>]+>', ' ', xml).split())
        return ''
    except Exception:
        return ''


# ═══════════════════════════════════════════════════════════
#  UI PRIMITIVE HELPERS
# ═══════════════════════════════════════════════════════════
def hex_c(h):
    return get_color_from_hex(h)


def lbl(txt, size=15, color=C_MUTED, bold=False, h=36):
    l = Label(
        text=txt,
        font_size=sp(size),
        bold=bold,
        color=hex_c(color),
        size_hint_y=None,
        height=dp(h),
        halign='left',
        valign='middle',
    )
    l.bind(size=l.setter('text_size'))
    return l


def card_bg(widget, color=C_CARD, radius=14):
    """Attach a rounded rectangle background to any widget."""
    with widget.canvas.before:
        Color(*hex_c(color))
        rr = RoundedRectangle(
            pos=widget.pos, size=widget.size, radius=[dp(radius)]
        )

    def _upd(w, *a):
        rr.pos = w.pos
        rr.size = w.size

    widget.bind(pos=_upd, size=_upd)


def separator(color=C_CARD2, h=1):
    s = Widget(size_hint_y=None, height=dp(h))
    with s.canvas:
        Color(*hex_c(color))
        Rectangle(pos=s.pos, size=s.size)
    s.bind(pos=lambda w, *a: setattr(w.canvas.children[-1], 'pos', w.pos),
           size=lambda w, *a: setattr(w.canvas.children[-1], 'size', w.size))
    return s


# ═══════════════════════════════════════════════════════════
#  FLAT BUTTON  (with press ripple animation)
# ═══════════════════════════════════════════════════════════
class FlatBtn(Button):
    def __init__(self, bg=C_BLUE, radius=14, **kw):
        super().__init__(**kw)
        self.bg_color  = bg
        self._radius   = radius
        self.background_normal   = ''
        self.background_down     = ''
        self.background_color    = (0, 0, 0, 0)
        self.color               = (1, 1, 1, 1)
        self.font_size           = kw.get('font_size', sp(16))
        self._rr = None
        self.bind(pos=self._draw, size=self._draw)

    def set_bg(self, color):
        self.bg_color = color
        self._draw()

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex_c(self.bg_color))
            self._rr = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[dp(self._radius)]
            )

    def on_press(self):
        # Scale-bounce animation for tactile feel
        anim = (
            Animation(opacity=0.55, duration=0.06)
            + Animation(opacity=1.0, duration=0.14)
        )
        anim.start(self)

    def on_disabled(self, inst, val):
        self.opacity = 0.4 if val else 1.0


# ═══════════════════════════════════════════════════════════
#  DARK PANEL (screen background)
# ═══════════════════════════════════════════════════════════
class DarkPanel(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*hex_c(C_BG))
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos  = self.pos
        self._rect.size = self.size


# ═══════════════════════════════════════════════════════════
#  LOGO IMAGE WIDGET
#  Uses AI.png from app directory; falls back to "SS" text
# ═══════════════════════════════════════════════════════════
class LogoWidget(FloatLayout):
    def __init__(self, size_hint=None, width=None, height=None, **kw):
        super().__init__(**kw)
        if size_hint is not None:
            self.size_hint = size_hint
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height

        # Try loading real logo image
        logo_path = self._find_logo()
        if logo_path:
            img = KivyImage(
                source=logo_path,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(1, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            )
            self.add_widget(img)
        else:
            # Fallback: styled "SS" text
            self.add_widget(Label(
                text='SS',
                font_size=sp(28),
                bold=True,
                color=hex_c(C_BLUE2),
                size_hint=(1, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            ))

    def _find_logo(self):
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI.png'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI.jpg'),
        ]
        if ANDROID_ENV:
            try:
                app = App.get_running_app()
                if app:
                    candidates.insert(0, os.path.join(app.user_data_dir, 'AI.png'))
            except Exception:
                pass
        for c in candidates:
            if os.path.exists(c):
                return c
        return None


# ═══════════════════════════════════════════════════════════
#  LOADING SCREEN
# ═══════════════════════════════════════════════════════════
class LoadingScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._d  = 0
        self._ev = None
        self._build()

    def _build(self):
        root = DarkPanel()

        # ── Logo image (centre-top area) ──
        logo_path = self._find_logo()
        if logo_path:
            self.logo_img = KivyImage(
                source=logo_path,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(None, None),
                size=(dp(180), dp(180)),
                pos_hint={'center_x': 0.5, 'center_y': 0.60},
                opacity=0,
            )
            root.add_widget(self.logo_img)
            self.logo_lbl = None
        else:
            # Fallback styled label
            self.logo_lbl = Label(
                text='SS',
                font_size=sp(96),
                bold=True,
                color=hex_c(C_BLUE2),
                pos_hint={'center_x': 0.5, 'center_y': 0.60},
                opacity=0,
            )
            root.add_widget(self.logo_lbl)
            self.logo_img = None

        self.title_lbl = Label(
            text='Titan AI Studio Pro',
            font_size=sp(26),
            bold=True,
            color=hex_c(C_WHITE),
            pos_hint={'center_x': 0.5, 'center_y': 0.38},
            opacity=0,
        )
        root.add_widget(self.title_lbl)

        self.sub_lbl = Label(
            text='Your Personal Narrator, Always Free.',
            font_size=sp(15),
            color=hex_c(C_MUTED),
            pos_hint={'center_x': 0.5, 'center_y': 0.30},
            opacity=0,
        )
        root.add_widget(self.sub_lbl)

        self.dot_lbl = Label(
            text='Loading...',
            font_size=sp(15),
            color=hex_c(C_BLUE2),
            pos_hint={'center_x': 0.5, 'center_y': 0.20},
            opacity=0,
        )
        root.add_widget(self.dot_lbl)

        # Animated progress bar strip
        self.prog = ProgressBar(
            max=100, value=0,
            size_hint=(0.7, None),
            height=dp(6),
            pos_hint={'center_x': 0.5, 'y': 0.12},
        )
        root.add_widget(self.prog)

        self.add_widget(root)

    def _find_logo(self):
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI.png'),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def on_enter(self, *a):
        logo_widget = self.logo_img or self.logo_lbl
        if logo_widget:
            Animation(opacity=1, duration=0.7).start(logo_widget)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self.title_lbl), 0.5)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self.sub_lbl), 0.8)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self.dot_lbl), 1.0)
        Clock.schedule_once(self._start_progress, 0.5)
        self._ev = Clock.schedule_interval(self._tick, 0.45)
        Clock.schedule_once(self._go, 3.8)

    def _start_progress(self, dt):
        Animation(value=90, duration=3.0, t='out_cubic').start(self.prog)

    def on_leave(self, *a):
        if self._ev:
            self._ev.cancel()
            self._ev = None

    def _tick(self, dt):
        self._d = (self._d + 1) % 4
        self.dot_lbl.text = 'Loading' + '.' * (self._d + 1)

    def _go(self, dt):
        Animation(value=100, duration=0.25).start(self.prog)
        Clock.schedule_once(lambda dt2: self._switch(), 0.3)

    def _switch(self):
        self.manager.transition = FadeTransition(duration=0.45)
        self.manager.current = 'studio'


# ═══════════════════════════════════════════════════════════
#  HISTORY SCREEN
# ═══════════════════════════════════════════════════════════
class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._sounds = []
        self._build()

    def _build(self):
        root = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        # ── Header ──
        hdr = BoxLayout(size_hint_y=None, height=dp(72), spacing=dp(12))
        card_bg(hdr, C_CARD, 0)

        back = FlatBtn(
            text='← Back', bg=C_GRAY,
            size_hint_x=None, width=dp(110),
            font_size=sp(15),
        )
        back.bind(on_press=self._go_back)
        hdr.add_widget(back)

        hdr.add_widget(Label(
            text='Download History',
            font_size=sp(22), bold=True,
            color=hex_c(C_ACCENT),
        ))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        # ── Scrollable list ──
        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(14),
            padding=[dp(2), dp(8)],
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)

        outer.add_widget(separator())

        # ── Clear button ──
        clr = FlatBtn(
            text='🗑  Clear All History',
            bg=C_DARK_RED,
            size_hint_y=None, height=dp(58),
            font_size=sp(16),
        )
        clr.bind(on_press=self._confirm_clear)
        outer.add_widget(clr)

        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        # Slide-in animation for the whole screen
        self.opacity = 0
        self.x = dp(80)
        anim = Animation(opacity=1, x=0, duration=0.3, t='out_cubic')
        anim.start(self)
        Clock.schedule_once(lambda dt: self._refresh(), 0.1)

    def _go_back(self, *a):
        self.manager.transition = SlideTransition(direction='right', duration=0.3)
        self.manager.current = 'studio'

    def _refresh(self):
        self.list_box.clear_widgets()
        data = history_load()
        if not data:
            empty = Label(
                text='No downloads yet.\nGenerate and save your first voice!',
                color=hex_c(C_MUTED),
                font_size=sp(15),
                size_hint_y=None,
                height=dp(120),
                halign='center', valign='middle',
            )
            empty.bind(size=empty.setter('text_size'))
            self.list_box.add_widget(empty)
            return

        for i, entry in enumerate(data):
            row = self._make_row(entry)
            row.opacity = 0
            self.list_box.add_widget(row)
            # Stagger fade-in for each item
            Clock.schedule_once(
                lambda dt, w=row: Animation(
                    opacity=1, duration=0.22, t='out_quad'
                ).start(w),
                i * 0.07,
            )

    def _make_row(self, entry):
        row = BoxLayout(
            size_hint_y=None, height=dp(100),
            spacing=dp(10), padding=[dp(14), dp(8)],
        )
        card_bg(row, C_CARD2, 16)

        # Icon area
        icon_box = BoxLayout(
            orientation='vertical',
            size_hint_x=None, width=dp(48),
        )
        icon_lbl = Label(
            text='🎵',
            font_size=sp(26),
            size_hint_y=None, height=dp(84),
        )
        icon_box.add_widget(icon_lbl)
        row.add_widget(icon_box)

        # Info area
        info = BoxLayout(orientation='vertical', size_hint_x=0.72)
        fname = Label(
            text=entry.get('filename', 'unknown'),
            font_size=sp(13), bold=True,
            color=hex_c(C_WHITE),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(40),
        )
        fname.bind(size=fname.setter('text_size'))
        info.add_widget(fname)

        meta = Label(
            text=(entry.get('lang', '') + '  •  '
                  + entry.get('voice', '') + '  •  '
                  + entry.get('time', '')),
            font_size=sp(12),
            color=hex_c(C_GREEN),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(32),
        )
        meta.bind(size=meta.setter('text_size'))
        info.add_widget(meta)
        row.add_widget(info)

        # Play button (only if file still exists)
        fp = entry.get('path', '')
        if os.path.exists(fp):
            pb = FlatBtn(
                text='▶ PLAY',
                bg=C_GREEN,
                size_hint_x=None, width=dp(82),
                font_size=sp(13),
            )
            pb.bind(on_press=lambda *a, p=fp, b=pb: self._play(p, b))
            row.add_widget(pb)
        else:
            ml = Label(
                text='[Missing]',
                font_size=sp(11),
                color=hex_c(C_RED),
                size_hint_x=None, width=dp(82),
            )
            row.add_widget(ml)

        return row

    def _play(self, path, btn):
        # Stop all currently playing sounds
        for s in self._sounds:
            try:
                s.stop()
            except Exception:
                pass
        self._sounds.clear()

        snd = SoundLoader.load(path)
        if snd:
            self._sounds.append(snd)
            snd.play()
            btn.text = '⏹ STOP'
            btn.set_bg(C_RED)

            def on_stop(dt):
                try:
                    btn.text = '▶ PLAY'
                    btn.set_bg(C_GREEN)
                except Exception:
                    pass

            Clock.schedule_once(on_stop, snd.length + 0.3)

    def _confirm_clear(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        box.add_widget(Label(
            text='Clear all download history?\nThis cannot be undone.',
            color=hex_c(C_WHITE), font_size=sp(15),
            halign='center', valign='middle',
        ))
        br = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(14))
        yes = FlatBtn(text='Yes, Clear', bg=C_DARK_RED, font_size=sp(15))
        no  = FlatBtn(text='Cancel',    bg=C_GRAY,     font_size=sp(15))
        br.add_widget(yes)
        br.add_widget(no)
        box.add_widget(br)
        p = Popup(
            title='Confirm',
            content=box,
            size_hint=(0.88, 0.42),
            background_color=hex_c(C_CARD),
        )

        def do_clear(*a):
            p.dismiss()
            history_clear()
            self._refresh()

        yes.bind(on_press=do_clear)
        no.bind(on_press=p.dismiss)
        p.open()

    def _clear(self, *a):
        history_clear()
        self._refresh()


# ═══════════════════════════════════════════════════════════
#  STUDIO SCREEN  (main TTS screen)
# ═══════════════════════════════════════════════════════════
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._audio    = None
        self.out_file  = None
        self.voice_sel = 'Male'    # default; toggled properly
        self._build()

    # ─────────────────────────────────────────────────────────
    def _build(self):
        root  = DarkPanel()
        outer = BoxLayout(orientation='vertical')

        # ══ HEADER BAR ══════════════════════════════════════
        hdr = BoxLayout(
            size_hint_y=None, height=dp(80),
            padding=[dp(16), dp(8)], spacing=dp(12),
        )
        card_bg(hdr, C_CARD, 0)

        # Logo image widget (or fallback)
        logo_box = BoxLayout(
            size_hint=(None, None),
            size=(dp(52), dp(52)),
        )
        logo_path = self._find_logo()
        if logo_path:
            logo_box.add_widget(KivyImage(
                source=logo_path,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(1, 1),
            ))
        else:
            logo_box.add_widget(Label(
                text='SS', font_size=sp(30), bold=True,
                color=hex_c(C_BLUE2),
                size_hint=(1, 1),
            ))
        hdr.add_widget(logo_box)

        tb = BoxLayout(orientation='vertical')
        t1 = Label(
            text='Titan AI Studio Pro',
            font_size=sp(19), bold=True,
            color=hex_c(C_WHITE),
            halign='left', valign='middle',
        )
        t1.bind(size=t1.setter('text_size'))
        t2 = Label(
            text='Your Personal Narrator, Always Free.',
            font_size=sp(12),
            color=hex_c(C_MUTED),
            halign='left', valign='middle',
        )
        t2.bind(size=t2.setter('text_size'))
        tb.add_widget(t1)
        tb.add_widget(t2)
        hdr.add_widget(tb)
        outer.add_widget(hdr)
        outer.add_widget(separator())

        # ══ SCROLLABLE CONTENT ══════════════════════════════
        scroll  = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(18), dp(18)],
            spacing=dp(18),
        )
        content.bind(minimum_height=content.setter('height'))

        # ── Language card ───────────────────────────────────
        lang_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(130),
            padding=[dp(16), dp(12)], spacing=dp(8),
        )
        card_bg(lang_card, C_CARD2, 16)
        lang_card.add_widget(lbl('Voice Language', 14, C_ACCENT, True, 28))
        self.lang_spin = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=dp(56),
            font_size=sp(17),
            color=(1, 1, 1, 1),
            background_color=hex_c(C_BLUE),
            background_normal='',
        )
        lang_card.add_widget(self.lang_spin)
        content.add_widget(lang_card)

        # ── Gender card ─────────────────────────────────────
        gender_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(120),
            padding=[dp(16), dp(12)], spacing=dp(8),
        )
        card_bg(gender_card, C_CARD2, 16)
        gender_card.add_widget(lbl('Voice Gender', 14, C_ACCENT, True, 28))
        gr = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(14))
        self._vbtns = {}
        for name in ['Male', 'Female']:
            b = FlatBtn(
                text=('♂ Male' if name == 'Male' else '♀ Female'),
                bg=C_BLUE,
                font_size=sp(16), bold=True,
            )
            # FIX: capture name correctly with default arg
            b.bind(on_press=lambda inst, n=name: self._pick_voice(n))
            gr.add_widget(b)
            self._vbtns[name] = b
        gender_card.add_widget(gr)
        content.add_widget(gender_card)
        # Set Male as default with correct highlight
        Clock.schedule_once(lambda dt: self._pick_voice('Male'), 0)

        # ── Speed card ──────────────────────────────────────
        speed_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(130),
            padding=[dp(16), dp(12)], spacing=dp(6),
        )
        card_bg(speed_card, C_CARD2, 16)
        speed_card.add_widget(lbl('Playback Speed', 14, C_ACCENT, True, 28))
        sr = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        sr.add_widget(lbl('Slow', 13, C_MUTED, False, 46))
        self.speed_slider = Slider(
            min=10, max=100, value=50, step=10,
        )
        self.speed_lbl = lbl('Speed: 50%', 13, C_CYAN, False, 46)
        self.speed_slider.bind(
            value=lambda i, v: setattr(
                self.speed_lbl, 'text', 'Speed: ' + str(int(v)) + '%'
            )
        )
        sr.add_widget(self.speed_slider)
        sr.add_widget(lbl('Fast', 13, C_MUTED, False, 46))
        speed_card.add_widget(sr)
        speed_card.add_widget(self.speed_lbl)
        content.add_widget(speed_card)

        # ── Text input card ─────────────────────────────────
        text_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(320),
            padding=[dp(16), dp(12)], spacing=dp(10),
        )
        card_bg(text_card, C_CARD2, 16)

        top_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        self.char_lbl = lbl('0 characters · 0 lines', 13, C_MUTED, False, 36)
        top_row.add_widget(self.char_lbl)
        imp = FlatBtn(
            text='📂 Import File',
            bg=C_BLUE2,
            size_hint_x=None, width=dp(140),
            font_size=sp(13),
        )
        imp.bind(on_press=self._import_file)
        top_row.add_widget(imp)
        text_card.add_widget(top_row)

        self.txt = TextInput(
            hint_text='Enter text to convert to voice...',
            multiline=True,
            size_hint=(1, 1),
            background_color=hex_c(C_SURFACE),
            foreground_color=hex_c(C_WHITE),
            hint_text_color=hex_c(C_MUTED),
            cursor_color=hex_c(C_ACCENT),
            font_size=sp(17),
            padding=[dp(14), dp(12)],
        )
        self.txt.bind(text=self._count)
        text_card.add_widget(self.txt)
        content.add_widget(text_card)

        # ── Status + progress ────────────────────────────────
        status_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(80),
            padding=[dp(16), dp(10)], spacing=dp(8),
        )
        card_bg(status_card, C_CARD2, 14)
        self.status_lbl = lbl('Ready to generate voice', 14, C_MUTED, False, 32)
        status_card.add_widget(self.status_lbl)
        self.prog = ProgressBar(
            max=100, value=0, size_hint_y=None, height=dp(10),
        )
        status_card.add_widget(self.prog)
        content.add_widget(status_card)

        # ── Generate button ──────────────────────────────────
        self.gen_btn = FlatBtn(
            text='⚡  Generate Audio',
            bg=C_BLUE,
            size_hint_y=None, height=dp(68),
            font_size=sp(18), bold=True,
        )
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        # ── Preview / Download row ───────────────────────────
        pd = BoxLayout(size_hint_y=None, height=dp(62), spacing=dp(14))
        self.play_btn = FlatBtn(
            text='▶ Preview Audio',
            bg=C_RED, font_size=sp(15),
            disabled=True,
        )
        self.dl_btn = FlatBtn(
            text='⬇ Download Voice',
            bg=C_GREEN, font_size=sp(15),
            disabled=True,
        )
        self.play_btn.bind(on_press=self._play)
        self.dl_btn.bind(on_press=self._download)
        pd.add_widget(self.play_btn)
        pd.add_widget(self.dl_btn)
        content.add_widget(pd)

        # ── History button ───────────────────────────────────
        hb = FlatBtn(
            text='📋  Download History',
            bg=C_PURPLE,
            size_hint_y=None, height=dp(58),
            font_size=sp(15),
        )
        hb.bind(on_press=self._go_hist)
        content.add_widget(hb)

        # ── Usage steps card ─────────────────────────────────
        ub = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(230),
            padding=[dp(16), dp(14)], spacing=dp(6),
        )
        card_bg(ub, C_CARD, 14)
        ub.add_widget(lbl('📖  How to Use', 15, C_ACCENT, True, 34))
        steps = [
            '1.  Select your Voice Language',
            '2.  Choose Gender: Male or Female',
            '3.  Adjust Speed with the slider',
            '4.  Type text or Import a file (TXT / PDF / DOCX)',
            '5.  Tap  ⚡ Generate Audio',
            '6.  Preview then Download your voice',
        ]
        for s in steps:
            ub.add_widget(lbl(s, 13, C_MUTED, False, 26))
        content.add_widget(ub)

        # Bottom padding
        content.add_widget(Widget(size_hint_y=None, height=dp(28)))

        scroll.add_widget(content)
        outer.add_widget(scroll)
        root.add_widget(outer)
        self.add_widget(root)

    def _find_logo(self):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI.png')
        return p if os.path.exists(p) else None

    # ── Screen transitions ───────────────────────────────────
    def on_enter(self, *a):
        self.opacity = 0
        Animation(opacity=1, duration=0.3, t='out_quad').start(self)

    def _go_hist(self, *a):
        self.manager.transition = SlideTransition(direction='left', duration=0.3)
        self.manager.current = 'history'

    # ── Voice gender selection (FIX: explicit assignment) ────
    def _pick_voice(self, name):
        self.voice_sel = name          # ← explicit string assignment
        for n, b in self._vbtns.items():
            b.set_bg(C_BLUE if n == name else C_CARD)
            b.bold = (n == name)

    # ── Character / line counter ─────────────────────────────
    def _count(self, inst, val):
        lines = len(val.splitlines()) if val.strip() else 0
        self.char_lbl.text = (
            str(len(val)) + ' characters  ·  '
            + str(lines) + ' lines'
        )

    # ── Import file ──────────────────────────────────────────
    def _import_file(self, *a):
        box = BoxLayout(
            orientation='vertical', padding=dp(16), spacing=dp(12)
        )
        box.add_widget(lbl('Select file type to import:', 15, C_WHITE, True, 40))
        br  = BoxLayout(size_hint_y=None, height=dp(62), spacing=dp(12))
        pop = [None]
        for ft in ['TXT', 'PDF', 'DOCX']:
            b = FlatBtn(text=ft, bg=C_BLUE, font_size=sp(16))
            b.bind(on_press=lambda x, t=ft, p=pop: self._open_chooser(t, p[0]))
            br.add_widget(b)
        box.add_widget(br)
        can = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None, height=dp(54))
        box.add_widget(can)
        p = Popup(
            title='Import File',
            content=box,
            size_hint=(0.92, 0.4),
            background_color=hex_c(C_CARD),
        )
        pop[0] = p
        can.bind(on_press=p.dismiss)
        p.open()

    def _open_chooser(self, ftype, prev):
        if prev:
            prev.dismiss()
        fm = {'TXT': ['*.txt'], 'PDF': ['*.pdf'], 'DOCX': ['*.docx']}
        sp_path = get_internal_storage_path()
        try:
            if ANDROID_ENV:
                sp_path = primary_external_storage_path() or sp_path
        except Exception:
            pass
        fc  = FileChooserListView(path=sp_path, filters=fm.get(ftype, ['*.*']))
        box = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        box.add_widget(fc)
        br  = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(10))
        sel = FlatBtn(text='Select', bg=C_GREEN, font_size=sp(15))
        can = FlatBtn(text='Cancel', bg=C_GRAY,  font_size=sp(15))
        br.add_widget(sel)
        br.add_widget(can)
        box.add_widget(br)
        p = Popup(
            title='Choose ' + ftype,
            content=box,
            size_hint=(0.95, 0.88),
            background_color=hex_c(C_CARD),
        )

        def do_sel(*a):
            if fc.selection:
                p.dismiss()
                self._read_file(fc.selection[0], ftype)

        sel.bind(on_press=do_sel)
        can.bind(on_press=p.dismiss)
        p.open()

    def _read_file(self, path, ftype):
        self.status_lbl.text = 'Reading file...'
        self.prog.value = 20

        def worker():
            try:
                if ftype == 'TXT':
                    text = read_txt(path)
                elif ftype == 'PDF':
                    text = read_pdf(path)
                else:
                    text = read_docx(path)
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: setattr(
                        self.status_lbl, 'text', 'Read error: ' + str(e)[:40]
                    )
                )
                return

            def apply(dt):
                if text.strip():
                    self.txt.text = text
                    self.status_lbl.text = 'File imported successfully!'
                    self.prog.value = 100
                else:
                    self.status_lbl.text = 'Could not read file. Try TXT format.'
                    self.prog.value = 0

            Clock.schedule_once(apply)

        threading.Thread(target=worker, daemon=True).start()

    # ── Button state helpers ─────────────────────────────────
    def _set_ready(self, ok=True):
        self.gen_btn.disabled  = False
        self.play_btn.disabled = not ok
        self.dl_btn.disabled   = not ok

    def _set_busy(self):
        self.gen_btn.disabled  = True
        self.play_btn.disabled = True
        self.dl_btn.disabled   = True

    def _upd(self, val, msg):
        self.prog.value       = val
        self.status_lbl.text  = msg

    # ── Generate audio ───────────────────────────────────────
    def _generate(self, *a):
        text = self.txt.text.strip()
        if not text:
            self._show_toast('Please enter some text first!')
            return
        ok, err = check_lang_text(text, self.lang_spin.text)
        if not ok:
            self._show_err(err)
            return
        self._set_busy()
        self._upd(0, 'Starting...')
        threading.Thread(target=self._worker, daemon=True).start()

    def _show_toast(self, msg):
        self.status_lbl.text = msg
        anim = (
            Animation(opacity=1, duration=0.1)
            + Animation(opacity=1, duration=2.0)
            + Animation(opacity=0.6, duration=0.4)
        )
        anim.start(self.status_lbl)

    def _show_err(self, msg):
        box = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(14))
        box.add_widget(Label(
            text=msg,
            color=hex_c(C_AMBER),
            font_size=sp(15),
            halign='center', valign='middle',
        ))
        ok = FlatBtn(text='OK', bg=C_BLUE, size_hint_y=None, height=dp(56))
        box.add_widget(ok)
        p = Popup(
            title='⚠ Language Mismatch',
            content=box,
            size_hint=(0.88, 0.42),
            background_color=hex_c(C_CARD),
        )
        ok.bind(on_press=p.dismiss)
        p.open()

    # ── TTS worker thread ────────────────────────────────────
    def _worker(self):
        try:
            from gtts import gTTS
            Clock.schedule_once(lambda dt: self._upd(20, 'Connecting to TTS service...'))
            lang  = LANGUAGES.get(self.lang_spin.text, 'en')
            tld   = VOICE_TLD.get(self.voice_sel, 'com')   # FIX: use voice_sel string
            slow  = int(self.speed_slider.value) <= 30
            label = self.voice_sel                           # already a plain string
            Clock.schedule_once(
                lambda dt: self._upd(50, 'Generating ' + label + ' voice...')
            )
            tts = gTTS(text=self.txt.text, lang=lang, tld=tld, slow=slow)
            out = os.path.join(
                App.get_running_app().user_data_dir, 'tts_out.mp3'
            )
            Clock.schedule_once(lambda dt: self._upd(80, 'Saving audio...'))
            tts.save(out)
            self.out_file = out
            Clock.schedule_once(lambda dt: self._on_done())
        except Exception as e:
            msg = str(e)
            Clock.schedule_once(lambda dt, m=msg: self._on_err(m))

    def _on_done(self):
        if self._audio:
            try:
                self._audio.stop()
                self._audio.unload()
            except Exception:
                pass
            self._audio = None
        self._audio = SoundLoader.load(self.out_file)
        self._upd(100, '✅  Audio ready!  Preview or Download.')
        self._set_ready(ok=True)
        # Animate progress bar reset after 1s
        Clock.schedule_once(
            lambda dt: Animation(value=0, duration=0.6, t='out_quad').start(self.prog),
            1.5,
        )

    def _on_err(self, msg):
        m = msg.lower()
        if any(k in m for k in ['network', 'connection', 'gaierror', 'timeout']):
            txt = '⚠ No internet! gTTS requires an active connection.'
        elif 'lang' in m:
            txt = '⚠ Language not supported by the TTS engine.'
        else:
            txt = '⚠ Error: ' + msg[:55]
        self._upd(0, txt)
        self._set_ready(ok=False)

    # ── Preview / stop ───────────────────────────────────────
    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = '▶ Preview Audio'
            self.play_btn.set_bg(C_RED)
        else:
            self._audio.play()
            self.play_btn.text = '⏹ Stop Preview'
            self.play_btn.set_bg(C_AMBER)

    # ── Download dialog ──────────────────────────────────────
    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self._show_toast('Generate audio first!')
            return

        if ANDROID_ENV:
            # Request storage permission before showing dialog
            try:
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                ])
            except Exception:
                pass

        dirs = get_save_dirs()
        if len(dirs) == 1:
            self._do_save(dirs[0][1], None)
            return

        box = BoxLayout(
            orientation='vertical', padding=dp(14), spacing=dp(10)
        )
        box.add_widget(Label(
            text='Where to save?',
            font_size=sp(16), bold=True,
            color=hex_c(C_WHITE),
            size_hint_y=None, height=dp(40),
        ))
        sv = ScrollView(size_hint=(1, 1))
        bb  = BoxLayout(
            orientation='vertical',
            size_hint_y=None, spacing=dp(10),
        )
        bb.bind(minimum_height=bb.setter('height'))
        pop = [None]

        for label, path in dirs:
            b = FlatBtn(
                text=label,
                bg=C_CARD2,
                size_hint_y=None, height=dp(72),
                font_size=sp(13),
            )
            b.bind(on_press=lambda x, p=path, pp=pop: self._do_save(p, pp[0]))
            bb.add_widget(b)

        sv.add_widget(bb)
        box.add_widget(sv)
        can = FlatBtn(
            text='Cancel', bg=C_GRAY,
            size_hint_y=None, height=dp(54),
        )
        box.add_widget(can)
        p = Popup(
            title='💾  Save Audio File',
            content=box,
            size_hint=(0.93, 0.76),
            background_color=hex_c(C_CARD),
        )
        pop[0] = p
        can.bind(on_press=p.dismiss)
        p.open()

    def _do_save(self, dest_dir, popup):
        if popup:
            popup.dismiss()
        fname = 'Titan_' + self.lang_spin.text + '_' + str(int(time.time())) + '.mp3'
        dest  = os.path.join(dest_dir, fname)
        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self._upd(100, '✅  Saved: ' + fname)
            history_save({
                'filename': fname,
                'path':     dest,
                'lang':     self.lang_spin.text,
                'voice':    self.voice_sel,
                'time':     time.strftime('%d %b %Y  %H:%M'),
            })
            # Success popup
            box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
            box.add_widget(Label(
                text='✅  Saved Successfully!\n\n' + fname + '\n\nLocation:\n' + dest_dir,
                color=hex_c(C_WHITE), font_size=sp(14),
                halign='center', valign='middle',
            ))
            ok = FlatBtn(text='Great!', bg=C_GREEN, size_hint_y=None, height=dp(58))
            box.add_widget(ok)
            p = Popup(
                title='Download Complete',
                content=box,
                size_hint=(0.9, 0.52),
                background_color=hex_c(C_CARD),
            )
            ok.bind(on_press=p.dismiss)
            p.open()
        except PermissionError:
            self._show_err(
                'Permission denied!\n\nPlease allow storage access\n'
                'in your phone Settings → App Permissions.'
            )
        except Exception as e:
            self._upd(0, 'Save failed: ' + str(e)[:45])


# ═══════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════
class TitanApp(App):
    def build(self):
        self.title = 'Titan AI Studio Pro'
        sm = ScreenManager(transition=FadeTransition(duration=0.35))
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(StudioScreen(name='studio'))
        sm.add_widget(HistoryScreen(name='history'))
        if ANDROID_ENV:
            Clock.schedule_once(self._ask_perms, 0.8)
        return sm

    def _ask_perms(self, *a):
        try:
            request_permissions([
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])
        except Exception:
            pass


if __name__ == '__main__':
    TitanApp().run()
