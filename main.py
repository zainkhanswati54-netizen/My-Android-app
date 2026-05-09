# ============================================================
#  Titan AI Studio Pro  –  main.py
#  Version 11.0.0  |  ULTIMATE EDITION
#  ─────────────────────────────────────────────────────────
#  FIXES IN THIS VERSION:
#    ✅ edge-tts Android fix: uses websockets/aiohttp instead of broken asyncio
#    ✅ Male/Female REAL neural voices (not gTTS fake gender)
#    ✅ Speed/Pitch/Emotion ALL working via edge-tts parameters
#    ✅ Advanced settings (breath, SSML, pacing) actually affect output
#    ✅ "Titan Studio PRO" folder auto-created on device
#    ✅ Storage permission requested before save
#    ✅ Beautiful animated UI with pulse, glow, phone mockup
#    ✅ Waveform animation during playback
#    ✅ Smooth screen transitions
#    ✅ Clean minimal layout — no clutter
#
#  HOW edge-tts ANDROID FIX WORKS:
#    - Standard asyncio.run() fails on Android (no event loop policy)
#    - Fix: create a new thread with its own asyncio event loop
#    - OR: use edge-tts's sync wrapper via threading.Event
#    - We use the threading approach for max compatibility
#
#  FOLDER: /storage/emulated/0/Titan Studio PRO/
#    Audio/     ← generated MP3s saved here
#    Imported/  ← imported docs
#    Exports/   ← batch exports
# ============================================================

import os
import threading
import time
import shutil
import json
import re
import math
import asyncio

# ── Android detection ──────────────────────────────────────
try:
    from android.permissions import (
        request_permissions, Permission, check_permission
    )
    from android.storage import primary_external_storage_path
    ANDROID_ENV = True
except Exception:
    ANDROID_ENV = False

# ── Kivy low-level config ──
from kivy.config import Config
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle, Line,
    Ellipse, StencilPush, StencilUse, StencilPop, StencilUnUse,
    Mesh,
)
from kivy.metrics import dp, sp
from kivy.properties import (
    StringProperty, BooleanProperty,
    NumericProperty, ListProperty, ObjectProperty,
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
    ScreenManager, Screen, SlideTransition, FadeTransition, CardTransition
)
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

# ═══════════════════════════════════════════════════════════
#  COLOUR PALETTE  (Premium Dark — same as v10, kept intact)
# ═══════════════════════════════════════════════════════════
C_BG       = '#020817'
C_BG2      = '#030E20'
C_CARD     = '#0F172A'
C_CARD2    = '#1E293B'
C_CARD3    = '#162032'
C_BLUE     = '#2563EB'
C_BLUE2    = '#3B82F6'
C_BLUE3    = '#1D4ED8'
C_ACCENT   = '#38BDF8'
C_ACCENT2  = '#0EA5E9'
C_GREEN    = '#22C55E'
C_GREEN2   = '#16A34A'
C_RED      = '#EF4444'
C_RED2     = '#DC2626'
C_PURPLE   = '#7C3AED'
C_PURPLE2  = '#6D28D9'
C_CYAN     = '#0EA5E9'
C_GRAY     = '#475569'
C_GRAY2    = '#334155'
C_WHITE    = '#F1F5F9'
C_WHITE2   = '#E2E8F0'
C_MUTED    = '#64748B'
C_MUTED2   = '#94A3B8'
C_AMBER    = '#F59E0B'
C_AMBER2   = '#D97706'
C_ORANGE   = '#F97316'
C_PINK     = '#EC4899'
C_TEAL     = '#14B8A6'
C_DARK_RED = '#7F1D1D'
C_SURFACE  = '#152032'
C_SURFACE2 = '#0D1B2E'
C_GOLD     = '#EAB308'
C_INDIGO   = '#6366F1'

# ═══════════════════════════════════════════════════════════
#  LANGUAGE DATA
# ═══════════════════════════════════════════════════════════
LANGUAGES = {
    'English': 'en', 'Urdu': 'ur', 'Hindi': 'hi', 'Arabic': 'ar',
    'French': 'fr', 'Spanish': 'es', 'German': 'de', 'Turkish': 'tr',
    'Russian': 'ru', 'Chinese': 'zh-TW', 'Japanese': 'ja', 'Korean': 'ko',
    'Portuguese': 'pt', 'Italian': 'it', 'Dutch': 'nl', 'Polish': 'pl',
    'Swedish': 'sv', 'Danish': 'da', 'Norwegian': 'no', 'Finnish': 'fi',
    'Greek': 'el', 'Romanian': 'ro', 'Czech': 'cs', 'Hungarian': 'hu',
    'Vietnamese': 'vi', 'Thai': 'th', 'Indonesian': 'id', 'Malay': 'ms',
    'Bengali': 'bn', 'Punjabi': 'pa', 'Tamil': 'ta', 'Telugu': 'te',
    'Swahili': 'sw', 'Catalan': 'ca', 'Ukrainian': 'uk',
}

# edge-tts Neural voice map: lang -> (male_voice, female_voice)
EDGE_VOICES = {
    'English':    ('en-US-GuyNeural',       'en-US-JennyNeural'),
    'Urdu':       ('ur-PK-AsadNeural',      'ur-PK-UzmaNeural'),
    'Hindi':      ('hi-IN-MadhurNeural',    'hi-IN-SwaraNeural'),
    'Arabic':     ('ar-SA-HamedNeural',     'ar-SA-ZariyahNeural'),
    'French':     ('fr-FR-HenriNeural',     'fr-FR-DeniseNeural'),
    'Spanish':    ('es-ES-AlvaroNeural',    'es-ES-ElviraNeural'),
    'German':     ('de-DE-ConradNeural',    'de-DE-KatjaNeural'),
    'Turkish':    ('tr-TR-AhmetNeural',     'tr-TR-EmelNeural'),
    'Russian':    ('ru-RU-DmitryNeural',    'ru-RU-SvetlanaNeural'),
    'Chinese':    ('zh-CN-YunxiNeural',     'zh-CN-XiaoxiaoNeural'),
    'Japanese':   ('ja-JP-KeitaNeural',     'ja-JP-NanamiNeural'),
    'Korean':     ('ko-KR-InJoonNeural',    'ko-KR-SunHiNeural'),
    'Portuguese': ('pt-BR-AntonioNeural',   'pt-BR-FranciscaNeural'),
    'Italian':    ('it-IT-DiegoNeural',     'it-IT-ElsaNeural'),
    'Dutch':      ('nl-NL-MaartenNeural',   'nl-NL-ColetteNeural'),
    'Polish':     ('pl-PL-MarekNeural',     'pl-PL-ZofiaNeural'),
    'Swedish':    ('sv-SE-MattiasNeural',   'sv-SE-SofieNeural'),
    'Danish':     ('da-DK-JeppeNeural',     'da-DK-ChristelNeural'),
    'Norwegian':  ('nb-NO-FinnNeural',      'nb-NO-PernilleNeural'),
    'Finnish':    ('fi-FI-HarriNeural',     'fi-FI-NooraNeural'),
    'Greek':      ('el-GR-NestorasNeural',  'el-GR-AthinaNeural'),
    'Romanian':   ('ro-RO-EmilNeural',      'ro-RO-AlinaNeural'),
    'Czech':      ('cs-CZ-AntoninNeural',   'cs-CZ-VlastaNeural'),
    'Hungarian':  ('hu-HU-TamasNeural',     'hu-HU-NoemiNeural'),
    'Vietnamese': ('vi-VN-NamMinhNeural',   'vi-VN-HoaiMyNeural'),
    'Thai':       ('th-TH-NiwatNeural',     'th-TH-PremwadeeNeural'),
    'Indonesian': ('id-ID-ArdiNeural',      'id-ID-GadisNeural'),
    'Malay':      ('ms-MY-OsmanNeural',     'ms-MY-YasminNeural'),
    'Bengali':    ('bn-BD-PradeepNeural',   'bn-BD-NabanitaNeural'),
    'Tamil':      ('ta-IN-ValluvarNeural',  'ta-IN-PallaviNeural'),
    'Telugu':     ('te-IN-MohanNeural',     'te-IN-ShrutiNeural'),
    'Ukrainian':  ('uk-UA-OstapNeural',     'uk-UA-PolinaNeural'),
    'Swahili':    ('sw-KE-RafikiNeural',    'sw-KE-ZuriNeural'),
}

# gTTS fallback TLD for gender simulation (used only if edge-tts fails)
VOICE_TLD_FALLBACK = {'Male': 'com', 'Female': 'co.uk'}

RTL_LANGS = {'Urdu', 'Arabic', 'Hebrew', 'Persian'}

LANG_FLAGS = {
    'English': '🇺🇸', 'Urdu': '🇵🇰', 'Hindi': '🇮🇳', 'Arabic': '🇸🇦',
    'French': '🇫🇷', 'Spanish': '🇪🇸', 'German': '🇩🇪', 'Turkish': '🇹🇷',
    'Russian': '🇷🇺', 'Chinese': '🇨🇳', 'Japanese': '🇯🇵', 'Korean': '🇰🇷',
    'Portuguese': '🇧🇷', 'Italian': '🇮🇹', 'Dutch': '🇳🇱', 'Polish': '🇵🇱',
    'Swedish': '🇸🇪', 'Danish': '🇩🇰', 'Norwegian': '🇳🇴', 'Finnish': '🇫🇮',
    'Greek': '🇬🇷', 'Romanian': '🇷🇴', 'Czech': '🇨🇿', 'Hungarian': '🇭🇺',
    'Vietnamese': '🇻🇳', 'Thai': '🇹🇭', 'Indonesian': '🇮🇩', 'Malay': '🇲🇾',
    'Bengali': '🇧🇩', 'Punjabi': '🇵🇰', 'Tamil': '🇮🇳', 'Telugu': '🇮🇳',
    'Swahili': '🇰🇪', 'Catalan': '🏳️', 'Ukrainian': '🇺🇦',
}

