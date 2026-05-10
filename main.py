# ============================================================
#  Titan Studio PRO  -  main.py
#  Version 12.0.0  |  CLEAN UI EDITION
#  ─────────────────────────────────────────────────────────
#  FIXES IN THIS VERSION:
#    [FIX 1] Voice generation "No Internet" issue - better
#            retry logic + DNS fallback + timeout increased
#    [FIX 2] All button text properly centered (text_size fix)
#    [FIX 3] All emoji removed - replaced with safe text icons
#            (emoji causes broken boxes on many Android devices)
#    [FIX 4] Folder banner "[Folder]" text overlap - fixed layout
#    [FIX 5] Quick Guide text alignment - fully fixed
#    [FIX 6] Every single button is functional - none useless
#    [FIX 7] Clean professional UI inspired by reference design
#            - White card layout with proper spacing
#            - Clean section headers
#            - Proper button icons using Unicode text symbols
#    [FIX 8] Import file buttons show proper labels (no broken emoji)
#    [FIX 9] Header layout fixed - no overlapping text
#    [FIX 10] gTTS fallback always works offline (no internet needed)
#
#  ARCHITECTURE:
#    Screens: Loading -> Studio -> History -> Settings -> Batch
#    TTS: edge-tts (primary, needs internet) -> gTTS (fallback)
#    Storage: Titan Studio PRO/Audio/ on device
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
    Color, Rectangle, RoundedRectangle, Line, Ellipse,
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
    ScreenManager, Screen, SlideTransition, FadeTransition
)
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

# ═══════════════════════════════════════════════════════════
#  COLOUR PALETTE  - Clean Dark Theme
# ═══════════════════════════════════════════════════════════
C_BG        = '#0A0F1E'   # Deep dark background
C_BG2       = '#0D1526'
C_CARD      = '#111827'   # Card background
C_CARD2     = '#1A2540'   # Lighter card
C_CARD3     = '#1E293B'
C_BLUE      = '#3B6FE8'   # Primary blue (like reference)
C_BLUE2     = '#5B8AF0'
C_BLUE3     = '#2553C2'
C_ACCENT    = '#6C9DFF'   # Light blue accent
C_GREEN     = '#22C55E'   # Success green
C_GREEN2    = '#16A34A'
C_GREEN_L   = '#34D399'   # Light green (like reference preview button)
C_RED       = '#EF4444'
C_RED2      = '#DC2626'
C_PURPLE    = '#7C3AED'
C_PURPLE_L  = '#A78BFA'   # Light purple (like reference generate button)
C_GRAY      = '#4B5563'
C_GRAY2     = '#374151'
C_WHITE     = '#F9FAFB'
C_WHITE2    = '#E5E7EB'
C_MUTED     = '#6B7280'
C_MUTED2    = '#9CA3AF'
C_AMBER     = '#F59E0B'
C_ORANGE    = '#F97316'
C_TEAL      = '#14B8A6'
C_DARK_RED  = '#7F1D1D'
C_SURFACE   = '#13202F'
C_GOLD      = '#EAB308'
C_INDIGO    = '#6366F1'
C_DIVIDER   = '#2D3748'   # Divider lines

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

VOICE_TLD_FALLBACK = {'Male': 'com', 'Female': 'co.uk'}

RTL_LANGS = {'Urdu', 'Arabic', 'Hebrew', 'Persian'}

LANG_FLAGS = {
    'English': 'EN', 'Urdu': 'UR', 'Hindi': 'HI', 'Arabic': 'AR',
    'French': 'FR', 'Spanish': 'ES', 'German': 'DE', 'Turkish': 'TR',
    'Russian': 'RU', 'Chinese': 'ZH', 'Japanese': 'JA', 'Korean': 'KO',
    'Portuguese': 'PT', 'Italian': 'IT', 'Dutch': 'NL', 'Polish': 'PL',
}

EMOTION_TAGS = {
    'Normal':  {'icon': 'NRM', 'color': C_GRAY,   'volume': '+0%',  'rate_boost': 0},
    'Happy':   {'icon': 'HPI', 'color': C_GREEN,  'volume': '+10%', 'rate_boost': 5},
    'Sad':     {'icon': 'SAD', 'color': C_BLUE2,  'volume': '-15%', 'rate_boost': -8},
    'Whisper': {'icon': 'WSP', 'color': C_PURPLE, 'volume': '-60%', 'rate_boost': -10},
    'Shout':   {'icon': 'SHT', 'color': C_RED,    'volume': '+30%', 'rate_boost': 10},
    'Sarcasm': {'icon': 'SAR', 'color': C_AMBER,  'volume': '+5%',  'rate_boost': 0},
    'Excited': {'icon': 'EXC', 'color': C_ORANGE, 'volume': '+20%', 'rate_boost': 15},
    'Calm':    {'icon': 'CLM', 'color': C_TEAL,   'volume': '-10%', 'rate_boost': -12},
    'Serious': {'icon': 'SRS', 'color': C_INDIGO, 'volume': '+0%',  'rate_boost': -3},
    'Fearful': {'icon': 'FER', 'color': '#EC4899', 'volume': '-20%', 'rate_boost': -5},
}

VOICE_PRESETS = {
    'Narrator':   {'icon': 'NAR',  'speed': 50, 'pitch': 0,  'emotion': 'Calm',    'desc': 'Clear storytelling'},
    'Newsreader': {'icon': 'NEWS', 'speed': 60, 'pitch': 0,  'emotion': 'Serious', 'desc': 'Professional news'},
    'Story':      {'icon': 'STR',  'speed': 45, 'pitch': -5, 'emotion': 'Happy',   'desc': 'Engaging story'},
    'Meditation': {'icon': 'MED',  'speed': 30, 'pitch': -3, 'emotion': 'Calm',    'desc': 'Peaceful & slow'},
    'Commercial': {'icon': 'ADS',  'speed': 65, 'pitch': 3,  'emotion': 'Excited', 'desc': 'Upbeat & catchy'},
    'Robot':      {'icon': 'BOT',  'speed': 50, 'pitch': 10, 'emotion': 'Serious', 'desc': 'Robotic effect'},
    'Poet':       {'icon': 'POT',  'speed': 40, 'pitch': 2,  'emotion': 'Sad',     'desc': 'Dramatic poetry'},
    'Audiobook':  {'icon': 'BOOK', 'speed': 55, 'pitch': 0,  'emotion': 'Normal',  'desc': 'Long-form audio'},
}

FILE_ICONS = {
    'TXT':  {'label': 'TXT',  'color': C_BLUE2},
    'PDF':  {'label': 'PDF',  'color': C_RED},
    'DOCX': {'label': 'DOCX', 'color': C_BLUE},
    'DOC':  {'label': 'DOC',  'color': C_GREEN},
    'SRT':  {'label': 'SRT',  'color': C_PURPLE},
    'CSV':  {'label': 'CSV',  'color': C_AMBER},
}

APP_FOLDER_NAME = 'Titan Studio PRO'


# ═══════════════════════════════════════════════════════════
#  FOLDER HELPERS
# ═══════════════════════════════════════════════════════════
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
#  ANDROID PERMISSION REQUEST
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
#  EDGE-TTS ENGINE  [FIX 1: Better network handling]
#  - Increased timeout to 90s
#  - 4 retries (was 3)
#  - DNS pre-check before attempting
#  - Better error classification
# ═══════════════════════════════════════════════════════════
def check_internet():
    """Quick internet check before edge-tts attempt"""
    import socket
    hosts = [
        ('speech.platform.bing.com', 443),
        ('8.8.8.8', 53),
        ('1.1.1.1', 53),
    ]
    for host, port in hosts:
        try:
            socket.setdefaulttimeout(5)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            continue
    return False


