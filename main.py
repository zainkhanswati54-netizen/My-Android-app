import os
import threading
import time
import shutil
import json

try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    ANDROID_ENV = True
except Exception:
    ANDROID_ENV = False

from kivy.config import Config
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import (Color, Rectangle, RoundedRectangle,
                            Ellipse, Line, Triangle)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

# ── Colors ──────────────────────────────────────────────────────────────────
C_BG     = '#020817'
C_CARD   = '#0F172A'
C_CARD2  = '#1E293B'
C_BLUE   = '#2563EB'
C_BLUE2  = '#3B82F6'
C_ACCENT = '#38BDF8'
C_GREEN  = '#22C55E'
C_RED    = '#EF4444'
C_PURPLE = '#7C3AED'
C_CYAN   = '#0EA5E9'
C_GRAY   = '#475569'
C_WHITE  = '#F1F5F9'
C_MUTED  = '#64748B'
C_AMBER  = '#F59E0B'
C_LOGO_BLUE = '#3B82F6'   # SS logo blue
C_LOGO_BG   = '#020817'   # SS logo dark background

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

# FIX: Correct voice profiles - Male=com, Female=co.uk
VOICE_PROFILES = {
    'Male':   {'tld': 'com',   'slow': False},
    'Female': {'tld': 'co.uk', 'slow': False},
}

LATIN_ONLY = {'English', 'French', 'Spanish', 'German', 'Turkish'}


# ── Helpers ──────────────────────────────────────────────────────────────────
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
            json.dump(data[:100], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_internal_storage():
    """Get best internal storage path."""
    if ANDROID_ENV:
        # Try /sdcard first (Android internal)
        for p in ['/sdcard', '/storage/emulated/0']:
            if os.path.exists(p):
                return p
        return '/sdcard'
    return os.path.expanduser('~')


def get_save_dirs():
    """
    FIX: Always show internal storage options first.
    SD Card options only if actually available.
    """
    dirs = []
    if ANDROID_ENV:
        base = get_internal_storage()
        dirs.append(('Internal Storage\n' + base, base))
        dl = os.path.join(base, 'Download')
        dirs.append(('Downloads Folder\n' + dl, dl))
        music = os.path.join(base, 'Music')
        dirs.append(('Music Folder\n' + music, music))
        docs = os.path.join(base, 'Documents')
        dirs.append(('Documents Folder\n' + docs, docs))
        # SD Card - only if different and accessible
        try:
            ext = primary_external_storage_path()
            if ext and ext != base and os.path.exists(ext):
                dirs.append(('SD Card\n' + ext, ext))
                dirs.append(('SD Card Downloads\n' + os.path.join(ext, 'Download'),
                              os.path.join(ext, 'Download')))
        except Exception:
            pass
    else:
        home = os.path.expanduser('~')
        dirs.append(('Home\n' + home, home))
        for name in ['Downloads', 'Desktop', 'Documents', 'Music']:
            p = os.path.join(home, name)
            if os.path.exists(p):
                dirs.append((name + '\n' + p, p))
    return dirs


def check_lang_text(text, lang):
    if lang in LATIN_ONLY:
        return True, ''
    has_latin = any(c.isalpha() and ord(c) < 128 for c in text)
    if not has_latin:
        return True, ''
    checks = {
        'Chinese':  (lambda t: any('\u4e00' <= c <= '\u9fff' for c in t),
                     '❌ Chinese selected!\nPlease write in Chinese characters.\n(Aap ko Chinese likhna hoga)'),
        'Japanese': (lambda t: any('\u3040' <= c <= '\u30ff' for c in t) or
                                any('\u4e00' <= c <= '\u9fff' for c in t),
                     '❌ Japanese selected!\nPlease write in Japanese characters.\n(Aap ko Japanese likhna hoga)'),
        'Korean':   (lambda t: any('\uac00' <= c <= '\ud7a3' for c in t),
                     '❌ Korean selected!\nPlease write in Korean characters.\n(Aap ko Korean likhna hoga)'),
        'Arabic':   (lambda t: any('\u0600' <= c <= '\u06ff' for c in t),
                     '❌ Arabic selected!\nPlease write in Arabic script.\n(Aap ko Arabic likhna hoga)'),
        'Urdu':     (lambda t: any('\u0600' <= c <= '\u06ff' for c in t),
                     '❌ Urdu selected!\nPlease write in Urdu script.\n(Aap ko Urdu likhna hoga)'),
        'Hindi':    (lambda t: any('\u0900' <= c <= '\u097f' for c in t),
                     '❌ Hindi selected!\nPlease write in Devanagari script.\n(Aap ko Hindi mein likhna hoga)'),
        'Russian':  (lambda t: any('\u0400' <= c <= '\u04ff' for c in t),
                     '❌ Russian selected!\nPlease write in Cyrillic script.\n(Aap ko Russian mein likhna hoga)'),
    }
    if lang in checks:
        fn, msg = checks[lang]
        if not fn(text):
            return False, msg
    return True, ''


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
        import re
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
        import zipfile, re
        with zipfile.ZipFile(path) as z:
            if 'word/document.xml' in z.namelist():
                xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
                return ' '.join(re.sub(r'<[^>]+>', ' ', xml).split())
        return ''
    except Exception:
        return ''


# ── Logo Widget: SS logo (blue on dark bg) ───────────────────────────────────
class TitanLogo(Widget):
    """
    Draws the SS logo: dark rounded square background + blue SS shape.
    Uses Kivy canvas mesh/bezier approach via RoundedRectangle + cutouts.
    We draw it as a Label with custom font-size 'SS' styled text for simplicity,
    but with proper canvas background to match the real logo.
    """
    def __init__(self, size_val=80, **kw):
        super().__init__(**kw)
        self.size_val = size_val
        self.size_hint = (None, None)
        self.size = (size_val, size_val)
        self.bind(pos=self._draw, size=self._draw)
        # Overlay label for SS text styled to match logo
        self._lbl = Label(
            text='SS',
            font_size=str(int(size_val * 0.52)) + 'sp',
            bold=True,
            color=get_color_from_hex(C_LOGO_BLUE),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._lbl)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *a):
        self._lbl.pos  = self.pos
        self._lbl.size = self.size
        self._lbl.font_size = str(int(self.size_val * 0.52)) + 'sp'
        self._draw()

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            # Dark rounded square background
            Color(*get_color_from_hex(C_LOGO_BG))
            RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[self.size_val * 0.18]
            )
            # Blue border/glow ring (subtle)
            Color(*get_color_from_hex(C_LOGO_BLUE)[:3], 0.18)
            Line(
                rounded_rectangle=(
                    self.x + 2, self.y + 2,
                    self.width - 4, self.height - 4,
                    self.size_val * 0.16,
                ),
                width=2,
            )