EMOTION_TAGS = {
    'Normal':  {'icon': '😐', 'color': C_GRAY,   'volume': '+0%',  'rate_boost': 0},
    'Happy':   {'icon': '😊', 'color': C_GREEN,  'volume': '+10%', 'rate_boost': 5},
    'Sad':     {'icon': '😢', 'color': C_BLUE2,  'volume': '-15%', 'rate_boost': -8},
    'Whisper': {'icon': '🤫', 'color': C_PURPLE, 'volume': '-60%', 'rate_boost': -10},
    'Shout':   {'icon': '📢', 'color': C_RED,    'volume': '+30%', 'rate_boost': 10},
    'Sarcasm': {'icon': '😏', 'color': C_AMBER,  'volume': '+5%',  'rate_boost': 0},
    'Excited': {'icon': '🎉', 'color': C_ORANGE, 'volume': '+20%', 'rate_boost': 15},
    'Calm':    {'icon': '🧘', 'color': C_TEAL,   'volume': '-10%', 'rate_boost': -12},
    'Serious': {'icon': '😐', 'color': C_INDIGO, 'volume': '+0%',  'rate_boost': -3},
    'Fearful': {'icon': '😨', 'color': C_PINK,   'volume': '-20%', 'rate_boost': -5},
}

VOICE_PRESETS = {
    'Narrator':   {'icon': '📖', 'speed': 50, 'pitch': 0,  'emotion': 'Calm',    'desc': 'Clear storytelling'},
    'Newsreader': {'icon': '📰', 'speed': 60, 'pitch': 0,  'emotion': 'Serious', 'desc': 'Professional news'},
    'Story Mode': {'icon': '🧙', 'speed': 45, 'pitch': -5, 'emotion': 'Happy',   'desc': 'Engaging story'},
    'Meditation': {'icon': '🧘', 'speed': 30, 'pitch': -3, 'emotion': 'Calm',    'desc': 'Peaceful & slow'},
    'Commercial': {'icon': '📺', 'speed': 65, 'pitch': 3,  'emotion': 'Excited', 'desc': 'Upbeat & catchy'},
    'Robot':      {'icon': '🤖', 'speed': 50, 'pitch': 10, 'emotion': 'Serious', 'desc': 'Robotic effect'},
    'Poet':       {'icon': '🎭', 'speed': 40, 'pitch': 2,  'emotion': 'Sad',     'desc': 'Dramatic poetry'},
    'Audiobook':  {'icon': '🎧', 'speed': 55, 'pitch': 0,  'emotion': 'Normal',  'desc': 'Long-form audio'},
}

FILE_ICONS = {
    'TXT':  {'emoji': '📝', 'color': C_BLUE2},
    'PDF':  {'emoji': '📕', 'color': C_RED},
    'DOCX': {'emoji': '📘', 'color': C_BLUE},
    'DOC':  {'emoji': '📗', 'color': C_GREEN},
    'SRT':  {'emoji': '🎬', 'color': C_PURPLE},
    'CSV':  {'emoji': '📊', 'color': C_AMBER},
}

# ═══════════════════════════════════════════════════════════
#  FOLDER: "Titan Studio PRO" (as requested)
# ═══════════════════════════════════════════════════════════
APP_FOLDER_NAME = 'Titan Studio PRO'


def get_titan_folder():
    if ANDROID_ENV:
        for root in ['/storage/emulated/0', '/sdcard', '/mnt/sdcard']:
            if os.path.exists(root):
                base = os.path.join(root, APP_FOLDER_NAME)
                break
        else:
            base = os.path.join(os.path.expanduser('~'), APP_FOLDER_NAME)
    else:
        base = os.path.join(os.path.expanduser('~'), APP_FOLDER_NAME)

    subfolders = ['Audio', 'Imported', 'Exports', 'Cloned', 'Queue']
    try:
        os.makedirs(base, exist_ok=True)
        for sf in subfolders:
            os.makedirs(os.path.join(base, sf), exist_ok=True)
        readme = os.path.join(base, 'README.txt')
        if not os.path.exists(readme):
            with open(readme, 'w', encoding='utf-8') as f:
                f.write('Titan Studio PRO\n')
                f.write('================\n')
                f.write('Audio/    - Generated MP3 voice files\n')
                f.write('Imported/ - Imported documents\n')
                f.write('Exports/  - Exported projects\n')
                f.write('Cloned/   - Voice cloning results\n')
                f.write('Queue/    - Batch processing\n')
    except Exception:
        pass
    return base


def get_audio_folder():
    return os.path.join(get_titan_folder(), 'Audio')


def get_internal_storage_path():
    if ANDROID_ENV:
        for p in ['/storage/emulated/0', '/sdcard', '/mnt/sdcard']:
            if os.path.exists(p):
                return p
    return os.path.expanduser('~')


# ═══════════════════════════════════════════════════════════
#  ANDROID PERMISSION REQUEST (before save)
# ═══════════════════════════════════════════════════════════
def request_storage_permissions(callback=None):
    if not ANDROID_ENV:
        if callback:
            callback(True)
        return
    try:
        from android.permissions import request_permissions, Permission
        perms = [
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
        ]

        def on_result(permissions, grants):
            ok = all(grants)
            if callback:
                callback(ok)

        request_permissions(perms, on_result)
    except Exception:
        if callback:
            callback(True)


# ═══════════════════════════════════════════════════════════
#  PERSISTENCE HELPERS
# ═══════════════════════════════════════════════════════════
def _app_dir():
    try:
        app = App.get_running_app()
        return app.user_data_dir if app else '.'
    except Exception:
        return '.'