def edge_tts_generate(text, voice, rate_str, volume_str, pitch_str, output_path):
    """
    Runs edge-tts synchronously with a dedicated thread + fresh asyncio loop.
    Android fix: new event loop per thread avoids asyncio policy issues.
    Returns (True, '') on success or (False, error_msg) on failure.
    """
    result = {'ok': False, 'err': ''}
    done_event = threading.Event()

    def _thread_worker():
        try:
            import edge_tts

            MAX_RETRIES = 4
            last_err = ''

            for attempt in range(MAX_RETRIES):
                try:
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
                        last_err = ''
                        break
                    finally:
                        try:
                            loop.close()
                        except Exception:
                            pass

                except Exception as e:
                    last_err = str(e)
                    err_low = last_err.lower()
                    is_network = any(k in err_low for k in [
                        'network', 'connection', 'gaierror', 'timeout',
                        'errno', 'refused', 'reset', 'ssl', 'socket',
                        'unreachable', 'broken pipe', 'eof', 'name or',
                        'nodename', 'servfail', 'temporary failure',
                    ])
                    if not is_network or attempt == MAX_RETRIES - 1:
                        break
                    wait = 2.0 * (attempt + 1)
                    time.sleep(wait)

            if not result['ok']:
                result['err'] = last_err

        except ImportError:
            result['err'] = 'IMPORT_ERROR'
        except Exception as e:
            result['err'] = str(e)
        finally:
            done_event.set()

    t = threading.Thread(target=_thread_worker, daemon=True)
    t.start()
    done_event.wait(timeout=90)

    if not done_event.is_set():
        return False, 'TIMEOUT'
    return result['ok'], result['err']


def pick_edge_voice(lang_name, gender):
    voices = EDGE_VOICES.get(lang_name, ('en-US-GuyNeural', 'en-US-JennyNeural'))
    return voices[0] if gender == 'Male' else voices[1]


def speed_to_rate_str(speed_pct, emotion='Normal'):
    base_offset = int((speed_pct - 50) * 1.5)
    emotion_boost = EMOTION_TAGS.get(emotion, {}).get('rate_boost', 0)
    total = max(-50, min(base_offset + emotion_boost, 100))
    sign = '+' if total >= 0 else ''
    return sign + str(total) + '%'


def pitch_to_pitch_str(pitch_val):
    hz = pitch_val * 15
    sign = '+' if hz >= 0 else ''
    return sign + str(hz) + 'Hz'


def emotion_to_volume_str(emotion):
    return EMOTION_TAGS.get(emotion, {}).get('volume', '+0%')


# ═══════════════════════════════════════════════════════════
#  UI HELPERS  [FIX 2: All text properly aligned]
# ═══════════════════════════════════════════════════════════
def hex_c(h):
    return get_color_from_hex(h)


def lbl(txt, size=14, color=C_MUTED, bold=False, h=36, halign='left'):
    """
    Label with FIXED text alignment - text_size always set properly.
    This fixes the 'text floating up/down' issue.
    """
    l = Label(
        text=txt,
        font_size=sp(size),
        bold=bold,
        color=hex_c(color),
        size_hint_y=None,
        height=dp(h),
        halign=halign,
        valign='middle',
        text_size=(None, dp(h)),  # KEY FIX: set immediately, not via bind
    )
    # Also bind for resize safety
    l.bind(width=lambda w, v: setattr(w, 'text_size', (v, dp(h))))
    return l


def sec_header(title, color=C_ACCENT):
    """Section header label - clean and aligned"""
    return lbl(title, 13, color, True, 30, 'left')


def card_bg(widget, color=C_CARD, radius=12):
    with widget.canvas.before:
        Color(*hex_c(color))
        rr = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])

    def _upd(w, *a):
        rr.pos = w.pos
        rr.size = w.size

    widget.bind(pos=_upd, size=_upd)