# ── Styled helpers ───────────────────────────────────────────────────────────
class FlatBtn(Button):
    def __init__(self, bg=C_BLUE, radius=16, **kw):
        super().__init__(**kw)
        self.bg     = bg
        self._radius = radius
        self.background_normal = ''
        self.background_down   = ''
        self.background_color  = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bind(pos=self._draw, size=self._draw)

    def set_bg(self, color):
        self.bg = color
        self._draw()

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])

    def on_press(self):
        # Scale + opacity animation on press
        anim = (Animation(opacity=0.55, duration=0.07) +
                Animation(opacity=1.0,  duration=0.15))
        anim.start(self)


class DarkPanel(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*get_color_from_hex(C_BG))
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos  = self.pos
        self._rect.size = self.size


def card_bg(widget, color=C_CARD, radius=14):
    with widget.canvas.before:
        Color(*get_color_from_hex(color))
        rr = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])

    def upd(w, *a, r=rr):
        r.pos  = w.pos
        r.size = w.size
    widget.bind(pos=upd, size=upd)


def lbl(txt, size=16, color=C_MUTED, bold=False, h=40):
    return Label(
        text=txt, font_size=str(size) + 'sp', bold=bold,
        color=get_color_from_hex(color),
        size_hint_y=None, height=h,
        halign='left', valign='middle',
    )