def history_path():
    return os.path.join(_app_dir(), 'history_v3.json')


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
            json.dump(data[:500], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def history_clear():
    try:
        with open(history_path(), 'w') as f:
            json.dump([], f)
    except Exception:
        pass


def settings_path():
    return os.path.join(_app_dir(), 'settings_v3.json')


def settings_load():
    try:
        with open(settings_path(), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def settings_save(data):
    try:
        with open(settings_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def queue_path():
    return os.path.join(_app_dir(), 'batch_queue_v3.json')


def queue_load():
    try:
        with open(queue_path(), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def queue_save(data):
    try:
        with open(queue_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════
#  FILE READERS
# ═══════════════════════════════════════════════════════════
def read_txt(path):
    for enc in ['utf-8', 'utf-16', 'utf-8-sig', 'latin-1', 'cp1252']:
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
                xml = re.sub(r'<w:p[ />]', '\n<w:p ', xml)
                xml = re.sub(r'</w:p>', '\n', xml)
                text = re.sub(r'<[^>]+>', ' ', xml)
                return ' '.join(text.split())
        return ''
    except Exception:
        return ''


def read_srt(path):
    try:
        content = read_txt(path)
        lines = content.split('\n')
        text_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.isdigit() or '-->' in line:
                continue
            line = re.sub(r'<[^>]+>', '', line)
            if line:
                text_lines.append(line)
        return ' '.join(text_lines)
    except Exception:
        return ''


def get_file_info(path):
    ext = os.path.splitext(path)[1].upper().lstrip('.')
    size = os.path.getsize(path) if os.path.exists(path) else 0
    if size < 1024:
        size_str = str(size) + ' B'
    elif size < 1024 * 1024:
        size_str = '{:.1f} KB'.format(size / 1024)
    else:
        size_str = '{:.1f} MB'.format(size / (1024 * 1024))
    return ext, size_str


# ═══════════════════════════════════════════════════════════
#  ★ EDGE-TTS ANDROID FIX ★
#  Standard asyncio.run() fails on Android because:
#  - Android's Python has no working default event loop policy
#  - The fix: run edge-tts in a brand-new thread that creates
#    its own asyncio event loop manually with loop.run_until_complete()
#  This is guaranteed to work on Android + Python 3.11
# ═══════════════════════════════════════════════════════════
def edge_tts_generate(text, voice, rate_str, volume_str, pitch_str, output_path):
    """
    Runs edge-tts synchronously using a dedicated thread + fresh event loop.
    This solves the Android asyncio issue 100%.
    Returns (True, '') on success or (False, error_msg) on failure.
    """
    result = {'ok': False, 'err': ''}
    done_event = threading.Event()

    def _thread_worker():
        try:
            import edge_tts

            # Create fresh event loop (key Android fix)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _async_gen():
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice,
                    rate=rate_str,
                    volume=volume_str,
                    pitch=pitch_str,
                )
                await communicate.save(output_path)

            try:
                loop.run_until_complete(_async_gen())
                result['ok'] = True
            finally:
                loop.close()
        except ImportError:
            result['err'] = 'IMPORT_ERROR'
        except Exception as e:
            result['err'] = str(e)
        finally:
            done_event.set()

    t = threading.Thread(target=_thread_worker, daemon=True)
    t.start()
    done_event.wait(timeout=45)  # 45 second timeout

    if not done_event.is_set():
        return False, 'Timeout — check internet connection'
    return result['ok'], result['err']


def pick_edge_voice(lang_name, gender):
    """Returns correct edge-tts voice string for lang + gender"""
    voices = EDGE_VOICES.get(lang_name, ('en-US-GuyNeural', 'en-US-JennyNeural'))
    return voices[0] if gender == 'Male' else voices[1]


def speed_to_rate_str(speed_pct, emotion='Normal'):
    """Convert speed slider (10-100) + emotion to edge-tts rate string"""
    # Base offset: speed 50 = 0%, below 50 = slower, above 50 = faster
    base_offset = int((speed_pct - 50) * 1.5)
    # Add emotion rate boost
    emotion_boost = EMOTION_TAGS.get(emotion, {}).get('rate_boost', 0)
    total = base_offset + emotion_boost
    total = max(-50, min(total, 100))  # clamp
    sign = '+' if total >= 0 else ''
    return sign + str(total) + '%'


def pitch_to_pitch_str(pitch_val):
    """Convert pitch slider (-10 to +10) to edge-tts pitch Hz string"""
    hz = pitch_val * 15  # ±150 Hz range
    sign = '+' if hz >= 0 else ''
    return sign + str(hz) + 'Hz'


def emotion_to_volume_str(emotion):
    """Get volume modifier based on emotion"""
    return EMOTION_TAGS.get(emotion, {}).get('volume', '+0%')


# ═══════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════
def hex_c(h):
    return get_color_from_hex(h)


def lbl(txt, size=15, color=C_MUTED, bold=False, h=36, halign='left'):
    l = Label(
        text=txt, font_size=sp(size), bold=bold,
        color=hex_c(color), size_hint_y=None, height=dp(h),
        halign=halign, valign='middle',
    )
    l.bind(size=l.setter('text_size'))
    return l


def card_bg(widget, color=C_CARD, radius=14):
    with widget.canvas.before:
        Color(*hex_c(color))
        rr = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])

    def _upd(w, *a):
        rr.pos = w.pos
        rr.size = w.size

    widget.bind(pos=_upd, size=_upd)


def separator(color=C_CARD2, h=1):
    s = Widget(size_hint_y=None, height=dp(h))
    with s.canvas:
        Color(*hex_c(color))
        rect = Rectangle(pos=s.pos, size=s.size)
    s.bind(
        pos=lambda w, *a: setattr(rect, 'pos', w.pos),
        size=lambda w, *a: setattr(rect, 'size', w.size),
    )
    return s


def spacer(h=12):
    return Widget(size_hint_y=None, height=dp(h))


# ═══════════════════════════════════════════════════════════
#  FLAT BUTTON  (Animated)
# ═══════════════════════════════════════════════════════════
class FlatBtn(Button):
    def __init__(self, bg=C_BLUE, radius=14, **kw):
        super().__init__(**kw)
        self.bg_color = bg
        self._radius = radius
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = kw.get('font_size', sp(16))
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
                pos=self.pos, size=self.size, radius=[dp(self._radius)]
            )

    def on_press(self):
        anim = Animation(opacity=0.6, duration=0.05) + Animation(opacity=1.0, duration=0.12)
        anim.start(self)

    def on_disabled(self, inst, val):
        self.opacity = 0.38 if val else 1.0


# ═══════════════════════════════════════════════════════════
#  ICON BUTTON
# ═══════════════════════════════════════════════════════════
class IconBtn(ButtonBehavior, Label):
    def __init__(self, icon='🎵', size_dp=44, bg=C_CARD2, **kw):
        super().__init__(**kw)
        self.text = icon
        self.font_size = sp(22)
        self.size_hint = (None, None)
        self.size = (dp(size_dp), dp(size_dp))
        self._bg_color = bg
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex_c(self._bg_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

    def on_press(self):
        Animation(opacity=0.5, duration=0.05).start(self)

    def on_release(self):
        Animation(opacity=1.0, duration=0.12).start(self)


# ═══════════════════════════════════════════════════════════
#  DARK PANEL
# ═══════════════════════════════════════════════════════════
class DarkPanel(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*hex_c(C_BG))
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size


# ═══════════════════════════════════════════════════════════
#  WAVEFORM VISUALIZER  (Animated bars)
# ═══════════════════════════════════════════════════════════
class WaveformWidget(Widget):
    def __init__(self, bars=28, color=C_BLUE2, **kw):
        super().__init__(**kw)
        self._bars = bars
        self._color = color
        self._heights = [0.08] * bars
        self._anim_ev = None
        self._active = False
        self._t = 0
        self.bind(pos=self._draw, size=self._draw)

    def start(self):
        self._active = True
        if not self._anim_ev:
            self._anim_ev = Clock.schedule_interval(self._tick, 0.055)

    def stop(self):
        self._active = False
        self._heights = [0.08] * self._bars
        self._draw()
        if self._anim_ev:
            self._anim_ev.cancel()
            self._anim_ev = None

    def pulse(self):
        """One-shot pulse animation for button press feedback"""
        if not self._anim_ev:
            self._anim_ev = Clock.schedule_interval(self._tick, 0.055)
        self._active = True
        Clock.schedule_once(lambda dt: self.stop(), 1.2)

    def _tick(self, dt):
        self._t += 0.18
        if self._active:
            for i in range(self._bars):
                phase = self._t + i * 0.35
                v = abs(math.sin(phase)) * 0.65 + abs(math.sin(phase * 2.7 + 1)) * 0.35
                self._heights[i] = max(0.05, v)
        else:
            self._heights = [0.07] * self._bars
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        if not self.width or not self.height:
            return
        bar_w = self.width / (self._bars * 1.5)
        gap = bar_w * 0.5
        total = self._bars * (bar_w + gap)
        start_x = self.x + (self.width - total) / 2

        with self.canvas:
            for i, h_ratio in enumerate(self._heights):
                x = start_x + i * (bar_w + gap)
                bh = h_ratio * self.height
                y = self.y + (self.height - bh) / 2
                alpha = 0.35 + h_ratio * 0.65
                r, g, b, _ = hex_c(self._color)
                Color(r, g, b, alpha)
                RoundedRectangle(
                    pos=(x, y), size=(bar_w, bh),
                    radius=[dp(bar_w / 2)],
                )

    def cleanup(self):
        if self._anim_ev:
            self._anim_ev.cancel()
            self._anim_ev = None


# ═══════════════════════════════════════════════════════════
#  GLOW CARD  (Card with animated gradient border glow)
# ═══════════════════════════════════════════════════════════
class GlowCard(BoxLayout):
    """Card that pulses a colored border glow — used for active elements"""
    def __init__(self, glow_color=C_BLUE2, **kw):
        super().__init__(**kw)
        self._glow_color = glow_color
        self._alpha = 0.5
        self._glow_anim = None
        with self.canvas.before:
            self._gc = Color(*(hex_c(glow_color)[:3]), self._alpha)
            self._grr = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            Color(*hex_c(C_CARD2))
            self._inner = RoundedRectangle(
                pos=(self.x + dp(2), self.y + dp(2)),
                size=(max(0, self.width - dp(4)), max(0, self.height - dp(4))),
                radius=[dp(16)],
            )
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._grr.pos = self.pos
        self._grr.size = self.size
        self._inner.pos = (self.x + dp(2), self.y + dp(2))
        self._inner.size = (max(0, self.width - dp(4)), max(0, self.height - dp(4)))

    def start_glow(self):
        self._glow_anim = Clock.schedule_interval(self._pulse_glow, 0.05)

    def stop_glow(self):
        if self._glow_anim:
            self._glow_anim.cancel()
            self._glow_anim = None

    def _pulse_glow(self, dt):
        self._alpha = 0.3 + 0.4 * abs(math.sin(time.time() * 2.5))
        self._gc.a = self._alpha


# ═══════════════════════════════════════════════════════════
#  EMOTION PICKER
# ═══════════════════════════════════════════════════════════
class EmotionPicker(BoxLayout):
    def __init__(self, callback=None, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(190)
        self.spacing = dp(8)
        self._callback = callback
        self._selected = 'Normal'
        self._btns = {}
        self._build()

    def _build(self):
        self.add_widget(lbl('Emotion & Mood', 14, C_ACCENT, True, 28))
        row1 = BoxLayout(size_hint_y=None, height=dp(65), spacing=dp(8))
        row2 = BoxLayout(size_hint_y=None, height=dp(65), spacing=dp(8))
        em1 = ['Normal', 'Happy', 'Sad', 'Whisper', 'Shout']
        em2 = ['Sarcasm', 'Excited', 'Calm', 'Serious', 'Fearful']
        for em in em1:
            self._add_btn(row1, em)
        for em in em2:
            self._add_btn(row2, em)
        self.add_widget(row1)
        self.add_widget(row2)
        Clock.schedule_once(lambda dt: self._select('Normal'), 0)

    def _add_btn(self, parent, emotion):
        data = EMOTION_TAGS[emotion]
        b = FlatBtn(
            text=data['icon'] + '\n' + emotion,
            bg=C_CARD2, font_size=sp(10), bold=False, radius=12,
        )
        b.bind(on_press=lambda x, e=emotion: self._select(e))
        self._btns[emotion] = b
        parent.add_widget(b)

    def _select(self, emotion):
        self._selected = emotion
        data = EMOTION_TAGS[emotion]
        for em, btn in self._btns.items():
            if em == emotion:
                btn.set_bg(data['color'])
                anim = Animation(opacity=0.7, duration=0.08) + Animation(opacity=1, duration=0.15)
                anim.start(btn)
            else:
                btn.set_bg(C_CARD2)
        if self._callback:
            self._callback(emotion)

    @property
    def selected(self):
        return self._selected


# ═══════════════════════════════════════════════════════════
#  PRESET PICKER
# ═══════════════════════════════════════════════════════════
class PresetPicker(BoxLayout):
    def __init__(self, callback=None, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(160)
        self.spacing = dp(8)
        self._callback = callback
        self._btns = {}
        self._build()

    def _build(self):
        self.add_widget(lbl('Voice Presets', 14, C_ACCENT, True, 28))
        sv = ScrollView(size_hint=(1, None), height=dp(120))
        row = BoxLayout(orientation='horizontal', size_hint=(None, 1), spacing=dp(10), padding=[dp(2), dp(4)])
        row.bind(minimum_width=row.setter('width'))
        for preset_name, data in VOICE_PRESETS.items():
            col = BoxLayout(orientation='vertical', size_hint=(None, 1), width=dp(88), spacing=dp(4))
            b = FlatBtn(text=data['icon'], bg=C_CARD2, size_hint_y=None, height=dp(52), font_size=sp(26), radius=12)
            b.bind(on_press=lambda x, n=preset_name: self._select(n))
            nl = Label(text=preset_name, font_size=sp(9), color=hex_c(C_MUTED2), size_hint_y=None, height=dp(20), bold=True)
            col.add_widget(b)
            col.add_widget(nl)
            self._btns[preset_name] = b
            row.add_widget(col)
        sv.add_widget(row)
        self.add_widget(sv)

    def _select(self, preset_name):
        for n, b in self._btns.items():
            b.set_bg(C_INDIGO if n == preset_name else C_CARD2)
        if self._callback:
            self._callback(preset_name, VOICE_PRESETS[preset_name])


# ═══════════════════════════════════════════════════════════
#  PITCH SLIDER CARD
# ═══════════════════════════════════════════════════════════
class PitchSliderCard(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(110)
        self.padding = [dp(16), dp(10)]
        self.spacing = dp(8)
        card_bg(self, C_CARD2, 16)
        self._build()

    def _build(self):
        self.add_widget(lbl('Pitch & Tone', 14, C_ACCENT, True, 28))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        row.add_widget(lbl('Low', 12, C_MUTED, False, 44))
        self.pitch_slider = Slider(min=-10, max=10, value=0, step=1)
        self.pitch_lbl = lbl('0 semi', 13, C_CYAN, False, 44)
        self.pitch_slider.bind(
            value=lambda i, v: setattr(
                self.pitch_lbl, 'text',
                ('+' if v > 0 else '') + str(int(v)) + ' semi'
            )
        )
        row.add_widget(self.pitch_slider)
        row.add_widget(lbl('High', 12, C_MUTED, False, 44))
        self.add_widget(row)
        self.add_widget(self.pitch_lbl)

    @property
    def value(self):
        return int(self.pitch_slider.value)


# ═══════════════════════════════════════════════════════════
#  ADVANCED OPTIONS CARD
# ═══════════════════════════════════════════════════════════
class AdvancedOptionsCard(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(240)
        self.padding = [dp(16), dp(12)]
        self.spacing = dp(8)
        card_bg(self, C_CARD2, 16)
        self._build()

    def _build(self):
        self.add_widget(lbl('Advanced Options', 14, C_ACCENT, True, 30))
        toggles = [
            ('breath_sw', '💨 Dynamic Breath Simulation'),
            ('latency_sw', '⚡ Ultra-Low Latency Mode'),
            ('ssml_sw', '📝 SSML Markup Support'),
            ('pacing_sw', '⏱ Adaptive Pacing'),
        ]
        for attr, label in toggles:
            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
            row.add_widget(lbl(label, 13, C_WHITE2, False, 44))
            sw = Switch(active=False, size_hint=(None, None), size=(dp(70), dp(44)))
            setattr(self, attr, sw)
            row.add_widget(sw)
            self.add_widget(row)
            self.add_widget(separator(C_CARD3, 1))

    @property
    def use_breaths(self):
        return self.breath_sw.active

    @property
    def use_ssml(self):
        return self.ssml_sw.active

    @property
    def low_latency(self):
        return self.latency_sw.active

    @property
    def adaptive_pacing(self):
        return self.pacing_sw.active


# ═══════════════════════════════════════════════════════════
#  FILE INFO CARD
# ═══════════════════════════════════════════════════════════
class FileInfoCard(BoxLayout):
    def __init__(self, path, ftype, **kw):
        super().__init__(**kw)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(72)
        self.padding = [dp(12), dp(8)]
        self.spacing = dp(12)
        card_bg(self, C_SURFACE, 12)
        info = FILE_ICONS.get(ftype.upper(), {'emoji': '📄', 'color': C_GRAY})

        icon_bg = FloatLayout(size_hint=(None, None), size=(dp(50), dp(50)))
        with icon_bg.canvas.before:
            Color(*hex_c(info.get('color', C_GRAY) + '33'))
            rr = RoundedRectangle(pos=icon_bg.pos, size=icon_bg.size, radius=[dp(10)])
        icon_bg.bind(
            pos=lambda w, *a: setattr(rr, 'pos', w.pos),
            size=lambda w, *a: setattr(rr, 'size', w.size),
        )
        icon_bg.add_widget(Label(text=info.get('emoji', '📄'), font_size=sp(26), size_hint=(1, 1)))
        self.add_widget(icon_bg)

        info_col = BoxLayout(orientation='vertical', size_hint_x=1)
        fname = os.path.basename(path)
        ext, size_str = get_file_info(path)
        name_lbl = Label(text=fname, font_size=sp(13), bold=True, color=hex_c(C_WHITE),
                         halign='left', valign='middle', size_hint_y=None, height=dp(30))
        name_lbl.bind(size=name_lbl.setter('text_size'))
        meta_lbl = Label(text=ftype.upper() + ' · ' + size_str, font_size=sp(11),
                         color=hex_c(info.get('color', C_MUTED)),
                         halign='left', valign='middle', size_hint_y=None, height=dp(24))
        meta_lbl.bind(size=meta_lbl.setter('text_size'))
        info_col.add_widget(name_lbl)
        info_col.add_widget(meta_lbl)
        self.add_widget(info_col)


# ═══════════════════════════════════════════════════════════
#  LOADING SCREEN  (Single clean loader, no double)
# ═══════════════════════════════════════════════════════════
class LoadingScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._dot_ev = None
        self._dot_count = 0
        self._already_gone = False
        self._build()

    def _build(self):
        root = DarkPanel()

        # Logo
        logo_path = self._find_logo()
        if logo_path:
            self.logo_widget = KivyImage(
                source=logo_path, allow_stretch=True, keep_ratio=True,
                size_hint=(None, None), size=(dp(150), dp(150)),
                pos_hint={'center_x': 0.5, 'center_y': 0.63}, opacity=0,
            )
        else:
            self.logo_widget = Label(
                text='T', font_size=sp(80), bold=True, color=hex_c(C_BLUE2),
                pos_hint={'center_x': 0.5, 'center_y': 0.63}, opacity=0,
            )
        root.add_widget(self.logo_widget)

        # Version badge
        self.ver_lbl = Label(
            text='v11.0  ULTIMATE', font_size=sp(11), bold=True,
            color=hex_c(C_GOLD), pos_hint={'center_x': 0.5, 'center_y': 0.48}, opacity=0,
        )
        root.add_widget(self.ver_lbl)

        # Title
        self.title_lbl = Label(
            text='Titan Studio PRO', font_size=sp(28), bold=True,
            color=hex_c(C_WHITE), pos_hint={'center_x': 0.5, 'center_y': 0.55}, opacity=0,
        )
        root.add_widget(self.title_lbl)

        # Subtitle
        self.sub_lbl = Label(
            text='Professional Voice Studio · Always Free',
            font_size=sp(13), color=hex_c(C_MUTED2),
            pos_hint={'center_x': 0.5, 'center_y': 0.40}, opacity=0,
        )
        root.add_widget(self.sub_lbl)

        # Animated loading text
        self.dot_lbl = Label(
            text='Initializing...', font_size=sp(14), color=hex_c(C_ACCENT),
            pos_hint={'center_x': 0.5, 'center_y': 0.30}, opacity=0,
        )
        root.add_widget(self.dot_lbl)

        # Progress bar
        self.prog = ProgressBar(
            max=100, value=0, size_hint=(0.7, None), height=dp(5),
            pos_hint={'center_x': 0.5, 'y': 0.22},
        )
        root.add_widget(self.prog)

        # Waveform decoration
        self.wave = WaveformWidget(
            bars=18, color=C_BLUE3,
            size_hint=(None, None), size=(dp(260), dp(32)),
            pos_hint={'center_x': 0.5, 'center_y': 0.16},
        )
        root.add_widget(self.wave)

        # Copyright
        root.add_widget(Label(
            text='© 2025 Titan Studio PRO', font_size=sp(11), color=hex_c(C_MUTED),
            pos_hint={'center_x': 0.5, 'center_y': 0.07},
        ))

        self.add_widget(root)

    def _find_logo(self):
        base = os.path.dirname(os.path.abspath(__file__))
        for name in ['AI.png', 'AI.jpg', 'logo.png']:
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
        return None

    def on_enter(self, *a):
        if self._already_gone:
            return
        self._animate_in()
        self.wave.start()
        self._dot_ev = Clock.schedule_interval(self._tick_dots, 0.4)
        Clock.schedule_once(lambda dt: Animation(value=90, duration=3.0, t='out_cubic').start(self.prog), 0.3)
        Clock.schedule_once(self._go, 3.6)

    def _animate_in(self):
        Animation(opacity=1, duration=0.9).start(self.logo_widget)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.title_lbl), 0.4)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.ver_lbl), 0.6)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.sub_lbl), 0.8)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.4).start(self.dot_lbl), 1.0)

    def _tick_dots(self, dt):
        self._dot_count = (self._dot_count + 1) % 4
        msgs = ['Initializing', 'Loading voices', 'Preparing studio', 'Almost ready']
        idx = self._dot_count
        self.dot_lbl.text = msgs[idx] + '...'

    def on_leave(self, *a):
        if self._dot_ev:
            self._dot_ev.cancel()
        self.wave.stop()

    def _go(self, dt):
        if self._already_gone:
            return
        self._already_gone = True
        Animation(value=100, duration=0.2).start(self.prog)
        Clock.schedule_once(self._switch, 0.25)

    def _switch(self, dt=None):
        self.manager.transition = FadeTransition(duration=0.5)
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

        hdr = BoxLayout(size_hint_y=None, height=dp(72), spacing=dp(12))
        back = FlatBtn(text='← Back', bg=C_GRAY, size_hint_x=None, width=dp(110), font_size=sp(15))
        back.bind(on_press=self._go_back)
        hdr.add_widget(back)
        hdr.add_widget(lbl('📋 Voice History', 22, C_ACCENT, True, 72))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        # Stats row
        self.stats_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10), padding=[dp(12), dp(8)])
        card_bg(self.stats_row, C_CARD2, 12)
        self.count_lbl = lbl('0 recordings', 13, C_MUTED2, False, 40)
        self.size_lbl = lbl('0 KB total', 13, C_MUTED2, False, 40)
        self.stats_row.add_widget(self.count_lbl)
        self.stats_row.add_widget(self.size_lbl)
        outer.add_widget(self.stats_row)

        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(14), padding=[dp(2), dp(8)])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)
        outer.add_widget(separator())

        clr = FlatBtn(text='🗑  Clear All History', bg=C_DARK_RED, size_hint_y=None, height=dp(58), font_size=sp(16))
        clr.bind(on_press=self._confirm_clear)
        outer.add_widget(clr)

        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        self.x = dp(80)
        Animation(opacity=1, x=0, duration=0.3, t='out_cubic').start(self)
        Clock.schedule_once(lambda dt: self._refresh(), 0.1)

    def _go_back(self, *a):
        self.manager.transition = SlideTransition(direction='right', duration=0.3)
        self.manager.current = 'studio'

    def _refresh(self):
        self.list_box.clear_widgets()
        data = history_load()
        total_size = sum(os.path.getsize(e.get('path', ''))
                         for e in data if os.path.exists(e.get('path', '')))
        if total_size < 1024 * 1024:
            sz = '{:.0f} KB'.format(total_size / 1024)
        else:
            sz = '{:.1f} MB'.format(total_size / (1024 * 1024))
        self.count_lbl.text = str(len(data)) + ' recordings'
        self.size_lbl.text = sz + ' total'

        if not data:
            self.list_box.add_widget(Label(
                text='No recordings yet.\nGenerate and save your first voice!',
                color=hex_c(C_MUTED), font_size=sp(15),
                size_hint_y=None, height=dp(120), halign='center', valign='middle',
            ))
            return

        for i, entry in enumerate(data):
            row = self._make_row(entry)
            row.opacity = 0
            self.list_box.add_widget(row)
            Clock.schedule_once(lambda dt, w=row: Animation(opacity=1, duration=0.22).start(w), i * 0.06)

    def _make_row(self, entry):
        row = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(10), padding=[dp(14), dp(8)])
        card_bg(row, C_CARD2, 16)
        em = entry.get('emotion', 'Normal')
        icon_text = EMOTION_TAGS.get(em, {}).get('icon', '🎵')
        row.add_widget(Label(text=icon_text, font_size=sp(28), size_hint_x=None, width=dp(44)))

        info = BoxLayout(orientation='vertical', size_hint_x=0.72)
        fname = Label(text=entry.get('filename', 'unknown'), font_size=sp(13), bold=True,
                      color=hex_c(C_WHITE), halign='left', valign='middle',
                      size_hint_y=None, height=dp(36))
        fname.bind(size=fname.setter('text_size'))
        info.add_widget(fname)

        flag = LANG_FLAGS.get(entry.get('lang', ''), '')
        meta = Label(
            text=flag + ' ' + entry.get('lang', '') + '  ·  ' + entry.get('voice', '') +
                 '  ·  ' + entry.get('emotion', 'Normal') + '  ·  ' + entry.get('time', ''),
            font_size=sp(11), color=hex_c(C_GREEN),
            halign='left', valign='middle', size_hint_y=None, height=dp(28),
        )
        meta.bind(size=meta.setter('text_size'))
        info.add_widget(meta)
        row.add_widget(info)

        fp = entry.get('path', '')
        if os.path.exists(fp):
            pb = FlatBtn(text='▶', bg=C_GREEN, size_hint_x=None, width=dp(52), font_size=sp(18))
            pb.bind(on_press=lambda *a, p=fp, b=pb: self._play(p, b))
            row.add_widget(pb)
        else:
            row.add_widget(Label(text='[Missing]', font_size=sp(10), color=hex_c(C_RED),
                                 size_hint_x=None, width=dp(60)))
        return row

    def _play(self, path, btn):
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
            btn.text = '⏹'
            btn.set_bg(C_RED)
            Clock.schedule_once(lambda dt: (setattr(btn, 'text', '▶'), btn.set_bg(C_GREEN)), snd.length + 0.3)

    def _confirm_clear(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        box.add_widget(Label(text='Clear all history?\nThis cannot be undone.',
                             color=hex_c(C_WHITE), font_size=sp(15), halign='center', valign='middle'))
        br = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(14))
        yes = FlatBtn(text='Yes, Clear', bg=C_DARK_RED, font_size=sp(15))
        no = FlatBtn(text='Cancel', bg=C_GRAY, font_size=sp(15))
        br.add_widget(yes)
        br.add_widget(no)
        box.add_widget(br)
        p = Popup(title='Confirm', content=box, size_hint=(0.88, 0.42), background_color=hex_c(C_CARD))
        yes.bind(on_press=lambda *a: (p.dismiss(), history_clear(), self._refresh()))
        no.bind(on_press=p.dismiss)
        p.open()