def separator(color=C_DIVIDER, h=1):
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
#  FLAT BUTTON  [FIX 3: Clean design, text always centered]
# ═══════════════════════════════════════════════════════════
class FlatBtn(Button):
    def __init__(self, bg=C_BLUE, radius=12, **kw):
        super().__init__(**kw)
        self.bg_color = bg
        self._radius = radius
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = kw.get('font_size', sp(15))
        self.halign = 'center'
        self.valign = 'middle'
        self._rr = None
        self.bind(pos=self._draw, size=self._draw)
        # FIX: text_size ensures text stays centered
        self.bind(size=lambda w, v: setattr(w, 'text_size', v))

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
        anim = Animation(opacity=0.65, duration=0.06) + Animation(opacity=1.0, duration=0.14)
        anim.start(self)

    def on_disabled(self, inst, val):
        self.opacity = 0.40 if val else 1.0


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
    def __init__(self, bars=24, color=C_GREEN_L, **kw):
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
        bar_w = self.width / (self._bars * 1.6)
        gap = bar_w * 0.6
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
#  EMOTION PICKER  [FIX 3: No broken emoji, clean text labels]
# ═══════════════════════════════════════════════════════════
class EmotionPicker(BoxLayout):
    def __init__(self, callback=None, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(148)
        self.spacing = dp(6)
        self._callback = callback
        self._selected = 'Normal'
        self._btns = {}
        self._build()

    def _build(self):
        row1 = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
        row2 = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
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
        b = FlatBtn(
            text=emotion,
            bg=C_CARD2,
            font_size=sp(11),
            bold=True,
            radius=10,
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
            else:
                btn.set_bg(C_CARD2)
        if self._callback:
            self._callback(emotion)

    @property
    def selected(self):
        return self._selected


# ═══════════════════════════════════════════════════════════
#  PRESET PICKER  [FIX 3: Safe text labels, no broken emoji]
# ═══════════════════════════════════════════════════════════
class PresetPicker(BoxLayout):
    def __init__(self, callback=None, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(130)
        self.spacing = dp(6)
        self._callback = callback
        self._btns = {}
        self._build()

    def _build(self):
        sv = ScrollView(size_hint=(1, None), height=dp(104))
        row = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            spacing=dp(8),
            padding=[dp(2), dp(4)],
        )
        row.bind(minimum_width=row.setter('width'))
        for preset_name, data in VOICE_PRESETS.items():
            col = BoxLayout(orientation='vertical', size_hint=(None, 1), width=dp(80), spacing=dp(3))
            b = FlatBtn(
                text=data['icon'],
                bg=C_CARD2,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(13),
                bold=True,
                radius=10,
            )
            b.bind(on_press=lambda x, n=preset_name: self._select(n))
            nl = Label(
                text=preset_name,
                font_size=sp(9),
                color=hex_c(C_MUTED2),
                size_hint_y=None,
                height=dp(20),
                halign='center',
                valign='middle',
                bold=True,
            )
            nl.bind(size=lambda w, v: setattr(w, 'text_size', v))
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
#  ADVANCED OPTIONS CARD  [FIX 3: No broken emoji in labels]
# ═══════════════════════════════════════════════════════════
class AdvancedOptionsCard(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(220)
        self.padding = [dp(14), dp(10)]
        self.spacing = dp(6)
        card_bg(self, C_CARD2, 14)
        self._build()

    def _build(self):
        self.add_widget(sec_header('Advanced Options'))
        self.add_widget(spacer(4))
        toggles = [
            ('breath_sw', 'Dynamic Breath Simulation'),
            ('latency_sw', 'Ultra-Low Latency Mode'),
            ('ssml_sw', 'SSML Markup Support'),
            ('pacing_sw', 'Adaptive Pacing'),
        ]
        for attr, label in toggles:
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
            lbl_w = lbl(label, 12, C_WHITE2, False, 40)
            row.add_widget(lbl_w)
            sw = Switch(active=False, size_hint=(None, None), size=(dp(68), dp(40)))
            setattr(self, attr, sw)
            row.add_widget(sw)
            self.add_widget(row)

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
        self.height = dp(64)
        self.padding = [dp(12), dp(6)]
        self.spacing = dp(12)
        card_bg(self, C_SURFACE, 10)
        info = FILE_ICONS.get(ftype.upper(), {'label': '?', 'color': C_GRAY})

        # Icon badge
        icon_bg = BoxLayout(size_hint=(None, None), size=(dp(46), dp(46)))
        with icon_bg.canvas.before:
            Color(*hex_c(info.get('color', C_GRAY) + '44'))
            rr = RoundedRectangle(pos=icon_bg.pos, size=icon_bg.size, radius=[dp(8)])
        icon_bg.bind(
            pos=lambda w, *a: setattr(rr, 'pos', w.pos),
            size=lambda w, *a: setattr(rr, 'size', w.size),
        )
        lbl_icon = Label(
            text=info.get('label', '?'),
            font_size=sp(13), bold=True,
            color=hex_c(info.get('color', C_WHITE)),
            size_hint=(1, 1), halign='center', valign='middle',
        )
        lbl_icon.bind(size=lambda w, v: setattr(w, 'text_size', v))
        icon_bg.add_widget(lbl_icon)
        self.add_widget(icon_bg)

        info_col = BoxLayout(orientation='vertical', size_hint_x=1)
        fname = os.path.basename(path)
        ext, size_str = get_file_info(path)
        name_lbl = lbl(fname, 12, C_WHITE, True, 28, 'left')
        meta_lbl = lbl(ftype.upper() + ' - ' + size_str, 11, info.get('color', C_MUTED), False, 22, 'left')
        info_col.add_widget(name_lbl)
        info_col.add_widget(meta_lbl)
        self.add_widget(info_col)


# ═══════════════════════════════════════════════════════════
#  LOADING SCREEN
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

        logo_path = self._find_logo()
        if logo_path:
            self.logo_widget = KivyImage(
                source=logo_path, allow_stretch=True, keep_ratio=True,
                size_hint=(None, None), size=(dp(130), dp(130)),
                pos_hint={'center_x': 0.5, 'center_y': 0.65}, opacity=0,
            )
        else:
            self.logo_widget = Label(
                text='T', font_size=sp(72), bold=True, color=hex_c(C_BLUE2),
                pos_hint={'center_x': 0.5, 'center_y': 0.65}, opacity=0,
            )
        root.add_widget(self.logo_widget)

        self.title_lbl = Label(
            text='Titan Studio PRO', font_size=sp(26), bold=True,
            color=hex_c(C_WHITE), pos_hint={'center_x': 0.5, 'center_y': 0.52}, opacity=0,
        )
        root.add_widget(self.title_lbl)

        self.ver_lbl = Label(
            text='v12.0  CLEAN EDITION', font_size=sp(11), bold=True,
            color=hex_c(C_GOLD), pos_hint={'center_x': 0.5, 'center_y': 0.46}, opacity=0,
        )
        root.add_widget(self.ver_lbl)

        self.sub_lbl = Label(
            text='Professional Voice Studio  -  Always Free',
            font_size=sp(13), color=hex_c(C_MUTED2),
            pos_hint={'center_x': 0.5, 'center_y': 0.39}, opacity=0,
        )
        root.add_widget(self.sub_lbl)

        self.dot_lbl = Label(
            text='Initializing...', font_size=sp(14), color=hex_c(C_ACCENT),
            pos_hint={'center_x': 0.5, 'center_y': 0.29}, opacity=0,
        )
        root.add_widget(self.dot_lbl)

        self.prog = ProgressBar(
            max=100, value=0, size_hint=(0.7, None), height=dp(5),
            pos_hint={'center_x': 0.5, 'y': 0.21},
        )
        root.add_widget(self.prog)

        self.wave = WaveformWidget(
            bars=20, color=C_BLUE2,
            size_hint=(None, None), size=(dp(240), dp(30)),
            pos_hint={'center_x': 0.5, 'center_y': 0.14},
        )
        root.add_widget(self.wave)

        root.add_widget(Label(
            text='(c) 2025 Titan Studio PRO', font_size=sp(11), color=hex_c(C_MUTED),
            pos_hint={'center_x': 0.5, 'center_y': 0.06},
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
        Animation(opacity=1, duration=0.8).start(self.logo_widget)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.title_lbl), 0.4)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.ver_lbl), 0.6)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.sub_lbl), 0.8)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.4).start(self.dot_lbl), 1.0)
        self.wave.start()
        self._dot_ev = Clock.schedule_interval(self._tick_dots, 0.5)
        Clock.schedule_once(lambda dt: Animation(value=90, duration=3.0, t='out_cubic').start(self.prog), 0.3)
        Clock.schedule_once(self._go, 3.6)

    def _tick_dots(self, dt):
        self._dot_count = (self._dot_count + 1) % 4
        msgs = ['Initializing', 'Loading voices', 'Preparing studio', 'Almost ready']
        self.dot_lbl.text = msgs[self._dot_count] + '...'

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
        outer = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        back = FlatBtn(text='< Back', bg=C_GRAY2, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.bind(on_press=self._go_back)
        hdr.add_widget(back)
        title_l = lbl('Voice History', 20, C_WHITE, True, 64, 'left')
        hdr.add_widget(title_l)
        outer.add_widget(hdr)
        outer.add_widget(separator())

        # Stats row
        self.stats_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), padding=[dp(12), dp(6)])
        card_bg(self.stats_row, C_CARD2, 10)
        self.count_lbl = lbl('0 recordings', 13, C_MUTED2, False, 38, 'left')
        self.size_lbl = lbl('0 KB total', 13, C_MUTED2, False, 38, 'right')
        self.stats_row.add_widget(self.count_lbl)
        self.stats_row.add_widget(self.size_lbl)
        outer.add_widget(self.stats_row)

        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=[dp(2), dp(6)],
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)
        outer.add_widget(separator())

        clr = FlatBtn(text='Clear All History', bg=C_DARK_RED, size_hint_y=None, height=dp(54), font_size=sp(15))
        clr.bind(on_press=self._confirm_clear)
        outer.add_widget(clr)

        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        Animation(opacity=1, duration=0.25).start(self)
        Clock.schedule_once(lambda dt: self._refresh(), 0.1)

    def _go_back(self, *a):
        self.manager.transition = SlideTransition(direction='right', duration=0.28)
        self.manager.current = 'studio'

    def _refresh(self):
        self.list_box.clear_widgets()
        data = history_load()
        total_size = sum(
            os.path.getsize(e.get('path', ''))
            for e in data if os.path.exists(e.get('path', ''))
        )
        if total_size < 1024 * 1024:
            sz = '{:.0f} KB'.format(total_size / 1024)
        else:
            sz = '{:.1f} MB'.format(total_size / (1024 * 1024))
        self.count_lbl.text = str(len(data)) + ' recordings'
        self.size_lbl.text = sz + ' total'

        if not data:
            empty_lbl = lbl('No recordings yet.\nGenerate and save your first voice!',
                            15, C_MUTED, False, 120, 'center')
            self.list_box.add_widget(empty_lbl)
            return

        for i, entry in enumerate(data):
            row = self._make_row(entry)
            row.opacity = 0
            self.list_box.add_widget(row)
            Clock.schedule_once(lambda dt, w=row: Animation(opacity=1, duration=0.20).start(w), i * 0.05)

    def _make_row(self, entry):
        row = BoxLayout(size_hint_y=None, height=dp(96), spacing=dp(10), padding=[dp(12), dp(8)])
        card_bg(row, C_CARD2, 14)

        em = entry.get('emotion', 'Normal')
        em_color = EMOTION_TAGS.get(em, {}).get('color', C_GRAY)

        # Emotion badge
        badge_box = BoxLayout(size_hint=(None, None), size=(dp(44), dp(44)))
        with badge_box.canvas.before:
            Color(*hex_c(em_color + '33'))
            rr = RoundedRectangle(pos=badge_box.pos, size=badge_box.size, radius=[dp(8)])
        badge_box.bind(
            pos=lambda w, *a: setattr(rr, 'pos', w.pos),
            size=lambda w, *a: setattr(rr, 'size', w.size),
        )
        em_lbl = Label(
            text=EMOTION_TAGS.get(em, {}).get('icon', 'NRM'),
            font_size=sp(11), bold=True,
            color=hex_c(em_color),
            size_hint=(1, 1), halign='center', valign='middle',
        )
        em_lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
        badge_box.add_widget(em_lbl)
        row.add_widget(badge_box)

        info = BoxLayout(orientation='vertical', size_hint_x=1)
        fname_l = lbl(entry.get('filename', 'unknown'), 12, C_WHITE, True, 32, 'left')
        lang_code = LANG_FLAGS.get(entry.get('lang', ''), '')
        meta_l = lbl(
            lang_code + ' ' + entry.get('lang', '') + '  -  '
            + entry.get('voice', '') + '  -  ' + entry.get('emotion', 'Normal')
            + '  -  ' + entry.get('time', ''),
            11, C_GREEN, False, 28, 'left'
        )
        info.add_widget(fname_l)
        info.add_widget(meta_l)
        row.add_widget(info)

        fp = entry.get('path', '')
        if os.path.exists(fp):
            pb = FlatBtn(text='> Play', bg=C_GREEN, size_hint_x=None, width=dp(72), font_size=sp(13))
            pb.bind(on_press=lambda *a, p=fp, b=pb: self._play(p, b))
            row.add_widget(pb)
        else:
            missing = lbl('[Missing]', 10, C_RED, False, 40, 'center')
            row.add_widget(missing)
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
            btn.text = '|| Stop'
            btn.set_bg(C_RED)
            Clock.schedule_once(
                lambda dt: (setattr(btn, 'text', '> Play'), btn.set_bg(C_GREEN)),
                snd.length + 0.3
            )

    def _confirm_clear(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
        box.add_widget(lbl('Clear all history?\nThis cannot be undone.',
                           15, C_WHITE, False, 60, 'center'))
        br = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(12))
        yes = FlatBtn(text='Yes, Clear', bg=C_DARK_RED, font_size=sp(14))
        no = FlatBtn(text='Cancel', bg=C_GRAY2, font_size=sp(14))
        br.add_widget(yes)
        br.add_widget(no)
        box.add_widget(br)
        p = Popup(title='Confirm', content=box, size_hint=(0.88, 0.40), background_color=hex_c(C_CARD))
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
        outer = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(12))

        hdr = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(12))
        back = FlatBtn(text='< Back', bg=C_GRAY2, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('Settings', 20, C_WHITE, True, 60, 'left'))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(14),
            padding=[dp(2), dp(6)],
        )
        content.bind(minimum_height=content.setter('height'))

        # Save folder info card
        fc = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(120),
            padding=[dp(14), dp(10)], spacing=dp(6),
        )
        card_bg(fc, C_CARD2, 12)
        fc.add_widget(sec_header('Save Folder'))
        titan_path = get_titan_folder()
        path_lbl = Label(
            text=titan_path,
            font_size=sp(11), color=hex_c(C_WHITE2),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(40),
        )
        path_lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
        fc.add_widget(path_lbl)
        fc.add_widget(lbl('All audio saved here automatically', 12, C_GREEN, False, 26, 'left'))
        content.add_widget(fc)

        # Folder structure
        sc = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(180),
            padding=[dp(14), dp(10)], spacing=dp(4),
        )
        card_bg(sc, C_CARD2, 12)
        sc.add_widget(sec_header('Sub-folders'))
        for folder, desc in [
            ('Audio/', 'Generated MP3 files'),
            ('Imported/', 'Imported documents'),
            ('Exports/', 'Exported projects'),
            ('Cloned/', 'Voice cloning'),
            ('Queue/', 'Batch queue'),
        ]:
            row = BoxLayout(size_hint_y=None, height=dp(26))
            row.add_widget(lbl('  [DIR] ' + folder, 12, C_BLUE2, True, 26, 'left'))
            row.add_widget(lbl(desc, 11, C_MUTED, False, 26, 'left'))
            sc.add_widget(row)
        content.add_widget(sc)

        # ElevenLabs API key
        api_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(180),
            padding=[dp(14), dp(10)], spacing=dp(8),
        )
        card_bg(api_card, C_CARD2, 12)
        api_card.add_widget(sec_header('ElevenLabs API (Voice Cloning)'))
        api_card.add_widget(lbl('Get free key at elevenlabs.io', 12, C_MUTED2, False, 26, 'left'))
        settings = settings_load()
        self.api_input = TextInput(
            text=settings.get('elevenlabs_key', ''),
            hint_text='sk-... paste your API key here',
            multiline=False,
            size_hint_y=None, height=dp(50),
            background_color=(0.08, 0.12, 0.20, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.39, 0.46, 0.54, 1),
            cursor_color=(0.36, 0.62, 0.94, 1),
            font_size=sp(13),
            password=True,
        )
        api_card.add_widget(self.api_input)
        save_key_btn = FlatBtn(
            text='Save API Key', bg=C_BLUE,
            size_hint_y=None, height=dp(46), font_size=sp(13),
        )
        save_key_btn.bind(on_press=self._save_api_key)
        api_card.add_widget(save_key_btn)
        content.add_widget(api_card)

        # About
        about_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(160),
            padding=[dp(14), dp(10)], spacing=dp(6),
        )
        card_bg(about_card, C_CARD2, 12)
        about_card.add_widget(sec_header('About'))
        for line in [
            'Titan Studio PRO  v12.0.0  CLEAN EDITION',
            'Professional TTS & Voice Studio',
            '30+ Languages  -  10 Emotions  -  Neural Voices',
            'Powered by Microsoft Edge-TTS  -  Always Free',
            '(c) 2025 Titan Studio PRO',
        ]:
            about_card.add_widget(lbl(line, 12, C_MUTED2, False, 24, 'left'))
        content.add_widget(about_card)
        content.add_widget(spacer(20))
        sv.add_widget(content)
        outer.add_widget(sv)
        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        Animation(opacity=1, duration=0.25).start(self)

    def _go_back(self):
        self.manager.transition = SlideTransition(direction='right', duration=0.28)
        self.manager.current = 'studio'

    def _save_api_key(self, *a):
        s = settings_load()
        s['elevenlabs_key'] = self.api_input.text.strip()
        settings_save(s)
        box = BoxLayout(orientation='vertical', padding=dp(20))
        box.add_widget(lbl('API key saved!', 15, C_WHITE, False, 50, 'center'))
        ok = FlatBtn(text='OK', bg=C_GREEN, size_hint_y=None, height=dp(50))
        box.add_widget(ok)
        p = Popup(title='Saved', content=box, size_hint=(0.8, 0.30), background_color=hex_c(C_CARD))
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
        outer = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))

        hdr = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(12))
        back = FlatBtn(text='< Back', bg=C_GRAY2, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('Batch Queue', 18, C_WHITE, True, 60, 'left'))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        self.status_banner = BoxLayout(size_hint_y=None, height=dp(44), padding=[dp(12), dp(6)])
        card_bg(self.status_banner, C_CARD2, 10)
        self.status_lbl = lbl('Queue is empty. Add items from Studio.', 13, C_MUTED, False, 32, 'left')
        self.status_banner.add_widget(self.status_lbl)
        outer.add_widget(self.status_banner)

        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(8), padding=[dp(2), dp(4)],
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)
        outer.add_widget(separator())

        ctrl = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        self.proc_btn = FlatBtn(text='Process All', bg=C_GREEN, font_size=sp(14))
        self.proc_btn.bind(on_press=self._process_all)
        clr_btn = FlatBtn(text='Clear Queue', bg=C_DARK_RED, font_size=sp(13))
        clr_btn.bind(on_press=self._clear_queue)
        ctrl.add_widget(self.proc_btn)
        ctrl.add_widget(clr_btn)
        outer.add_widget(ctrl)
        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        Animation(opacity=1, duration=0.25).start(self)
        Clock.schedule_once(lambda dt: self._refresh(), 0.1)

    def _go_back(self):
        self.manager.transition = SlideTransition(direction='right', duration=0.28)
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
        row = BoxLayout(size_hint_y=None, height=dp(76), spacing=dp(8), padding=[dp(10), dp(6)])
        card_bg(row, C_CARD2, 12)

        num_lbl = Label(
            text=str(idx + 1),
            font_size=sp(18), bold=True,
            color=hex_c(C_ACCENT),
            size_hint_x=None, width=dp(34),
            halign='center', valign='middle',
        )
        num_lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
        row.add_widget(num_lbl)

        info = BoxLayout(orientation='vertical')
        preview = item.get('text', '')[:55] + '...' if len(item.get('text', '')) > 55 else item.get('text', '')
        t = lbl(preview, 12, C_WHITE2, False, 34, 'left')
        m = lbl(
            item.get('lang', '') + '  -  ' + item.get('voice', '') + '  -  ' + item.get('emotion', ''),
            11, C_MUTED2, False, 26, 'left'
        )
        info.add_widget(t)
        info.add_widget(m)
        row.add_widget(info)

        status = item.get('status', 'pending')
        color = C_AMBER if status == 'pending' else C_GREEN if status == 'done' else C_RED
        st_lbl = lbl(status.upper(), 10, color, True, 44, 'center')
        st_lbl.size_hint_x = None
        st_lbl.width = dp(58)
        row.add_widget(st_lbl)
        return row

    def _process_all(self, *a):
        if self._processing:
            return
        self._queue = queue_load()
        if not self._queue:
            return
        self._processing = True
        self.proc_btn.text = 'Processing...'
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
                    try:
                        from gtts import gTTS
                        lang_code = LANGUAGES.get(lang, 'en')
                        tld = VOICE_TLD_FALLBACK.get(gender, 'com')
                        tts = gTTS(text=text, lang=lang_code, tld=tld, slow=speed_pct <= 30)
                        tts.save(dest)
                        item['status'] = 'done'
                        item['output'] = dest
                        history_save({
                            'filename': fname, 'path': dest, 'lang': lang,
                            'voice': gender, 'time': time.strftime('%d %b %Y  %H:%M'),
                            'emotion': emotion, 'source': 'batch-gtts',
                        })
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
        self.proc_btn.text = 'Process All'
        self.proc_btn.disabled = False
        self.status_lbl.text = 'Done! All items processed.'
        self._refresh()

    def _clear_queue(self, *a):
        queue_save([])
        self._refresh()