# ── Loading Screen ────────────────────────────────────────────────────────────
class LoadingScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = DarkPanel()

        # Logo - SS icon (big, centered)
        logo_wrap = FloatLayout(
            pos_hint={'center_x': 0.5, 'center_y': 0.60},
            size_hint=(None, None),
            size=(130, 130),
            opacity=0,
        )
        self.logo_widget = TitanLogo(size_val=130)
        logo_wrap.add_widget(self.logo_widget)
        self.logo_wrap = logo_wrap
        root.add_widget(logo_wrap)

        self.title_lbl = Label(
            text='Titan AI Studio Pro', font_size='28sp', bold=True,
            color=get_color_from_hex(C_WHITE),
            pos_hint={'center_x': 0.5, 'center_y': 0.37},
            opacity=0,
        )
        root.add_widget(self.title_lbl)

        self.sub_lbl = Label(
            text='Your Personal Narrator, Always Free.',
            font_size='16sp', color=get_color_from_hex(C_MUTED),
            pos_hint={'center_x': 0.5, 'center_y': 0.29},
            opacity=0,
        )
        root.add_widget(self.sub_lbl)

        self.dot_lbl = Label(
            text='Loading....', font_size='16sp',
            color=get_color_from_hex(C_BLUE2),
            pos_hint={'center_x': 0.5, 'center_y': 0.20},
            opacity=0,
        )
        root.add_widget(self.dot_lbl)
        self.add_widget(root)
        self._d = 0

    def on_enter(self, *a):
        self.logo_wrap.opacity = 0
        self.title_lbl.opacity = 0
        self.sub_lbl.opacity   = 0
        self.dot_lbl.opacity   = 0

        # Fade + slight scale animation
        Animation(opacity=1, duration=0.7).start(self.logo_wrap)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.title_lbl), 0.5)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.sub_lbl), 0.8)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.dot_lbl), 1.0)
        self._ev = Clock.schedule_interval(self._tick, 0.5)
        Clock.schedule_once(self._go, 3.5)

    def on_leave(self, *a):
        if hasattr(self, '_ev'):
            self._ev.cancel()

    def _tick(self, dt):
        self._d = (self._d + 1) % 4
        self.dot_lbl.text = 'Loading' + '.' * (self._d + 1)

    def _go(self, dt):
        self.manager.transition = FadeTransition(duration=0.5)
        self.manager.current = 'studio'