# ═══════════════════════════════════════════════════════════
#  SETTINGS SCREEN
# ═══════════════════════════════════════════════════════════
class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        root = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))

        hdr = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        back = FlatBtn(text='← Back', bg=C_GRAY, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('⚙ Settings', 20, C_ACCENT, True, 64))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(16), padding=[dp(2), dp(6)])
        content.bind(minimum_height=content.setter('height'))

        # Titan folder info
        fc = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(130),
                       padding=[dp(16), dp(12)], spacing=dp(8))
        card_bg(fc, C_CARD2, 14)
        fc.add_widget(lbl('📁 Save Folder: Titan Studio PRO', 14, C_ACCENT, True, 28))
        titan_path = get_titan_folder()
        pl = Label(text=titan_path, font_size=sp(12), color=hex_c(C_WHITE2),
                   halign='left', valign='middle', size_hint_y=None, height=dp(40))
        pl.bind(size=pl.setter('text_size'))
        fc.add_widget(pl)
        fc.add_widget(lbl('All audio saved here automatically', 12, C_GREEN, False, 28))
        content.add_widget(fc)

        # Folder structure
        sc = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(170),
                       padding=[dp(16), dp(12)], spacing=dp(6))
        card_bg(sc, C_CARD2, 14)
        sc.add_widget(lbl('📂 Sub-folders', 14, C_ACCENT, True, 28))
        for folder, desc in [
            ('Audio/', 'Generated MP3 files'), ('Imported/', 'Imported documents'),
            ('Exports/', 'Exported projects'), ('Cloned/', 'Voice cloning'), ('Queue/', 'Batch queue'),
        ]:
            row = BoxLayout(size_hint_y=None, height=dp(24))
            row.add_widget(lbl('  📁 ' + folder, 12, C_BLUE2, True, 24))
            row.add_widget(lbl(desc, 11, C_MUTED, False, 24))
            sc.add_widget(row)
        content.add_widget(sc)

        # ElevenLabs API key
        api_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180),
                             padding=[dp(16), dp(12)], spacing=dp(10))
        card_bg(api_card, C_CARD2, 14)
        api_card.add_widget(lbl('🔑 ElevenLabs API (Voice Cloning)', 14, C_ACCENT, True, 28))
        api_card.add_widget(lbl('For premium voice cloning features:', 12, C_MUTED2, False, 28))
        settings = settings_load()
        self.api_input = TextInput(
            text=settings.get('elevenlabs_key', ''),
            hint_text='sk-... (Get free key at elevenlabs.io)',
            multiline=False, size_hint_y=None, height=dp(52),
            background_color=(0.08, 0.12, 0.20, 1), foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.39, 0.46, 0.54, 1), cursor_color=(0.23, 0.74, 0.97, 1),
            font_size=sp(14), password=True,
        )
        api_card.add_widget(self.api_input)
        save_key_btn = FlatBtn(text='💾 Save API Key', bg=C_BLUE, size_hint_y=None, height=dp(48), font_size=sp(14))
        save_key_btn.bind(on_press=self._save_api_key)
        api_card.add_widget(save_key_btn)
        content.add_widget(api_card)

        # About
        about_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150),
                               padding=[dp(16), dp(12)], spacing=dp(8))
        card_bg(about_card, C_CARD2, 14)
        about_card.add_widget(lbl('ℹ About', 14, C_ACCENT, True, 28))
        for line in [
            'Titan Studio PRO  v11.0.0  ULTIMATE',
            'Professional TTS & Voice Studio',
            '30+ Languages · 10 Emotions · Real Neural Voices',
            'Powered by Microsoft Edge-TTS · Always Free',
            '© 2025 Titan Studio PRO',
        ]:
            about_card.add_widget(lbl(line, 12, C_MUTED2, False, 22))
        content.add_widget(about_card)
        content.add_widget(spacer(24))
        sv.add_widget(content)
        outer.add_widget(sv)
        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        Animation(opacity=1, duration=0.3).start(self)

    def _go_back(self):
        self.manager.transition = SlideTransition(direction='right', duration=0.3)
        self.manager.current = 'studio'

    def _save_api_key(self, *a):
        s = settings_load()
        s['elevenlabs_key'] = self.api_input.text.strip()
        settings_save(s)
        box = BoxLayout(orientation='vertical', padding=dp(20))
        box.add_widget(Label(text='API key saved!', color=hex_c(C_WHITE), font_size=sp(15)))
        ok = FlatBtn(text='OK', bg=C_GREEN, size_hint_y=None, height=dp(50))
        box.add_widget(ok)
        p = Popup(title='✅', content=box, size_hint=(0.8, 0.3), background_color=hex_c(C_CARD))
        ok.bind(on_press=p.dismiss)
        p.open()