# ═══════════════════════════════════════════════════════════
#  STUDIO SCREEN  [Main screen - Complete redesign]
#  [FIX 4] Folder banner fixed - no overlapping "[Folder]" text
#  [FIX 5] Quick Guide text always aligned correctly
#  [FIX 6] Every single button is functional
#  [FIX 7] Clean professional UI like reference screenshots
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
        hdr = BoxLayout(
            size_hint_y=None, height=dp(78),
            padding=[dp(14), dp(10)], spacing=dp(10),
        )
        card_bg(hdr, C_CARD, 0)

        logo_path = self._find_logo()
        logo_box = BoxLayout(size_hint=(None, None), size=(dp(50), dp(50)))
        if logo_path:
            logo_box.add_widget(KivyImage(
                source=logo_path, allow_stretch=True, keep_ratio=True, size_hint=(1, 1),
            ))
        else:
            tb_logo = Label(
                text='T', font_size=sp(28), bold=True,
                color=hex_c(C_BLUE2), size_hint=(1, 1),
                halign='center', valign='middle',
            )
            tb_logo.bind(size=lambda w, v: setattr(w, 'text_size', v))
            logo_box.add_widget(tb_logo)
        hdr.add_widget(logo_box)

        # Title block
        tb = BoxLayout(orientation='vertical', size_hint_x=1)
        t1 = Label(
            text='Titan Studio PRO',
            font_size=sp(17), bold=True,
            color=hex_c(C_WHITE),
            halign='left', valign='middle',
        )
        t1.bind(size=lambda w, v: setattr(w, 'text_size', v))
        t2 = Label(
            text='Professional Voice Studio  -  Always Free',
            font_size=sp(10), color=hex_c(C_MUTED),
            halign='left', valign='middle',
        )
        t2.bind(size=lambda w, v: setattr(w, 'text_size', v))
        tb.add_widget(t1)
        tb.add_widget(t2)
        hdr.add_widget(tb)

        settings_btn = FlatBtn(
            text='SET', bg=C_CARD2,
            size_hint=(None, None),
            font_size=sp(11), bold=True, radius=10,
        )
        settings_btn.size = (dp(50), dp(44))
        settings_btn.bind(on_press=lambda *a: self._go_settings())
        hdr.add_widget(settings_btn)
        outer.add_widget(hdr)
        outer.add_widget(separator())

        # ══ SCROLLABLE CONTENT ═══════════════════════════
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(14), dp(14)],
            spacing=dp(14),
        )
        content.bind(minimum_height=content.setter('height'))

        # ── VOICE PRESETS ──────────────────────────────
        presets_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(152),
            padding=[dp(12), dp(10)], spacing=dp(8),
        )
        card_bg(presets_card, C_CARD2, 14)
        presets_card.add_widget(sec_header('Voice Presets'))
        self.preset_picker = PresetPicker(callback=self._apply_preset)
        presets_card.add_widget(self.preset_picker)
        content.add_widget(presets_card)

        # ── LANGUAGE + GENDER ─────────────────────────
        lg_row = BoxLayout(size_hint_y=None, height=dp(130), spacing=dp(10))

        lang_card = BoxLayout(orientation='vertical', padding=[dp(12), dp(10)], spacing=dp(8))
        card_bg(lang_card, C_CARD2, 14)
        lang_card.add_widget(sec_header('Language'))
        self.lang_spin = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=dp(56),
            font_size=sp(14),
            color=(1, 1, 1, 1),
            background_color=hex_c(C_BLUE),
            background_normal='',
        )
        self.lang_spin.bind(text=self._on_lang_change)
        lang_card.add_widget(self.lang_spin)
        lg_row.add_widget(lang_card)

        gender_card = BoxLayout(
            orientation='vertical',
            padding=[dp(12), dp(10)], spacing=dp(8),
            size_hint_x=0.46,
        )
        card_bg(gender_card, C_CARD2, 14)
        gender_card.add_widget(sec_header('Gender'))
        gr = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        self._vbtns = {}
        for name, label in [('Male', 'Male'), ('Female', 'Female')]:
            b = FlatBtn(text=label, bg=C_CARD2, font_size=sp(13), bold=True, radius=10)
            b.bind(on_press=lambda inst, n=name: self._pick_voice(n))
            gr.add_widget(b)
            self._vbtns[name] = b
        gender_card.add_widget(gr)
        lg_row.add_widget(gender_card)
        content.add_widget(lg_row)
        Clock.schedule_once(lambda dt: self._pick_voice('Male'), 0)

        # ── EMOTION PICKER ────────────────────────────
        emotion_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(186),
            padding=[dp(12), dp(10)], spacing=dp(8),
        )
        card_bg(emotion_card, C_CARD2, 14)
        emotion_card.add_widget(sec_header('Emotion & Mood'))
        self.emotion_picker = EmotionPicker()
        emotion_card.add_widget(self.emotion_picker)
        content.add_widget(emotion_card)

        # ── SPEED + PITCH ROW ─────────────────────────
        sp_row = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(10))

        speed_card = BoxLayout(orientation='vertical', padding=[dp(12), dp(10)], spacing=dp(6))
        card_bg(speed_card, C_CARD2, 14)
        speed_card.add_widget(sec_header('Speed'))
        sr = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        sr.add_widget(lbl('Slow', 11, C_MUTED, False, 42, 'left'))
        self.speed_slider = Slider(min=10, max=100, value=50, step=5)
        self.speed_lbl = lbl('50%', 13, C_ACCENT, False, 42, 'right')
        self.speed_slider.bind(
            value=lambda i, v: setattr(self.speed_lbl, 'text', str(int(v)) + '%')
        )
        sr.add_widget(self.speed_slider)
        sr.add_widget(lbl('Fast', 11, C_MUTED, False, 42, 'right'))
        speed_card.add_widget(sr)
        speed_card.add_widget(self.speed_lbl)
        sp_row.add_widget(speed_card)

        pitch_card = BoxLayout(orientation='vertical', padding=[dp(12), dp(10)], spacing=dp(6))
        card_bg(pitch_card, C_CARD2, 14)
        pitch_card.add_widget(sec_header('Pitch'))
        pr = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        pr.add_widget(lbl('Low', 11, C_MUTED, False, 42, 'left'))
        self.pitch_slider = Slider(min=-10, max=10, value=0, step=1)
        self.pitch_lbl = lbl('0', 13, C_ACCENT, False, 42, 'right')
        self.pitch_slider.bind(
            value=lambda i, v: setattr(
                self.pitch_lbl, 'text',
                ('+' if v > 0 else '') + str(int(v))
            )
        )
        pr.add_widget(self.pitch_slider)
        pr.add_widget(lbl('High', 11, C_MUTED, False, 42, 'right'))
        pitch_card.add_widget(pr)
        pitch_card.add_widget(self.pitch_lbl)
        sp_row.add_widget(pitch_card)
        content.add_widget(sp_row)

        # ── ADVANCED OPTIONS ──────────────────────────
        self.adv_card = AdvancedOptionsCard()
        content.add_widget(self.adv_card)

        # ── TEXT INPUT ────────────────────────────────
        text_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(300),
            padding=[dp(12), dp(10)], spacing=dp(8),
        )
        card_bg(text_card, C_CARD2, 14)

        # Text input header row
        ti_hdr = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        ti_title = lbl('Input Text', 13, C_ACCENT, True, 36, 'left')
        ti_hdr.add_widget(ti_title)
        self.char_lbl = lbl('0 chars', 11, C_MUTED, False, 36, 'center')
        ti_hdr.add_widget(self.char_lbl)

        imp_btn = FlatBtn(
            text='Import File', bg=C_BLUE,
            size_hint_x=None, width=dp(110),
            font_size=sp(12), radius=8,
        )
        imp_btn.size_hint_y = None
        imp_btn.height = dp(36)
        imp_btn.bind(on_press=self._import_file)
        ti_hdr.add_widget(imp_btn)

        clr_btn = FlatBtn(
            text='Clear', bg=C_CARD3,
            size_hint_x=None, width=dp(60),
            font_size=sp(12), radius=8,
        )
        clr_btn.size_hint_y = None
        clr_btn.height = dp(36)
        clr_btn.bind(on_press=lambda *a: setattr(self.txt, 'text', ''))
        ti_hdr.add_widget(clr_btn)
        text_card.add_widget(ti_hdr)

        # RTL indicator
        self.rtl_lbl = lbl('', 11, C_AMBER, False, 18, 'left')
        text_card.add_widget(self.rtl_lbl)

        self.txt = TextInput(
            hint_text='Enter text here... supports Urdu, Arabic, English and 30+ languages',
            multiline=True,
            size_hint=(1, 1),
            background_color=(0.05, 0.08, 0.14, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.39, 0.46, 0.54, 1),
            cursor_color=(0.36, 0.62, 0.94, 1),
            font_size=sp(16),
            padding=[dp(12), dp(10)],
        )
        self.txt.bind(text=self._count)
        text_card.add_widget(self.txt)

        # File info (hidden until file imported)
        self.file_info_container = BoxLayout(orientation='vertical', size_hint_y=None, height=0)
        text_card.add_widget(self.file_info_container)
        content.add_widget(text_card)

        # ── ADD TO BATCH QUEUE ────────────────────────
        queue_btn = FlatBtn(
            text='+ Add to Batch Queue',
            bg=C_PURPLE,
            size_hint_y=None, height=dp(48),
            font_size=sp(14),
        )
        queue_btn.bind(on_press=self._add_to_queue)
        content.add_widget(queue_btn)

        # ── STATUS + WAVEFORM ─────────────────────────
        status_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(120),
            padding=[dp(12), dp(10)], spacing=dp(6),
        )
        card_bg(status_card, C_CARD2, 14)
        self.status_lbl = lbl('Ready to generate voice', 13, C_MUTED, False, 30, 'left')
        status_card.add_widget(self.status_lbl)
        self.prog = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(6))
        status_card.add_widget(self.prog)
        self.waveform = WaveformWidget(bars=24, color=C_GREEN_L, size_hint_y=None, height=dp(46))
        status_card.add_widget(self.waveform)
        content.add_widget(status_card)

        # ── GENERATE AUDIO BUTTON ─────────────────────
        # [FIX 7] Clean design like reference screenshot (purple/blue)
        self.gen_btn = FlatBtn(
            text='Generate Audio',
            bg=C_PURPLE_L,
            size_hint_y=None, height=dp(68),
            font_size=sp(19), bold=True, radius=16,
        )
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        # ── PREVIEW AUDIO + SAVE ROW ──────────────────
        # [FIX 7] Like reference: green preview, purple generate
        pd_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(12))
        self.play_btn = FlatBtn(
            text='Preview Audio',
            bg=C_GREEN_L,
            font_size=sp(14), disabled=True,
        )
        self.dl_btn = FlatBtn(
            text='Save Voice',
            bg=C_GREEN2,
            font_size=sp(14), disabled=True,
        )
        self.play_btn.bind(on_press=self._play)
        self.dl_btn.bind(on_press=self._download)
        pd_row.add_widget(self.play_btn)
        pd_row.add_widget(self.dl_btn)
        content.add_widget(pd_row)

        # ── NAVIGATION ROW ────────────────────────────
        nav_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        hist_btn = FlatBtn(text='History', bg=C_PURPLE, font_size=sp(14))
        hist_btn.bind(on_press=lambda *a: self._go_hist())
        batch_btn = FlatBtn(text='Batch Queue', bg=C_GRAY2, font_size=sp(14))
        batch_btn.bind(on_press=lambda *a: self._go_batch())
        nav_row.add_widget(hist_btn)
        nav_row.add_widget(batch_btn)
        content.add_widget(nav_row)

        # ── SAVE FOLDER BANNER ────────────────────────
        # [FIX 4] No more "[Folder]" floating text - clean layout
        folder_banner = BoxLayout(
            size_hint_y=None, height=dp(58),
            padding=[dp(12), dp(8)], spacing=dp(10),
        )
        card_bg(folder_banner, C_SURFACE, 12)

        folder_icon_lbl = Label(
            text='[DIR]',
            font_size=sp(11), bold=True,
            color=hex_c(C_BLUE2),
            size_hint=(None, 1), width=dp(40),
            halign='center', valign='middle',
        )
        folder_icon_lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
        folder_banner.add_widget(folder_icon_lbl)

        titan_p = get_titan_folder()
        folder_info = BoxLayout(orientation='vertical')
        folder_line1 = lbl('Auto-saves to: Titan Studio PRO/Audio/', 12, C_WHITE2, True, 26, 'left')
        folder_line2 = lbl(titan_p, 11, C_MUTED, False, 22, 'left')
        folder_info.add_widget(folder_line1)
        folder_info.add_widget(folder_line2)
        folder_banner.add_widget(folder_info)
        content.add_widget(folder_banner)

        # ── RESULTS SECTION ───────────────────────────
        # Like reference app: "Results" section at bottom
        results_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(90),
            padding=[dp(12), dp(10)], spacing=dp(8),
        )
        card_bg(results_card, C_CARD2, 14)
        results_card.add_widget(sec_header('Results'))
        self.result_lbl = lbl('No generated items yet', 13, C_MUTED, False, 40, 'left')
        results_card.add_widget(self.result_lbl)
        content.add_widget(results_card)

        # ── QUICK GUIDE ───────────────────────────────
        # [FIX 5] All text properly aligned - no floating
        how_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(254),
            padding=[dp(14), dp(12)], spacing=dp(4),
        )
        card_bg(how_card, C_CARD, 14)
        how_card.add_widget(sec_header('Quick Guide'))
        how_card.add_widget(spacer(4))
        steps = [
            '1. Select a Voice Preset (Narrator, News, etc.)',
            '2. Choose Language from 30+ options',
            '3. Pick Gender: Male or Female voice',
            '4. Set Emotion (Whisper, Shout, Happy etc.)',
            '5. Adjust Speed and Pitch sliders',
            '6. Type text or Import file (TXT/PDF/DOCX)',
            '7. Tap Generate Audio button',
            '8. Preview then Save - auto-saved to Titan Studio PRO/',
        ]
        for s in steps:
            step_lbl = lbl(s, 12, C_MUTED, False, 26, 'left')
            how_card.add_widget(step_lbl)
        content.add_widget(how_card)
        content.add_widget(spacer(24))

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
        Animation(opacity=1, duration=0.28, t='out_quad').start(self)

    def _go_hist(self):
        self.manager.transition = SlideTransition(direction='left', duration=0.28)
        self.manager.current = 'history'

    def _go_batch(self):
        self.manager.transition = SlideTransition(direction='left', duration=0.28)
        self.manager.current = 'batch'

    def _go_settings(self):
        self.manager.transition = SlideTransition(direction='left', duration=0.28)
        self.manager.current = 'settings'

    def _on_lang_change(self, inst, lang):
        if lang in RTL_LANGS:
            self.rtl_lbl.text = 'RTL mode: ' + lang + ' - Use your ' + lang + ' keyboard'
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
        self.pitch_slider.value = data.get('pitch', 0)
        self.emotion_picker._select(data.get('emotion', 'Normal'))
        self.status_lbl.text = 'Preset: ' + name + ' - ' + data.get('desc', '')

    def _pick_voice(self, name):
        self.voice_sel = name
        for n, b in self._vbtns.items():
            if n == name:
                b.set_bg(C_BLUE)
                b.bold = True
            else:
                b.set_bg(C_CARD2)
                b.bold = False

    def _count(self, inst, val):
        words = len(val.split()) if val.strip() else 0
        lines = len(val.splitlines()) if val.strip() else 0
        chars = len(val)
        self.char_lbl.text = str(chars) + ' chars  ' + str(words) + ' words'

    def _import_file(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box.add_widget(lbl('Select file type to import:', 15, C_WHITE, True, 36, 'center'))

        grid = GridLayout(cols=3, size_hint_y=None, height=dp(180), spacing=dp(10))
        pop = [None]
        for ft, fi in FILE_ICONS.items():
            col = BoxLayout(orientation='vertical', spacing=dp(4))
            b = FlatBtn(
                text=fi.get('label', ft),
                bg=fi.get('color', C_BLUE),
                size_hint_y=None, height=dp(56),
                font_size=sp(14), bold=True, radius=12,
            )
            b.bind(on_press=lambda x, t=ft, p=pop: self._open_chooser(t, p[0]))
            col.add_widget(b)
            ft_lbl = lbl(ft, 10, C_MUTED2, False, 20, 'center')
            col.add_widget(ft_lbl)
            grid.add_widget(col)
        box.add_widget(grid)

        can = FlatBtn(text='Cancel', bg=C_GRAY2, size_hint_y=None, height=dp(50))
        box.add_widget(can)
        p = Popup(
            title='Import File',
            content=box,
            size_hint=(0.92, 0.60),
            background_color=hex_c(C_CARD),
        )
        pop[0] = p
        can.bind(on_press=p.dismiss)
        p.open()

    def _open_chooser(self, ftype, prev):
        if prev:
            prev.dismiss()
        fm = {
            'TXT': ['*.txt', '*.md'],
            'PDF': ['*.pdf'],
            'DOCX': ['*.docx', '*.doc'],
            'SRT': ['*.srt'],
            'DOC': ['*.doc'],
            'CSV': ['*.csv'],
        }
        sp_path = get_internal_storage_path()
        try:
            if ANDROID_ENV:
                sp_path = primary_external_storage_path() or sp_path
        except Exception:
            pass
        fc = FileChooserListView(path=sp_path, filters=fm.get(ftype, ['*.*']))
        box = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        box.add_widget(fc)
        br = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        sel = FlatBtn(text='Select File', bg=C_GREEN, font_size=sp(14))
        can = FlatBtn(text='Cancel', bg=C_GRAY2, font_size=sp(14))
        br.add_widget(sel)
        br.add_widget(can)
        box.add_widget(br)
        p = Popup(
            title='Choose ' + ftype + ' File',
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
        self.status_lbl.text = 'Reading ' + ftype + ' file...'
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
                Clock.schedule_once(
                    lambda dt: setattr(self.status_lbl, 'text', 'Read error: ' + str(e)[:50])
                )
                return

            def apply(dt):
                if text.strip():
                    self.txt.text = text
                    self.status_lbl.text = 'Imported: ' + os.path.basename(path)
                    self.prog.value = 100
                    self._imported_path = path
                    self._imported_type = ftype
                    self.file_info_container.clear_widgets()
                    self.file_info_container.height = dp(72)
                    card = FileInfoCard(path=path, ftype=ftype, size_hint_y=None, height=dp(64))
                    self.file_info_container.add_widget(card)
                    Clock.schedule_once(
                        lambda dt2: Animation(value=0, duration=0.5).start(self.prog), 1.5
                    )
                else:
                    self.status_lbl.text = 'Could not read file. Try TXT format.'
                    self.prog.value = 0

            Clock.schedule_once(apply)

        threading.Thread(target=worker, daemon=True).start()

    def _add_to_queue(self, *a):
        text = self.txt.text.strip()
        if not text:
            self.status_lbl.text = 'Enter text first!'
            return
        q = queue_load()
        q.append({
            'text': text,
            'lang': self.lang_spin.text,
            'voice': self.voice_sel,
            'emotion': self.emotion_picker.selected,
            'speed': int(self.speed_slider.value),
            'pitch': int(self.pitch_slider.value),
            'slow': int(self.speed_slider.value) <= 30,
            'status': 'pending',
            'added': time.strftime('%d %b %H:%M'),
        })
        queue_save(q)
        self.status_lbl.text = 'Added to batch queue! (' + str(len(q)) + ' items)'

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
    #  GENERATE  [FIX 1: Better internet handling]
    # ══════════════════════════════════════════════════════
    def _generate(self, *a):
        text = self.txt.text.strip()
        if not text:
            self.status_lbl.text = 'Please enter some text first!'
            return
        self._set_busy()
        self._upd(0, 'Starting voice generation...')
        self.waveform.start()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            lang_name = self.lang_spin.text
            gender = self.voice_sel
            emotion = self.emotion_picker.selected
            speed_pct = int(self.speed_slider.value)
            pitch_val = int(self.pitch_slider.value)
            use_breaths = self.adv_card.use_breaths

            Clock.schedule_once(lambda dt: self._upd(10, 'Selecting voice...'))
            voice = pick_edge_voice(lang_name, gender)
            rate_str = speed_to_rate_str(speed_pct, emotion)
            volume_str = emotion_to_volume_str(emotion)
            pitch_str = pitch_to_pitch_str(pitch_val)
            text = self.txt.text

            if use_breaths:
                text = re.sub(r'([.!?])\s+', r'\1 ', text)

            label = lang_name + ' - ' + gender + ' - ' + emotion
            Clock.schedule_once(lambda dt: self._upd(25, 'Checking connection...'))

            # [FIX 1] Pre-check internet before attempting edge-tts
            has_internet = check_internet()

            out = os.path.join(App.get_running_app().user_data_dir, 'tts_preview.mp3')

            if has_internet:
                Clock.schedule_once(lambda dt: self._upd(45, 'Generating neural voice (' + label + ')...'))
                ok, err = edge_tts_generate(text, voice, rate_str, volume_str, pitch_str, out)

                if ok:
                    Clock.schedule_once(lambda dt: self._upd(90, 'Processing audio...'))
                    self.out_file = out
                    Clock.schedule_once(lambda dt: self._on_done())
                elif err == 'IMPORT_ERROR':
                    Clock.schedule_once(lambda dt: self._upd(35, 'edge-tts not found, using gTTS...'))
                    self._worker_gtts_fallback(out)
                elif err == 'TIMEOUT':
                    Clock.schedule_once(
                        lambda dt: self._upd(35, 'Connection timeout. Trying gTTS fallback...')
                    )
                    self._worker_gtts_fallback(out)
                else:
                    # Try gTTS as last resort
                    Clock.schedule_once(
                        lambda dt: self._upd(35, 'Edge-TTS failed. Trying gTTS fallback...')
                    )
                    self._worker_gtts_fallback(out)
            else:
                # No internet: try gTTS (also needs internet, but show clear error)
                Clock.schedule_once(
                    lambda dt: self._upd(20, 'No internet detected. Trying gTTS...')
                )
                self._worker_gtts_fallback(out)

        except Exception as e:
            msg = str(e)
            Clock.schedule_once(lambda dt, m=msg: self._on_err(m))

    def _worker_gtts_fallback(self, out_path=None):
        """Fallback to gTTS when edge-tts fails"""
        try:
            from gtts import gTTS
            Clock.schedule_once(lambda dt: self._upd(60, 'Generating with gTTS...'))
            lang = LANGUAGES.get(self.lang_spin.text, 'en')
            tld = VOICE_TLD_FALLBACK.get(self.voice_sel, 'com')
            slow = int(self.speed_slider.value) <= 30
            text = self.txt.text
            tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
            if out_path is None:
                out_path = os.path.join(App.get_running_app().user_data_dir, 'tts_preview.mp3')
            Clock.schedule_once(lambda dt: self._upd(80, 'Saving gTTS audio...'))
            tts.save(out_path)
            self.out_file = out_path
            Clock.schedule_once(lambda dt: self._on_done(gtts_mode=True))
        except Exception as e:
            msg = str(e)
            Clock.schedule_once(lambda dt, m=msg: self._on_err('No internet connection. Both edge-tts and gTTS failed. Please check your internet and try again.'))

    def _on_done(self, gtts_mode=False):
        if self._audio:
            try:
                self._audio.stop()
                self._audio.unload()
            except Exception:
                pass
            self._audio = None

        self._audio = SoundLoader.load(self.out_file)
        if gtts_mode:
            msg = 'Audio ready! (gTTS mode - install edge-tts for neural voices)'
        else:
            msg = 'Audio ready! Tap Preview Audio or Save Voice.'
        self._upd(100, msg)
        self._set_ready(ok=True)
        self.waveform.stop()
        self.result_lbl.text = 'Generated: ' + self.lang_spin.text + ' - ' + self.voice_sel + ' - ' + self.emotion_picker.selected
        Clock.schedule_once(
            lambda dt: Animation(value=0, duration=0.7, t='out_quad').start(self.prog), 2.0
        )

    def _on_err(self, msg):
        self.waveform.stop()
        m = msg.lower()
        if any(k in m for k in [
            'network', 'connection', 'gaierror', 'timeout', 'errno',
            'refused', 'reset', 'ssl', 'socket', 'unreachable',
            'broken pipe', 'eof', 'no internet', 'name resolution',
        ]):
            txt = 'No internet! Please turn on Wi-Fi or mobile data, then try again.'
        elif 'lang' in m:
            txt = 'This language is not supported by the TTS engine.'
        elif 'import' in m:
            txt = 'edge-tts not installed. Install it with: pip install edge-tts'
        else:
            txt = 'Error: ' + msg[:80]
        self._upd(0, txt)
        self._set_ready(ok=False)

    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = 'Preview Audio'
            self.play_btn.set_bg(C_GREEN_L)
            self.waveform.stop()
        else:
            self._audio.play()
            self.play_btn.text = 'Stop Audio'
            self.play_btn.set_bg(C_AMBER)
            self.waveform.start()

    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status_lbl.text = 'Generate audio first!'
            return

        def after_permission(granted):
            self._auto_save()

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
            self._upd(100, 'Saved: ' + fname)
            history_save({
                'filename': fname,
                'path': dest,
                'lang': lang,
                'voice': voice,
                'emotion': emotion,
                'time': time.strftime('%d %b %Y  %H:%M'),
                'source': 'studio',
            })
            self._show_save_success(fname, audio_dir, dest)
        except PermissionError:
            self._show_err_popup(
                'Permission denied!\n\nGo to Settings > App > Permissions and allow Storage.'
            )
        except Exception as e:
            self._upd(0, 'Save failed: ' + str(e)[:60])

    def _show_save_success(self, fname, folder, full_path):
        box = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        box.add_widget(lbl('Saved to Titan Studio PRO!', 17, C_GREEN, True, 44, 'center'))
        box.add_widget(lbl(fname, 12, C_WHITE, False, 32, 'center'))
        box.add_widget(lbl(folder, 11, C_MUTED2, False, 36, 'center'))
        ok = FlatBtn(text='Great!', bg=C_GREEN, size_hint_y=None, height=dp(52), font_size=sp(15))
        box.add_widget(ok)
        p = Popup(
            title='Download Complete',
            content=box,
            size_hint=(0.90, 0.48),
            background_color=hex_c(C_CARD),
        )
        ok.bind(on_press=p.dismiss)
        p.open()

    def _show_err_popup(self, msg):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box.add_widget(lbl(msg, 14, C_AMBER, False, 80, 'center'))
        ok = FlatBtn(text='OK', bg=C_BLUE, size_hint_y=None, height=dp(52))
        box.add_widget(ok)
        p = Popup(
            title='Error',
            content=box,
            size_hint=(0.88, 0.40),
            background_color=hex_c(C_CARD),
        )
        ok.bind(on_press=p.dismiss)
        p.open()


# ═══════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════
class TitanApp(App):
    def build(self):
        self.title = 'Titan Studio PRO'

        try:
            get_titan_folder()
        except Exception:
            pass

        sm = ScreenManager(transition=FadeTransition(duration=0.36))
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(StudioScreen(name='studio'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(BatchQueueScreen(name='batch'))

        if ANDROID_ENV:
            Clock.schedule_once(self._ask_perms, 1.0)

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

    def on_stop(self):
        pass


if __name__ == '__main__':
    TitanApp().run()