# ── History Screen ────────────────────────────────────────────────────────────
class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._sounds = []
        self._build()

    def _build(self):
        root = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=[20, 20], spacing=16)

        # Header with logo
        hdr = BoxLayout(size_hint_y=None, height=dp(80), spacing=14)
        card_bg(hdr, C_CARD, 0)
        back = FlatBtn(text='← Back', bg=C_GRAY, size_hint_x=None,
                       width=dp(120), font_size='17sp', bold=True)
        back.bind(on_press=self._go_back)
        hdr.add_widget(back)
        hdr.add_widget(Label(
            text='Download History', font_size='24sp', bold=True,
            color=get_color_from_hex(C_ACCENT),
        ))
        # Logo in header
        logo_h = TitanLogo(size_val=54)
        logo_h.size_hint = (None, None)
        logo_h.size = (54, 54)
        hdr.add_widget(logo_h)
        outer.add_widget(hdr)

        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical', size_hint_y=None, spacing=14, padding=[0, 8])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)

        clr = FlatBtn(text='🗑  Clear All History', bg='#7F1D1D',
                      size_hint_y=None, height=dp(68), font_size='18sp', bold=True)
        clr.bind(on_press=self._clear)
        outer.add_widget(clr)

        root.add_widget(outer)
        self.add_widget(root)

    def _go_back(self, *a):
        self.manager.transition = SlideTransition(direction='right', duration=0.35)
        self.manager.current = 'studio'

    def on_enter(self, *a):
        # Slide in animation
        self.opacity = 0
        self.x = 200
        anim = Animation(opacity=1, x=0, duration=0.3, t='out_cubic')
        anim.start(self)
        self._refresh()

    def _refresh(self):
        self.list_box.clear_widgets()
        data = history_load()
        if not data:
            empty = Label(
                text='No downloads yet.\nGenerate and download audio to see history.',
                color=get_color_from_hex(C_MUTED),
                size_hint_y=None, height=dp(100),
                font_size='17sp', halign='center',
            )
            self.list_box.add_widget(empty)
            return

        for i, entry in enumerate(data):
            row = BoxLayout(size_hint_y=None, height=dp(105),
                            spacing=12, padding=[16, 8], opacity=0)
            card_bg(row, C_CARD2, 16)

            info = BoxLayout(orientation='vertical', size_hint_x=0.80)
            fname_lbl = Label(
                text=entry.get('filename', 'unknown'),
                font_size='15sp', bold=True,
                color=get_color_from_hex(C_WHITE),
                halign='left', valign='middle',
                size_hint_y=None, height=dp(42),
            )
            fname_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
            info.add_widget(fname_lbl)
            info.add_widget(Label(
                text=entry.get('lang', '') + '   ' +
                     entry.get('voice', '') + '   ' +
                     entry.get('time', ''),
                font_size='14sp', color=get_color_from_hex(C_GREEN),
                halign='left', valign='middle',
                size_hint_y=None, height=dp(36),
            ))
            row.add_widget(info)

            fp = entry.get('path', '')
            if os.path.exists(fp):
                pb = FlatBtn(text='▶ PLAY', bg=C_GREEN,
                             size_hint_x=None, width=dp(90), font_size='15sp', bold=True)
                pb.bind(on_press=lambda *a, p=fp: self._play(p))
                row.add_widget(pb)

            self.list_box.add_widget(row)
            # Staggered slide-in animation for each card
            delay = 0.05 + i * 0.07
            def _animate(dt, w=row):
                w.x = 60
                anim = Animation(opacity=1, x=0, duration=0.3, t='out_cubic')
                anim.start(w)
            Clock.schedule_once(_animate, delay)

    def _play(self, path):
        snd = SoundLoader.load(path)
        if snd:
            self._sounds.append(snd)
            snd.play()

    def _clear(self, *a):
        # Confirm popup
        box = BoxLayout(orientation='vertical', padding=20, spacing=16)
        box.add_widget(Label(
            text='Clear all download history?\n(Files will NOT be deleted)',
            color=get_color_from_hex(C_WHITE), font_size='16sp',
            halign='center',
        ))
        br = BoxLayout(size_hint_y=None, height=dp(65), spacing=14)
        yes = FlatBtn(text='Yes, Clear', bg=C_RED, font_size='16sp', bold=True)
        no  = FlatBtn(text='Cancel', bg=C_GRAY, font_size='16sp')
        br.add_widget(yes)
        br.add_widget(no)
        box.add_widget(br)
        p = Popup(title='Confirm Clear', content=box,
                  size_hint=(0.88, 0.40),
                  background_color=get_color_from_hex(C_CARD))
        def do_clear(*a):
            p.dismiss()
            try:
                with open(history_path(), 'w') as f:
                    json.dump([], f)
            except Exception:
                pass
            self._refresh()
        yes.bind(on_press=do_clear)
        no.bind(on_press=p.dismiss)
        p.open()