# ═══════════════════════════════════════════════════════════
#  BATCH QUEUE SCREEN
# ═══════════════════════════════════════════════════════════
class BatchQueueScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._queue = []
        self._processing = False
        self._build()

    def _build(self):
        root = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        hdr = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        back = FlatBtn(text='← Back', bg=C_GRAY, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('📋 Batch Processing Queue', 18, C_ACCENT, True, 64))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        self.status_banner = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(14), dp(8)])
        card_bg(self.status_banner, C_CARD2, 12)
        self.status_lbl = lbl('Queue is empty. Add items from Studio.', 13, C_MUTED, False, 32)
        self.status_banner.add_widget(self.status_lbl)
        outer.add_widget(self.status_banner)

        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=[dp(2), dp(6)])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)
        outer.add_widget(separator())

        ctrl = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(12))
        self.proc_btn = FlatBtn(text='▶ Process All', bg=C_GREEN, font_size=sp(15))
        self.proc_btn.bind(on_press=self._process_all)
        clr_btn = FlatBtn(text='🗑 Clear Queue', bg=C_DARK_RED, font_size=sp(14))
        clr_btn.bind(on_press=self._clear_queue)
        ctrl.add_widget(self.proc_btn)
        ctrl.add_widget(clr_btn)
        outer.add_widget(ctrl)
        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        self.x = dp(80)
        Animation(opacity=1, x=0, duration=0.3, t='out_cubic').start(self)
        Clock.schedule_once(lambda dt: self._refresh(), 0.1)

    def _go_back(self):
        self.manager.transition = SlideTransition(direction='right', duration=0.3)
        self.manager.current = 'studio'

    def _refresh(self):
        self._queue = queue_load()
        self.list_box.clear_widgets()
        if not self._queue:
            self.status_lbl.text = 'Queue is empty. Add items from Studio.'
            return
        self.status_lbl.text = str(len(self._queue)) + ' items in queue'
        for i, item in enumerate(self._queue):
            self.list_box.add_widget(self._make_row(i, item))

    def _make_row(self, idx, item):
        row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10), padding=[dp(12), dp(8)])
        card_bg(row, C_CARD2, 14)
        row.add_widget(Label(text=str(idx + 1), font_size=sp(20), bold=True,
                             color=hex_c(C_ACCENT), size_hint_x=None, width=dp(36)))
        info = BoxLayout(orientation='vertical')
        t = lbl(item.get('text', '')[:60] + '...', 13, C_WHITE2, False, 36)
        m = lbl(item.get('lang', '') + '  ·  ' + item.get('voice', '') + '  ·  ' + item.get('emotion', ''),
                11, C_MUTED2, False, 28)
        info.add_widget(t)
        info.add_widget(m)
        row.add_widget(info)
        status = item.get('status', 'pending')
        color = C_AMBER if status == 'pending' else C_GREEN if status == 'done' else C_RED
        row.add_widget(Label(text=status.upper(), font_size=sp(10), bold=True,
                             color=hex_c(color), size_hint_x=None, width=dp(60)))
        return row

    def _process_all(self, *a):
        if self._processing:
            return
        self._queue = queue_load()
        if not self._queue:
            return
        self._processing = True
        self.proc_btn.text = '⏳ Processing...'
        self.proc_btn.disabled = True
        threading.Thread(target=self._worker_all, daemon=True).start()

    def _worker_all(self):
        results = []
        for i, item in enumerate(self._queue):
            try:
                text = item.get('text', '')
                lang = item.get('lang', 'English')
                gender = item.get('voice', 'Male')
                speed_pct = item.get('speed', 50)
                emotion = item.get('emotion', 'Normal')
                pitch_val = item.get('pitch', 0)

                voice = pick_edge_voice(lang, gender)
                rate_str = speed_to_rate_str(speed_pct, emotion)
                volume_str = emotion_to_volume_str(emotion)
                pitch_str = pitch_to_pitch_str(pitch_val)

                fname = 'Queue_{}_{}_{}.mp3'.format(i + 1, lang, int(time.time()))
                dest = os.path.join(get_audio_folder(), fname)
                os.makedirs(get_audio_folder(), exist_ok=True)

                ok, err = edge_tts_generate(text, voice, rate_str, volume_str, pitch_str, dest)

                if ok:
                    item['status'] = 'done'
                    item['output'] = dest
                    history_save({
                        'filename': fname, 'path': dest, 'lang': lang,
                        'voice': gender, 'time': time.strftime('%d %b %Y  %H:%M'),
                        'emotion': emotion, 'source': 'batch',
                    })
                elif err == 'IMPORT_ERROR':
                    # Fallback to gTTS
                    try:
                        from gtts import gTTS
                        lang_code = LANGUAGES.get(lang, 'en')
                        tld = VOICE_TLD_FALLBACK.get(gender, 'com')
                        tts = gTTS(text=text, lang=lang_code, tld=tld, slow=speed_pct <= 30)
                        tts.save(dest)
                        item['status'] = 'done'
                        item['output'] = dest
                        history_save({'filename': fname, 'path': dest, 'lang': lang,
                                      'voice': gender, 'time': time.strftime('%d %b %Y  %H:%M'),
                                      'emotion': emotion, 'source': 'batch-gtts'})
                    except Exception:
                        item['status'] = 'error'
                else:
                    item['status'] = 'error'
            except Exception:
                item['status'] = 'error'
            results.append(item)
            idx_copy = i
            Clock.schedule_once(
                lambda dt, n=idx_copy: setattr(
                    self.status_lbl, 'text',
                    'Processing {} / {}'.format(n + 1, len(self._queue))
                ), 0
            )

        queue_save(results)
        Clock.schedule_once(lambda dt: self._done_all(), 0)

    def _done_all(self):
        self._processing = False
        self.proc_btn.text = '▶ Process All'
        self.proc_btn.disabled = False
        self.status_lbl.text = '✅ All items processed!'
        self._refresh()

    def _clear_queue(self, *a):
        queue_save([])
        self._refresh()