# ── Studio Screen ─────────────────────────────────────────────────────────────
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._audio   = None
        self.out_file = None
        self.voice_sel = 'Male'
        self._build()

    def _build(self):
        root   = DarkPanel()
        outer  = BoxLayout(orientation='vertical')

        # ── Header ──────────────────────────────────────────────────────────
        hdr = BoxLayout(size_hint_y=None, height=dp(82), padding=[16, 10], spacing=14)
        card_bg(hdr, C_CARD, 0)

        # Logo (SS icon)
        logo = TitanLogo(size_val=56)
        logo.size_hint = (None, None)
        logo.size = (56, 56)
        hdr.add_widget(logo)

        tb = BoxLayout(orientation='vertical')
        t1 = Label(
            text='Titan AI Studio Pro', font_size='21sp', bold=True,
            color=get_color_from_hex(C_WHITE),
            halign='left', valign='middle',
        )
        t1.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        t2 = Label(
            text='Your Personal Narrator, Always Free.',
            font_size='13sp', color=get_color_from_hex(C_MUTED),
            halign='left', valign='middle',
        )
        t2.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        tb.add_widget(t1)
        tb.add_widget(t2)
        hdr.add_widget(tb)
        outer.add_widget(hdr)

        # ── Scrollable Content ───────────────────────────────────────────────
        scroll  = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical', size_hint_y=None,
            padding=[20, 18], spacing=18,
        )
        content.bind(minimum_height=content.setter('height'))

        # Language
        content.add_widget(lbl('🌐  Voice Language', 17, C_WHITE, True, 42))
        self.lang_spin = Spinner(
            text='English', values=list(LANGUAGES.keys()),
            size_hint_y=None, height=dp(68), font_size='19sp',
            color=(1, 1, 1, 1),
            background_color=get_color_from_hex(C_BLUE),
        )
        content.add_widget(self.lang_spin)

        # Gender
        content.add_widget(lbl('🎙  Gender', 17, C_WHITE, True, 42))
        gr = BoxLayout(size_hint_y=None, height=dp(70), spacing=16)
        self._vbtns = {}
        for name in VOICE_PROFILES:
            b = FlatBtn(text=name, bg=C_BLUE, font_size='19sp', bold=True)
            b.bind(on_press=lambda *a, n=name: self._pick_voice(n))
            gr.add_widget(b)
            self._vbtns[name] = b
        content.add_widget(gr)
        self._pick_voice('Male')

        # Speed
        content.add_widget(lbl('⚡  Speed', 17, C_WHITE, True, 42))
        sr = BoxLayout(size_hint_y=None, height=dp(52), spacing=12)
        sr.add_widget(lbl('Slow', 15, C_MUTED, False, 52))
        self.speed_slider = Slider(min=10, max=100, value=50, step=10)
        self.speed_lbl = lbl('Speed: 50%', 15, C_ACCENT, False, 52)
        self.speed_slider.bind(value=lambda i, v: setattr(
            self.speed_lbl, 'text', 'Speed: ' + str(int(v)) + '%'))
        sr.add_widget(self.speed_slider)
        sr.add_widget(lbl('Fast', 15, C_MUTED, False, 52))
        content.add_widget(sr)
        content.add_widget(self.speed_lbl)

        # Text area row
        cr = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        self.char_lbl = lbl('Input Text: 0 characters (0 lines)', 14, C_MUTED, False, 50)
        cr.add_widget(self.char_lbl)
        imp = FlatBtn(text='📂 Import File', bg=C_BLUE2,
                      size_hint_x=None, width=dp(155), font_size='15sp')
        imp.bind(on_press=self._import_file)
        cr.add_widget(imp)
        content.add_widget(cr)

        self.txt = TextInput(
            hint_text='Enter text to synthesize here...',
            multiline=True, size_hint_y=None, height=dp(220),
            background_color=get_color_from_hex(C_CARD2),
            foreground_color=get_color_from_hex(C_WHITE),
            hint_text_color=get_color_from_hex(C_MUTED),
            cursor_color=get_color_from_hex(C_ACCENT),
            font_size='19sp', padding=[18, 16],
        )
        self.txt.bind(text=self._count)
        content.add_widget(self.txt)

        # Status
        self.status_lbl = lbl('Ready to generate!', 15, C_MUTED, False, 42)
        content.add_widget(self.status_lbl)
        self.prog = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(16))
        content.add_widget(self.prog)

        # Preview / Download buttons
        pd = BoxLayout(size_hint_y=None, height=dp(74), spacing=16)
        self.play_btn = FlatBtn(text='▶ Preview Audio', bg=C_RED,
                                font_size='17sp', bold=True, disabled=True)
        self.dl_btn = FlatBtn(text='⬇ Download Voice', bg=C_GREEN,
                               font_size='17sp', bold=True, disabled=True)
        self.play_btn.bind(on_press=self._play)
        self.dl_btn.bind(on_press=self._download)
        pd.add_widget(self.play_btn)
        pd.add_widget(self.dl_btn)
        content.add_widget(pd)

        # Generate button
        self.gen_btn = FlatBtn(
            text='🎵  Generate Audio', bg=C_BLUE,
            size_hint_y=None, height=dp(78), font_size='20sp', bold=True)
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        # History button
        hb = FlatBtn(text='📋  Download History', bg=C_PURPLE,
                     size_hint_y=None, height=dp(68), font_size='18sp', bold=True)
        hb.bind(on_press=self._go_hist)
        content.add_widget(hb)

        # Usage steps card (at bottom - user scrolls to see)
        ub = BoxLayout(orientation='vertical', size_hint_y=None,
                       height=dp(240), padding=[18, 16])
        card_bg(ub, C_CARD2, 16)
        ub.add_widget(lbl('📖  Usage Steps:', 17, C_WHITE, True, 36))
        for s in [
            '1. Select Voice Language from dropdown',
            '2. Choose Gender: Male or Female',
            '3. Adjust Speed using the slider',
            '4. Type or Import your text file (TXT/PDF/DOCX)',
            '5. Tap Generate Audio button',
            '6. Preview then Download your voice',
        ]:
            ub.add_widget(lbl(s, 14, C_MUTED, False, 30))
        content.add_widget(ub)
        content.add_widget(Label(size_hint_y=None, height=dp(30)))

        scroll.add_widget(content)
        outer.add_widget(scroll)
        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        Animation(opacity=1, duration=0.4, t='out_quad').start(self)

    def _go_hist(self, *a):
        self.manager.transition = SlideTransition(direction='left', duration=0.35)
        self.manager.current = 'history'

    def _pick_voice(self, name):
        self.voice_sel = name
        for n, b in self._vbtns.items():
            b.set_bg(C_BLUE if n == name else C_CARD2)

    def _count(self, inst, val):
        lines = len(val.splitlines()) if val.strip() else 0
        self.char_lbl.text = (
            'Input Text: ' + str(len(val)) +
            ' characters (' + str(lines) + ' lines)')

    def _import_file(self, *a):
        box = BoxLayout(orientation='vertical', padding=16, spacing=12)
        box.add_widget(lbl('Select file type:', 17, C_WHITE, True, 44))
        br = BoxLayout(size_hint_y=None, height=dp(68), spacing=14)
        pop = [None]
        for ft in ['TXT', 'PDF', 'DOCX']:
            b = FlatBtn(text=ft, bg=C_BLUE, font_size='17sp', bold=True)
            b.bind(on_press=lambda x, t=ft, p=pop: self._open_chooser(t, p[0]))
            br.add_widget(b)
        box.add_widget(br)
        can = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None, height=dp(58), font_size='16sp')
        box.add_widget(can)
        p = Popup(title='Import File', content=box,
                  size_hint=(0.9, 0.40),
                  background_color=get_color_from_hex(C_CARD))
        pop[0] = p
        can.bind(on_press=p.dismiss)
        p.open()

    def _open_chooser(self, ftype, prev):
        if prev:
            prev.dismiss()
        fm = {'TXT': ['*.txt'], 'PDF': ['*.pdf'], 'DOCX': ['*.docx']}
        sp = get_internal_storage() if ANDROID_ENV else os.path.expanduser('~')
        fc = FileChooserListView(path=sp, filters=fm.get(ftype, ['*.*']))
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(fc)
        br = BoxLayout(size_hint_y=None, height=dp(65), spacing=12)
        sel = FlatBtn(text='✓ Select', bg=C_GREEN, font_size='17sp', bold=True)
        can = FlatBtn(text='Cancel', bg=C_GRAY, font_size='17sp')
        br.add_widget(sel)
        br.add_widget(can)
        box.add_widget(br)
        p = Popup(title='Choose ' + ftype, content=box,
                  size_hint=(0.95, 0.90),
                  background_color=get_color_from_hex(C_CARD))

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
                Clock.schedule_once(lambda dt: setattr(
                    self.status_lbl, 'text', 'Read error: ' + str(e)[:40]))
                return

            def apply(dt):
                if text.strip():
                    self.txt.text = text
                    self.status_lbl.text = '✓ File imported successfully!'
                    self.prog.value = 100
                else:
                    self.status_lbl.text = 'Could not read file. Try TXT format.'
                    self.prog.value = 0
            Clock.schedule_once(apply)
        threading.Thread(target=worker, daemon=True).start()

    def _set_ready(self, ok=True):
        self.gen_btn.disabled  = False
        self.play_btn.disabled = not ok
        self.dl_btn.disabled   = not ok

    def _set_busy(self):
        self.gen_btn.disabled  = True
        self.play_btn.disabled = True
        self.dl_btn.disabled   = True

    def _upd(self, val, msg):
        self.prog.value = val
        self.status_lbl.text = msg

    def _generate(self, *a):
        text = self.txt.text.strip()
        if not text:
            self.status_lbl.text = 'Please enter text first!'
            return
        ok, err = check_lang_text(text, self.lang_spin.text)
        if not ok:
            self._show_err(err)
            return
        self._set_busy()
        self._upd(0, 'Starting...')
        threading.Thread(target=self._worker, daemon=True).start()

    def _show_err(self, msg):
        box = BoxLayout(orientation='vertical', padding=20, spacing=14)
        box.add_widget(Label(
            text=msg, color=get_color_from_hex(C_AMBER),
            font_size='16sp', halign='center',
        ))
        ok = FlatBtn(text='OK', bg=C_BLUE, size_hint_y=None, height=dp(62),
                     font_size='17sp', bold=True)
        box.add_widget(ok)
        p = Popup(title='⚠ Language Mismatch', content=box,
                  size_hint=(0.90, 0.42),
                  background_color=get_color_from_hex(C_CARD))
        ok.bind(on_press=p.dismiss)
        p.open()

    def _worker(self):
        try:
            from gtts import gTTS
            Clock.schedule_once(lambda dt: self._upd(20, 'Connecting to server...'))
            lang = LANGUAGES.get(self.lang_spin.text, 'en')

            # FIX: Properly get voice profile by current selection
            voice_name = self.voice_sel  # 'Male' or 'Female'
            prof = VOICE_PROFILES[voice_name]
            slow = int(self.speed_slider.value) <= 40

            Clock.schedule_once(
                lambda dt: self._upd(50, 'Generating ' + voice_name + ' voice...'))

            # FIX: Use correct tld for gender
            tts = gTTS(text=self.txt.text, lang=lang, tld=prof['tld'], slow=slow)
            out = os.path.join(App.get_running_app().user_data_dir, 'tts_out.mp3')
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
        self._upd(100, '✓ Audio ready! Preview or Download.')
        self._set_ready(ok=True)
        self.play_btn.text = '▶ Preview Audio'

    def _on_err(self, msg):
        m = msg.lower()
        if any(k in m for k in ['network', 'connection', 'gaierror', 'timeout']):
            txt = '❌ No internet! gTTS needs active internet.'
        elif 'lang' in m:
            txt = '❌ This language is not supported.'
        else:
            txt = '❌ Error: ' + msg[:50]
        self._upd(0, txt)
        self._set_ready(ok=False)

    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = '▶ Preview Audio'
        else:
            self._audio.play()
            self.play_btn.text = '⏹ Stop Preview'

    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status_lbl.text = 'Generate audio first!'
            return

        # FIX: Request storage permission before saving
        if ANDROID_ENV:
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

        box = BoxLayout(orientation='vertical', padding=14, spacing=12)
        box.add_widget(lbl('📁  Where to save?', 18, C_WHITE, True, 46))
        sv = ScrollView(size_hint=(1, 1))
        bb = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
        bb.bind(minimum_height=bb.setter('height'))
        pop = [None]
        for name, path in dirs:
            b = FlatBtn(text=name, bg=C_CARD2,
                        size_hint_y=None, height=dp(76), font_size='15sp', bold=True)
            b.bind(on_press=lambda x, p=path, pp=pop: self._do_save(p, pp[0]))
            bb.add_widget(b)
        sv.add_widget(bb)
        box.add_widget(sv)
        can = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None,
                      height=dp(60), font_size='17sp')
        box.add_widget(can)
        p = Popup(title='Save Audio File', content=box,
                  size_hint=(0.92, 0.75),
                  background_color=get_color_from_hex(C_CARD))
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
            self.status_lbl.text = 'Saved: ' + fname
            history_save({
                'filename': fname,
                'path':     dest,
                'lang':     self.lang_spin.text,
                'voice':    self.voice_sel,
                'time':     time.strftime('%d %b %Y  %H:%M'),
            })
            box = BoxLayout(orientation='vertical', padding=20, spacing=16)
            box.add_widget(Label(
                text='✅ Saved!\n\n' + fname + '\n\n📂 ' + dest_dir,
                color=get_color_from_hex(C_WHITE),
                font_size='15sp', halign='center',
            ))
            ok = FlatBtn(text='Great!', bg=C_GREEN, size_hint_y=None,
                         height=dp(65), font_size='18sp', bold=True)
            box.add_widget(ok)
            p = Popup(title='✓ Download Complete', content=box,
                      size_hint=(0.90, 0.52),
                      background_color=get_color_from_hex(C_CARD))
            ok.bind(on_press=p.dismiss)
            p.open()
        except Exception as e:
            self.status_lbl.text = 'Save failed: ' + str(e)[:45]


# ── App ───────────────────────────────────────────────────────────────────────
class TitanApp(App):
    def build(self):
        self.title = 'Titan AI Studio Pro'
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(StudioScreen(name='studio'))
        sm.add_widget(HistoryScreen(name='history'))
        if ANDROID_ENV:
            Clock.schedule_once(self._ask_perms, 0.5)
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