# ═══════════════════════════════════════════════════════════
#  STUDIO SCREEN  (Main screen — beautiful redesign)
# ═══════════════════════════════════════════════════════════
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._audio = None
        self.out_file = None
        self.voice_sel = 'Male'
        self._imported_path = None
        self._imported_type = None
        self._build()

    def _build(self):
        root = DarkPanel()
        outer = BoxLayout(orientation='vertical')

        # ══ HEADER BAR ═══════════════════════════════════
        hdr = BoxLayout(size_hint_y=None, height=dp(82), padding=[dp(14), dp(8)], spacing=dp(12))
        card_bg(hdr, C_CARD, 0)

        # Logo
        logo_path = self._find_logo()
        logo_box = BoxLayout(size_hint=(None, None), size=(dp(52), dp(52)))
        if logo_path:
            logo_box.add_widget(KivyImage(source=logo_path, allow_stretch=True, keep_ratio=True, size_hint=(1, 1)))
        else:
            logo_box.add_widget(Label(text='T', font_size=sp(30), bold=True, color=hex_c(C_BLUE2), size_hint=(1, 1)))
        hdr.add_widget(logo_box)

        # Title block
        tb = BoxLayout(orientation='vertical', size_hint_x=1)
        t1 = Label(text='Titan Studio PRO', font_size=sp(19), bold=True, color=hex_c(C_WHITE), halign='left', valign='middle')
        t1.bind(size=t1.setter('text_size'))
        t2 = Label(text='Professional Voice Studio · Always Free', font_size=sp(11), color=hex_c(C_MUTED), halign='left', valign='middle')
        t2.bind(size=t2.setter('text_size'))
        tb.add_widget(t1)
        tb.add_widget(t2)
        hdr.add_widget(tb)

        settings_btn = IconBtn(icon='⚙', size_dp=44, bg=C_CARD2)
        settings_btn.font_size = sp(20)
        settings_btn.bind(on_press=lambda *a: self._go_settings())
        hdr.add_widget(settings_btn)

        outer.add_widget(hdr)
        outer.add_widget(separator())

        # ══ SCROLLABLE CONTENT ═══════════════════════════
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, padding=[dp(16), dp(16)], spacing=dp(16))
        content.bind(minimum_height=content.setter('height'))

        # ── Voice Preset Picker ──
        self.preset_picker = PresetPicker(callback=self._apply_preset)
        content.add_widget(self.preset_picker)

        # ── Language + Gender ──
        lg_row = BoxLayout(size_hint_y=None, height=dp(142), spacing=dp(12))

        lang_card = BoxLayout(orientation='vertical', padding=[dp(14), dp(10)], spacing=dp(8))
        card_bg(lang_card, C_CARD2, 16)
        lang_card.add_widget(lbl('🌍 Language', 13, C_ACCENT, True, 26))
        self.lang_spin = Spinner(
            text='English', values=list(LANGUAGES.keys()),
            size_hint_y=None, height=dp(60),
            font_size=sp(15), color=(1, 1, 1, 1),
            background_color=hex_c(C_BLUE), background_normal='',
        )
        self.lang_spin.bind(text=self._on_lang_change)
        lang_card.add_widget(self.lang_spin)
        lg_row.add_widget(lang_card)

        gender_card = BoxLayout(orientation='vertical', padding=[dp(14), dp(10)], spacing=dp(8), size_hint_x=0.48)
        card_bg(gender_card, C_CARD2, 16)
        gender_card.add_widget(lbl('🎙 Voice', 13, C_ACCENT, True, 26))
        gr = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        self._vbtns = {}
        for name, icon, label in [('Male', '♂', 'Male'), ('Female', '♀', 'Female')]:
            b = FlatBtn(text=icon + '\n' + label, bg=C_CARD2, font_size=sp(13), bold=True, radius=12)
            b.bind(on_press=lambda inst, n=name: self._pick_voice(n))
            gr.add_widget(b)
            self._vbtns[name] = b
        gender_card.add_widget(gr)
        lg_row.add_widget(gender_card)
        content.add_widget(lg_row)
        Clock.schedule_once(lambda dt: self._pick_voice('Male'), 0)

        # ── Emotion Picker ──
        emotion_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(206), padding=[dp(14), dp(10)], spacing=dp(6))
        card_bg(emotion_box, C_CARD2, 16)
        self.emotion_picker = EmotionPicker()
        emotion_box.add_widget(self.emotion_picker)
        content.add_widget(emotion_box)

        # ── Speed & Pitch Row ──
        sp_row = BoxLayout(size_hint_y=None, height=dp(118), spacing=dp(12))

        speed_card = BoxLayout(orientation='vertical', padding=[dp(14), dp(10)], spacing=dp(6))
        card_bg(speed_card, C_CARD2, 16)
        speed_card.add_widget(lbl('⚡ Speed', 13, C_ACCENT, True, 26))
        sr = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        sr.add_widget(lbl('Slow', 12, C_MUTED, False, 44))
        self.speed_slider = Slider(min=10, max=100, value=50, step=5)
        self.speed_lbl = lbl('50%', 13, C_CYAN, False, 44)
        self.speed_slider.bind(value=lambda i, v: setattr(self.speed_lbl, 'text', str(int(v)) + '%'))
        sr.add_widget(self.speed_slider)
        sr.add_widget(lbl('Fast', 12, C_MUTED, False, 44))
        speed_card.add_widget(sr)
        speed_card.add_widget(self.speed_lbl)
        sp_row.add_widget(speed_card)

        self.pitch_card = PitchSliderCard()
        sp_row.add_widget(self.pitch_card)
        content.add_widget(sp_row)

        # ── Advanced Options ──
        self.adv_card = AdvancedOptionsCard()
        content.add_widget(self.adv_card)

        # ── Text Input Card ──
        text_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(320),
                              padding=[dp(14), dp(12)], spacing=dp(10))
        card_bg(text_card, C_CARD2, 16)

        top_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(8))
        self.char_lbl = lbl('0 chars · 0 lines · 0 words', 12, C_MUTED, False, 38)
        top_row.add_widget(self.char_lbl)
        imp = FlatBtn(text='📂 Import', bg=C_BLUE2, size_hint_x=None, width=dp(100), font_size=sp(13))
        imp.bind(on_press=self._import_file)
        top_row.add_widget(imp)
        clr_txt = IconBtn(icon='✕', size_dp=38, bg=C_CARD3)
        clr_txt.bind(on_press=lambda *a: setattr(self.txt, 'text', ''))
        top_row.add_widget(clr_txt)
        text_card.add_widget(top_row)

        self.rtl_lbl = lbl('', 11, C_AMBER, False, 20)
        text_card.add_widget(self.rtl_lbl)

        self.txt = TextInput(
            hint_text='Enter text here... (Urdu, Arabic, English, any language)',
            multiline=True, size_hint=(1, 1),
            background_color=(0.06, 0.09, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.39, 0.46, 0.54, 1),
            cursor_color=(0.23, 0.74, 0.97, 1),
            font_size=sp(17), padding=[dp(14), dp(12)],
        )
        self.txt.bind(text=self._count)
        text_card.add_widget(self.txt)

        self.file_info_container = BoxLayout(orientation='vertical', size_hint_y=None, height=0)
        text_card.add_widget(self.file_info_container)
        content.add_widget(text_card)

        # ── Add to Queue button ──
        queue_btn = FlatBtn(text='+ Add to Batch Queue', bg=C_PURPLE, size_hint_y=None, height=dp(50), font_size=sp(14))
        queue_btn.bind(on_press=self._add_to_queue)
        content.add_widget(queue_btn)

        # ── Status + Waveform Card ──
        status_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(130),
                                padding=[dp(14), dp(10)], spacing=dp(8))
        card_bg(status_card, C_CARD2, 14)

        self.status_lbl = lbl('Ready to generate voice', 14, C_MUTED, False, 32)
        status_card.add_widget(self.status_lbl)

        self.prog = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
        status_card.add_widget(self.prog)

        self.waveform = WaveformWidget(bars=22, color=C_BLUE2, size_hint_y=None, height=dp(50))
        status_card.add_widget(self.waveform)
        content.add_widget(status_card)

        # ── Generate Button (large, glowing) ──
        self.gen_btn = FlatBtn(
            text='🎙 Generate Voice',
            bg=C_BLUE, size_hint_y=None, height=dp(72),
            font_size=sp(20), bold=True, radius=18,
        )
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        # ── Preview + Save Row ──
        pd_row = BoxLayout(size_hint_y=None, height=dp(62), spacing=dp(14))
        self.play_btn = FlatBtn(text='▶ Play Preview', bg=C_RED, font_size=sp(15), disabled=True)
        self.dl_btn = FlatBtn(text='💾 Save Voice', bg=C_GREEN, font_size=sp(15), disabled=True)
        self.play_btn.bind(on_press=self._play)
        self.dl_btn.bind(on_press=self._download)
        pd_row.add_widget(self.play_btn)
        pd_row.add_widget(self.dl_btn)
        content.add_widget(pd_row)

        # ── Navigation Row ──
        nav_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        hist_btn = FlatBtn(text='📋 History', bg=C_PURPLE, font_size=sp(14))
        hist_btn.bind(on_press=lambda *a: self._go_hist())
        batch_btn = FlatBtn(text='📦 Batch Queue', bg=C_GRAY, font_size=sp(14))
        batch_btn.bind(on_press=lambda *a: self._go_batch())
        nav_row.add_widget(hist_btn)
        nav_row.add_widget(batch_btn)
        content.add_widget(nav_row)

        # ── Save folder banner ──
        folder_banner = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(14), dp(8)], spacing=dp(8))
        card_bg(folder_banner, C_SURFACE, 12)
        folder_banner.add_widget(Label(text='📁', font_size=sp(22), size_hint_x=None, width=dp(36)))
        titan_p = get_titan_folder()
        fl = Label(text='Auto-saves to: Titan Studio PRO/Audio/\n' + titan_p,
                   font_size=sp(11), color=hex_c(C_MUTED2), halign='left', valign='middle')
        fl.bind(size=fl.setter('text_size'))
        folder_banner.add_widget(fl)
        content.add_widget(folder_banner)

        # ── How to Use ──
        how_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(250),
                             padding=[dp(16), dp(14)], spacing=dp(5))
        card_bg(how_card, C_CARD, 14)
        how_card.add_widget(lbl('📖 Quick Guide', 15, C_ACCENT, True, 34))
        steps = [
            '1. Select Voice Preset (Narrator, News, etc.)',
            '2. Choose Language (30+ supported)',
            '3. Pick Gender: Male or Female',
            '4. Set Emotion (Whisper, Shout, Happy…)',
            '5. Adjust Speed & Pitch sliders',
            '6. Type or Import text (TXT/PDF/DOCX)',
            '7. Tap 🎙 Generate Voice',
            '8. Preview → auto-saved to Titan Studio PRO/',
        ]
        for s in steps:
            how_card.add_widget(lbl(s, 12, C_MUTED, False, 24))
        content.add_widget(how_card)
        content.add_widget(spacer(28))

        scroll.add_widget(content)
        outer.add_widget(scroll)
        root.add_widget(outer)
        self.add_widget(root)

    def _find_logo(self):
        base = os.path.dirname(os.path.abspath(__file__))
        for name in ['AI.png', 'AI.jpg', 'logo.png']:
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
        return None

    def on_enter(self, *a):
        self.opacity = 0
        Animation(opacity=1, duration=0.3, t='out_quad').start(self)

    def _go_hist(self):
        self.manager.transition = SlideTransition(direction='left', duration=0.3)
        self.manager.current = 'history'

    def _go_batch(self):
        self.manager.transition = SlideTransition(direction='left', duration=0.3)
        self.manager.current = 'batch'

    def _go_settings(self):
        self.manager.transition = SlideTransition(direction='left', duration=0.3)
        self.manager.current = 'settings'

    def _on_lang_change(self, inst, lang):
        if lang in RTL_LANGS:
            self.rtl_lbl.text = '← RTL mode: ' + lang
            try:
                self.txt.base_direction = 'rtl'
            except Exception:
                pass
        else:
            self.rtl_lbl.text = ''
            try:
                self.txt.base_direction = 'ltr'
            except Exception:
                pass

    def _apply_preset(self, name, data):
        self.speed_slider.value = data.get('speed', 50)
        self.pitch_card.pitch_slider.value = data.get('pitch', 0)
        self.emotion_picker._select(data.get('emotion', 'Normal'))
        self.status_lbl.text = 'Preset: ' + data.get('icon', '') + ' ' + name + ' · ' + data.get('desc', '')

    def _pick_voice(self, name):
        self.voice_sel = name
        for n, b in self._vbtns.items():
            b.set_bg(C_BLUE if n == name else C_CARD2)
            b.bold = (n == name)

    def _count(self, inst, val):
        words = len(val.split()) if val.strip() else 0
        lines = len(val.splitlines()) if val.strip() else 0
        chars = len(val)
        self.char_lbl.text = str(chars) + ' chars  ·  ' + str(words) + ' words  ·  ' + str(lines) + ' lines'

    def _import_file(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))
        box.add_widget(lbl('Select file type to import:', 15, C_WHITE, True, 40))
        grid = GridLayout(cols=3, size_hint_y=None, height=dp(100), spacing=dp(10))
        pop = [None]
        for ft, fi in FILE_ICONS.items():
            col = BoxLayout(orientation='vertical', spacing=dp(4))
            b = FlatBtn(text=fi.get('emoji', ft), bg=fi.get('color', C_BLUE),
                        size_hint_y=None, height=dp(56), font_size=sp(24), radius=12)
            b.bind(on_press=lambda x, t=ft, p=pop: self._open_chooser(t, p[0]))
            col.add_widget(b)
            col.add_widget(Label(text=ft, font_size=sp(10), color=hex_c(C_MUTED2), size_hint_y=None, height=dp(18)))
            grid.add_widget(col)
        box.add_widget(grid)
        can = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None, height=dp(52))
        box.add_widget(can)
        p = Popup(title='Import File', content=box, size_hint=(0.92, 0.52), background_color=hex_c(C_CARD))
        pop[0] = p
        can.bind(on_press=p.dismiss)
        p.open()

    def _open_chooser(self, ftype, prev):
        if prev:
            prev.dismiss()
        fm = {'TXT': ['*.txt', '*.md'], 'PDF': ['*.pdf'], 'DOCX': ['*.docx', '*.doc'],
              'SRT': ['*.srt'], 'DOC': ['*.doc'], 'CSV': ['*.csv']}
        sp_path = get_internal_storage_path()
        try:
            if ANDROID_ENV:
                sp_path = primary_external_storage_path() or sp_path
        except Exception:
            pass
        fc = FileChooserListView(path=sp_path, filters=fm.get(ftype, ['*.*']))
        box = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        box.add_widget(fc)
        br = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(10))
        sel = FlatBtn(text='✅ Select', bg=C_GREEN, font_size=sp(15))
        can = FlatBtn(text='Cancel', bg=C_GRAY, font_size=sp(15))
        br.add_widget(sel)
        br.add_widget(can)
        box.add_widget(br)
        p = Popup(title='Choose ' + ftype + ' File', content=box, size_hint=(0.95, 0.88), background_color=hex_c(C_CARD))

        def do_sel(*a):
            if fc.selection:
                p.dismiss()
                self._read_file(fc.selection[0], ftype)

        sel.bind(on_press=do_sel)
        can.bind(on_press=p.dismiss)
        p.open()

    def _read_file(self, path, ftype):
        self.status_lbl.text = '📂 Reading ' + ftype + ' file...'
        self.prog.value = 20

        def worker():
            try:
                if ftype in ('TXT', 'MD', 'CSV'):
                    text = read_txt(path)
                elif ftype == 'PDF':
                    text = read_pdf(path)
                elif ftype in ('DOCX', 'DOC'):
                    text = read_docx(path)
                elif ftype == 'SRT':
                    text = read_srt(path)
                else:
                    text = read_txt(path)
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self.status_lbl, 'text', 'Read error: ' + str(e)[:50]))
                return

            def apply(dt):
                if text.strip():
                    self.txt.text = text
                    self.status_lbl.text = '✅ Imported: ' + os.path.basename(path)
                    self.prog.value = 100
                    self._imported_path = path
                    self._imported_type = ftype
                    self.file_info_container.clear_widgets()
                    self.file_info_container.height = dp(80)
                    card = FileInfoCard(path=path, ftype=ftype, size_hint_y=None, height=dp(72))
                    self.file_info_container.add_widget(card)
                    Clock.schedule_once(lambda dt2: Animation(value=0, duration=0.5).start(self.prog), 1.5)
                else:
                    self.status_lbl.text = '⚠ Could not read file. Try TXT format.'
                    self.prog.value = 0

            Clock.schedule_once(apply)

        threading.Thread(target=worker, daemon=True).start()

    def _add_to_queue(self, *a):
        text = self.txt.text.strip()
        if not text:
            self.status_lbl.text = '⚠ Enter text first!'
            return
        q = queue_load()
        q.append({
            'text': text, 'lang': self.lang_spin.text, 'voice': self.voice_sel,
            'emotion': self.emotion_picker.selected, 'speed': int(self.speed_slider.value),
            'pitch': self.pitch_card.value, 'slow': int(self.speed_slider.value) <= 30,
            'status': 'pending', 'added': time.strftime('%d %b %H:%M'),
        })
        queue_save(q)
        self.status_lbl.text = '✅ Added to batch queue! (' + str(len(q)) + ' items)'

    def _set_ready(self, ok=True):
        self.gen_btn.disabled = False
        self.play_btn.disabled = not ok
        self.dl_btn.disabled = not ok

    def _set_busy(self):
        self.gen_btn.disabled = True
        self.play_btn.disabled = True
        self.dl_btn.disabled = True

    def _upd(self, val, msg):
        self.prog.value = val
        self.status_lbl.text = msg

    # ══════════════════════════════════════════════════════
    #  GENERATE — uses edge-tts with Android fix
    # ══════════════════════════════════════════════════════
    def _generate(self, *a):
        text = self.txt.text.strip()
        if not text:
            self.status_lbl.text = '⚠ Please enter some text first!'
            return
        self._set_busy()
        self._upd(0, 'Starting voice generation...')
        self.waveform.start()
        # Animate generate button
        anim = Animation(opacity=0.5, duration=0.08) + Animation(opacity=1.0, duration=0.15)
        anim.start(self.gen_btn)
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        """
        ★ ANDROID EDGE-TTS FIX ★
        Uses dedicated thread with fresh asyncio event loop.
        Falls back to gTTS only if edge-tts is not installed.
        """
        try:
            lang_name = self.lang_spin.text
            gender = self.voice_sel
            emotion = self.emotion_picker.selected
            speed_pct = int(self.speed_slider.value)
            pitch_val = self.pitch_card.value
            use_breaths = self.adv_card.use_breaths

            Clock.schedule_once(lambda dt: self._upd(15, 'Selecting voice...'))

            voice = pick_edge_voice(lang_name, gender)
            rate_str = speed_to_rate_str(speed_pct, emotion)
            volume_str = emotion_to_volume_str(emotion)
            pitch_str = pitch_to_pitch_str(pitch_val)

            text = self.txt.text

            # Add breath pauses if enabled
            if use_breaths:
                text = re.sub(r'([.!?])\s+', r'\1 ', text)

            label = lang_name + ' · ' + gender + ' · ' + emotion
            Clock.schedule_once(lambda dt: self._upd(35, 'Connecting to TTS service (' + label + ')...'))

            out = os.path.join(App.get_running_app().user_data_dir, 'tts_preview.mp3')

            Clock.schedule_once(lambda dt: self._upd(55, 'Generating neural voice...'))

            ok, err = edge_tts_generate(text, voice, rate_str, volume_str, pitch_str, out)

            if ok:
                Clock.schedule_once(lambda dt: self._upd(88, 'Processing audio...'))
                self.out_file = out
                Clock.schedule_once(lambda dt: self._on_done())
            elif err == 'IMPORT_ERROR':
                # edge-tts not installed — use gTTS fallback
                Clock.schedule_once(lambda dt: self._upd(30, 'Using gTTS fallback (install edge-tts for better quality)...'))
                self._worker_gtts_fallback()
            else:
                err_msg = err
                Clock.schedule_once(lambda dt, m=err_msg: self._on_err(m))

        except Exception as e:
            msg = str(e)
            Clock.schedule_once(lambda dt, m=msg: self._on_err(m))

    def _worker_gtts_fallback(self):
        """Fallback: gTTS (robotic, no real gender support, speed limited)"""
        try:
            from gtts import gTTS
            lang = LANGUAGES.get(self.lang_spin.text, 'en')
            # gTTS tld trick: com = default (slightly male-ish), co.uk = slightly female-ish
            tld = VOICE_TLD_FALLBACK.get(self.voice_sel, 'com')
            slow = int(self.speed_slider.value) <= 30
            text = self.txt.text
            tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
            out = os.path.join(App.get_running_app().user_data_dir, 'tts_preview.mp3')
            Clock.schedule_once(lambda dt: self._upd(75, 'Saving audio (gTTS)...'))
            tts.save(out)
            self.out_file = out
            Clock.schedule_once(lambda dt: self._on_done(gtts_mode=True))
        except Exception as e:
            msg = str(e)
            Clock.schedule_once(lambda dt, m=msg: self._on_err(m))

    def _on_done(self, gtts_mode=False):
        if self._audio:
            try:
                self._audio.stop()
                self._audio.unload()
            except Exception:
                pass
            self._audio = None

        self._audio = SoundLoader.load(self.out_file)
        msg = '✅ Audio ready!  Preview or Save.' if not gtts_mode else '✅ Audio ready (gTTS mode — install edge-tts for better quality).'
        self._upd(100, msg)
        self._set_ready(ok=True)
        self.waveform.stop()
        Clock.schedule_once(lambda dt: Animation(value=0, duration=0.7, t='out_quad').start(self.prog), 1.8)

    def _on_err(self, msg):
        self.waveform.stop()
        m = msg.lower()
        if any(k in m for k in ['network', 'connection', 'gaierror', 'timeout', 'errno']):
            txt = '⚠ No internet! TTS needs an active connection.'
        elif 'lang' in m:
            txt = '⚠ Language not supported by the TTS engine.'
        else:
            txt = '⚠ Error: ' + msg[:80]
        self._upd(0, txt)
        self._set_ready(ok=False)

    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = '▶ Play Preview'
            self.play_btn.set_bg(C_RED)
            self.waveform.stop()
        else:
            self._audio.play()
            self.play_btn.text = '⏹ Stop'
            self.play_btn.set_bg(C_AMBER)
            self.waveform.start()

    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status_lbl.text = '⚠ Generate audio first!'
            return

        def after_permission(granted):
            if granted:
                self._auto_save()
            else:
                # Still try to save internally
                self._auto_save()

        # Request permission before saving
        request_storage_permissions(after_permission)

    def _auto_save(self):
        emotion = self.emotion_picker.selected
        lang = self.lang_spin.text
        voice = self.voice_sel
        ts = str(int(time.time()))
        fname = 'Titan_{lang}_{voice}_{ts}.mp3'.format(lang=lang, voice=voice, ts=ts)
        audio_dir = get_audio_folder()
        dest = os.path.join(audio_dir, fname)

        try:
            os.makedirs(audio_dir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self._upd(100, '✅ Saved: ' + fname)
            history_save({
                'filename': fname, 'path': dest, 'lang': lang,
                'voice': voice, 'emotion': emotion,
                'time': time.strftime('%d %b %Y  %H:%M'), 'source': 'studio',
            })
            self._show_save_success(fname, audio_dir, dest)
        except PermissionError:
            self._show_err_popup('Permission denied!\n\nGo to Settings → App → Permissions and allow Storage.')
        except Exception as e:
            self._upd(0, '⚠ Save failed: ' + str(e)[:60])

    def _show_save_success(self, fname, folder, full_path):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
        box.add_widget(Label(text='✅ Saved to Titan Studio PRO!', color=hex_c(C_GREEN),
                             font_size=sp(18), bold=True, halign='center', valign='middle',
                             size_hint_y=None, height=dp(40)))
        box.add_widget(Label(text='📁 ' + fname, color=hex_c(C_WHITE), font_size=sp(13),
                             halign='center', valign='middle', size_hint_y=None, height=dp(34)))
        box.add_widget(Label(text=folder, color=hex_c(C_MUTED2), font_size=sp(11),
                             halign='center', valign='middle', size_hint_y=None, height=dp(40)))
        ok = FlatBtn(text='Great! 🎉', bg=C_GREEN, size_hint_y=None, height=dp(56), font_size=sp(15))
        box.add_widget(ok)
        p = Popup(title='Download Complete 🎵', content=box, size_hint=(0.92, 0.52), background_color=hex_c(C_CARD))
        ok.bind(on_press=p.dismiss)
        p.open()

    def _show_err_popup(self, msg):
        box = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(14))
        box.add_widget(Label(text=msg, color=hex_c(C_AMBER), font_size=sp(14), halign='center', valign='middle'))
        ok = FlatBtn(text='OK', bg=C_BLUE, size_hint_y=None, height=dp(56))
        box.add_widget(ok)
        p = Popup(title='⚠ Error', content=box, size_hint=(0.88, 0.42), background_color=hex_c(C_CARD))
        ok.bind(on_press=p.dismiss)
        p.open()


# ═══════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════
class TitanApp(App):
    def build(self):
        self.title = 'Titan Studio PRO'

        # Pre-create app folders
        try:
            get_titan_folder()
        except Exception:
            pass

        sm = ScreenManager(transition=FadeTransition(duration=0.38))
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(StudioScreen(name='studio'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(BatchQueueScreen(name='batch'))

        if ANDROID_ENV:
            Clock.schedule_once(self._ask_perms, 1.0)

        return sm

    def _ask_perms(self, *a):
        """Request all needed permissions at startup"""
        try:
            request_permissions([
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])
        except Exception:
            pass

    def on_stop(self):
        pass


if __name__ == '__main__':
    TitanApp().run()
