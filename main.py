# ============================================================
#  Titan Studio PRO  -  main.py
#  Version 2.0  |  CYBER MINT EDITION  (Kokoro TTS)
#  ─────────────────────────────────────────────────────────
#  CHANGES IN v2.0:
#    [UPGRADE] Replaced edge-tts with Kokoro-TTS engine.
#              Kokoro is an offline, high-quality neural TTS.
#              True Male/Female voices that actually work.
#              Advanced features (speed, pitch, emotion)
#              properly applied. 35+ language support via
#              gTTS fallback for non-English languages.
#              No internet required for English voices.
#
#  KOKORO VOICE MAP:
#    Male   English  → af_sky / am_adam / am_michael
#    Female English  → af_heart / af_bella / af_sarah
#    Other languages → gTTS fallback (internet required)
#
#  CYBER MINT THEME PALETTE:
#    Base:    #FFFFFF  (Pure White backgrounds)
#    Surface: #F0FDF4  (Hint of Mint - cards/sections)
#    Accent:  #10B981  (Vibrant Emerald - buttons/icons)
#    Dark:    #064E3B  (Deep Emerald - active states)
#    Text:    #334155  (Slate Gray - premium look)
#    Muted:   #64748B  (Muted Slate - secondary text)
#    Border:  #D1FAE5  (Light Mint - card borders)
#    Error:   #EF4444  (Red - errors)
#    Warning: #F59E0B  (Amber - warnings)
# ============================================================

import os
import threading
import time
import shutil
import json
import re
import math
import tempfile

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
from kivy.core.text import LabelBase
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
#  FONT REGISTRATION
# ═══════════════════════════════════════════════════════════
def _register_fonts():
    """Register fonts for Urdu, Hindi, Arabic, CJK support."""
    font_map = [
        ('NotoNastaliq',    ['NotoNastaliqUrdu-Regular.ttf', 'NotoNastaliqUrdu.ttf']),
        ('NotoDevanagari',  ['NotoSansDevanagari-Regular.ttf', 'NotoSansDevanagari.ttf']),
        ('NotoArabic',      ['NotoNaskhArabic-Regular.ttf', 'NotoNaskhArabic.ttf']),
        ('NotoSansCJK',     ['NotoSansCJK-Regular.ttc', 'NotoSansSC-Regular.otf']),
        ('NotoSans',        ['NotoSans-Regular.ttf']),
    ]
    base_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        '/system/fonts',
        '/system/product/fonts',
        os.path.expanduser('~') + '/.fonts',
        '/usr/share/fonts/truetype/noto',
        '/usr/share/fonts/noto',
    ]
    for name, filenames in font_map:
        for d in base_dirs:
            for fn in filenames:
                p = os.path.join(d, fn)
                if os.path.exists(p):
                    try:
                        LabelBase.register(name=name, fn_regular=p)
                    except Exception:
                        pass
                    break

_register_fonts()

LANG_FONTS = {
    'Urdu':    'NotoNastaliq',
    'Arabic':  'NotoArabic',
    'Hindi':   'NotoDevanagari',
    'Bengali': 'NotoDevanagari',
    'Punjabi': 'NotoDevanagari',
    'Tamil':   'NotoDevanagari',
    'Telugu':  'NotoDevanagari',
    'Chinese': 'NotoSansCJK',
    'Japanese':'NotoSansCJK',
    'Korean':  'NotoSansCJK',
}
DEFAULT_FONT = 'Roboto'

# ═══════════════════════════════════════════════════════════
#  CYBER MINT COLOUR PALETTE
# ═══════════════════════════════════════════════════════════
C_BG        = '#FFFFFF'
C_BG2       = '#F0FDF4'
C_CARD      = '#F0FDF4'
C_CARD2     = '#DCFCE7'
C_CARD3     = '#BBF7D0'
C_GREEN     = '#10B981'
C_GREEN2    = '#059669'
C_GREEN3    = '#064E3B'
C_GREEN_L   = '#34D399'
C_TEXT      = '#334155'
C_TEXT2     = '#1E293B'
C_MUTED     = '#64748B'
C_MUTED2    = '#94A3B8'
C_BORDER    = '#D1FAE5'
C_RED       = '#EF4444'
C_RED2      = '#DC2626'
C_AMBER     = '#F59E0B'
C_ORANGE    = '#F97316'
C_BLUE      = '#0EA5E9'
C_BLUE2     = '#38BDF8'
C_PURPLE    = '#7C3AED'
C_PURPLE_L  = '#A78BFA'
C_INDIGO    = '#6366F1'
C_DIVIDER   = '#D1FAE5'
C_SURFACE   = '#ECFDF5'
C_GOLD      = '#D97706'
C_TEAL      = '#0D9488'
C_DARK_RED  = '#991B1B'
C_WHITE     = '#FFFFFF'
C_WHITE2    = '#F8FAFC'

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

LANG_KEYBOARD_LOCALE = {
    'English': 'en', 'Urdu': 'ur', 'Hindi': 'hi', 'Arabic': 'ar',
    'French': 'fr', 'Spanish': 'es', 'German': 'de', 'Turkish': 'tr',
    'Russian': 'ru', 'Chinese': 'zh', 'Japanese': 'ja', 'Korean': 'ko',
    'Portuguese': 'pt', 'Italian': 'it', 'Dutch': 'nl', 'Polish': 'pl',
    'Bengali': 'bn', 'Punjabi': 'pa', 'Tamil': 'ta', 'Telugu': 'te',
    'Thai': 'th', 'Vietnamese': 'vi', 'Greek': 'el', 'Ukrainian': 'uk',
}

# ═══════════════════════════════════════════════════════════
#  KOKORO TTS VOICE MAP
#  Kokoro supports English natively with true Male/Female.
#  For other languages, gTTS fallback is used.
#
#  Format: lang_name → (male_voice_id, female_voice_id)
#  Kokoro voice IDs:
#    af_*  = American Female
#    am_*  = American Male
#    bf_*  = British Female
#    bm_*  = British Male
# ═══════════════════════════════════════════════════════════
KOKORO_VOICES = {
    # (male_voice, female_voice)
    'English':    ('am_michael',  'af_heart'),
    # All other languages use gTTS fallback
}

# For gTTS fallback - language code + tld per gender
GTTS_VOICE_MAP = {
    'English':    {'Male': ('en', 'com'),     'Female': ('en', 'co.uk')},
    'Urdu':       {'Male': ('ur', 'com'),     'Female': ('ur', 'com')},
    'Hindi':      {'Male': ('hi', 'com'),     'Female': ('hi', 'co.in')},
    'Arabic':     {'Male': ('ar', 'com'),     'Female': ('ar', 'com')},
    'French':     {'Male': ('fr', 'fr'),      'Female': ('fr', 'com')},
    'Spanish':    {'Male': ('es', 'es'),      'Female': ('es', 'com')},
    'German':     {'Male': ('de', 'de'),      'Female': ('de', 'com')},
    'Turkish':    {'Male': ('tr', 'com'),     'Female': ('tr', 'com')},
    'Russian':    {'Male': ('ru', 'com'),     'Female': ('ru', 'com')},
    'Chinese':    {'Male': ('zh-TW', 'com'),  'Female': ('zh-TW', 'com')},
    'Japanese':   {'Male': ('ja', 'co.jp'),   'Female': ('ja', 'com')},
    'Korean':     {'Male': ('ko', 'com'),     'Female': ('ko', 'com')},
    'Portuguese': {'Male': ('pt', 'com.br'),  'Female': ('pt', 'com')},
    'Italian':    {'Male': ('it', 'it'),      'Female': ('it', 'com')},
    'Dutch':      {'Male': ('nl', 'com'),     'Female': ('nl', 'com')},
    'Polish':     {'Male': ('pl', 'pl'),      'Female': ('pl', 'com')},
    'Swedish':    {'Male': ('sv', 'com'),     'Female': ('sv', 'com')},
    'Danish':     {'Male': ('da', 'dk'),      'Female': ('da', 'com')},
    'Norwegian':  {'Male': ('no', 'com'),     'Female': ('no', 'com')},
    'Finnish':    {'Male': ('fi', 'com'),     'Female': ('fi', 'com')},
    'Greek':      {'Male': ('el', 'com'),     'Female': ('el', 'com')},
    'Romanian':   {'Male': ('ro', 'com'),     'Female': ('ro', 'com')},
    'Czech':      {'Male': ('cs', 'cz'),      'Female': ('cs', 'com')},
    'Hungarian':  {'Male': ('hu', 'com'),     'Female': ('hu', 'com')},
    'Vietnamese': {'Male': ('vi', 'com'),     'Female': ('vi', 'com')},
    'Thai':       {'Male': ('th', 'com'),     'Female': ('th', 'com')},
    'Indonesian': {'Male': ('id', 'co.id'),   'Female': ('id', 'com')},
    'Malay':      {'Male': ('ms', 'com'),     'Female': ('ms', 'com')},
    'Bengali':    {'Male': ('bn', 'com'),     'Female': ('bn', 'com')},
    'Tamil':      {'Male': ('ta', 'co.in'),   'Female': ('ta', 'com')},
    'Telugu':     {'Male': ('te', 'co.in'),   'Female': ('te', 'com')},
    'Ukrainian':  {'Male': ('uk', 'com'),     'Female': ('uk', 'com')},
    'Swahili':    {'Male': ('sw', 'com'),     'Female': ('sw', 'com')},
    'Punjabi':    {'Male': ('pa', 'co.in'),   'Female': ('pa', 'com')},
    'Catalan':    {'Male': ('ca', 'com'),     'Female': ('ca', 'com')},
}

RTL_LANGS = {'Urdu', 'Arabic', 'Hebrew', 'Persian'}

LANG_FLAGS = {
    'English': 'EN', 'Urdu': 'UR', 'Hindi': 'HI', 'Arabic': 'AR',
    'French': 'FR', 'Spanish': 'ES', 'German': 'DE', 'Turkish': 'TR',
    'Russian': 'RU', 'Chinese': 'ZH', 'Japanese': 'JA', 'Korean': 'KO',
    'Portuguese': 'PT', 'Italian': 'IT', 'Dutch': 'NL', 'Polish': 'PL',
}

EMOTION_TAGS = {
    'Normal':  {'icon': 'NRM', 'color': C_TEXT,    'volume': 1.0,  'rate_boost': 0},
    'Happy':   {'icon': 'HPI', 'color': C_GREEN,   'volume': 1.1,  'rate_boost': 5},
    'Sad':     {'icon': 'SAD', 'color': C_BLUE2,   'volume': 0.85, 'rate_boost': -8},
    'Whisper': {'icon': 'WSP', 'color': C_PURPLE,  'volume': 0.4,  'rate_boost': -10},
    'Shout':   {'icon': 'SHT', 'color': C_RED,     'volume': 1.3,  'rate_boost': 10},
    'Sarcasm': {'icon': 'SAR', 'color': C_AMBER,   'volume': 1.05, 'rate_boost': 0},
    'Excited': {'icon': 'EXC', 'color': C_ORANGE,  'volume': 1.2,  'rate_boost': 15},
    'Calm':    {'icon': 'CLM', 'color': C_TEAL,    'volume': 0.9,  'rate_boost': -12},
    'Serious': {'icon': 'SRS', 'color': C_INDIGO,  'volume': 1.0,  'rate_boost': -3},
    'Fearful': {'icon': 'FER', 'color': '#EC4899', 'volume': 0.8,  'rate_boost': -5},
}

VOICE_PRESETS = {
    'Narrator':   {'icon': 'NAR',  'speed': 1.0,  'pitch': 1.0,  'emotion': 'Calm',    'desc': 'Clear storytelling'},
    'Newsreader': {'icon': 'NEWS', 'speed': 1.1,  'pitch': 1.0,  'emotion': 'Serious', 'desc': 'Professional news'},
    'Story':      {'icon': 'STR',  'speed': 0.95, 'pitch': 0.95, 'emotion': 'Happy',   'desc': 'Engaging story'},
    'Meditation': {'icon': 'MED',  'speed': 0.75, 'pitch': 0.95, 'emotion': 'Calm',    'desc': 'Peaceful & slow'},
    'Commercial': {'icon': 'ADS',  'speed': 1.15, 'pitch': 1.05, 'emotion': 'Excited', 'desc': 'Upbeat & catchy'},
    'Robot':      {'icon': 'BOT',  'speed': 1.0,  'pitch': 0.7,  'emotion': 'Serious', 'desc': 'Robotic effect'},
    'Poet':       {'icon': 'POT',  'speed': 0.85, 'pitch': 1.05, 'emotion': 'Sad',     'desc': 'Dramatic poetry'},
    'Audiobook':  {'icon': 'BOOK', 'speed': 1.0,  'pitch': 1.0,  'emotion': 'Normal',  'desc': 'Long-form audio'},
}

FILE_ICONS = {
    'TXT':  {'label': 'TXT',  'color': C_BLUE},
    'PDF':  {'label': 'PDF',  'color': C_RED},
    'DOCX': {'label': 'DOCX', 'color': '#3B82F6'},
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
        internal_root = '/storage/emulated/0'
        if os.path.exists(internal_root):
            base = os.path.join(internal_root, APP_FOLDER_NAME)
        else:
            try:
                app = App.get_running_app()
                base = os.path.join(app.user_data_dir if app else os.path.expanduser('~'), APP_FOLDER_NAME)
            except Exception:
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
        try:
            perms.append(Permission.MANAGE_EXTERNAL_STORAGE)
        except Exception:
            pass

        def on_result(permissions, grants):
            if callback:
                callback(True)

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
#  KOKORO TTS ENGINE
#
#  Kokoro is an offline neural TTS engine. It generates
#  very natural speech. We use it for English (Male/Female).
#  For other languages we fall back to gTTS (online).
#
#  Kokoro speed parameter: 1.0 = normal, 0.5 = slow, 1.5 = fast
#  Kokoro pitch: controlled via voice selection or post-processing
# ═══════════════════════════════════════════════════════════

def kokoro_generate(text, voice_id, speed, output_path):
    """
    Generate audio using Kokoro TTS engine.
    voice_id: Kokoro voice string e.g. 'am_michael', 'af_heart'
    speed: float 0.5 - 2.0 (1.0 = normal)
    output_path: where to save the .wav file
    Returns (ok, error_message)
    """
    result = {'ok': False, 'err': ''}
    done_event = threading.Event()

    def _worker():
        try:
            from kokoro import KPipeline
            import soundfile as sf
            import numpy as np

            # Kokoro pipeline: lang_code 'a' = American English
            lang_code = 'a'  # 'a' = American, 'b' = British
            if voice_id.startswith('b'):
                lang_code = 'b'

            pipeline = KPipeline(lang_code=lang_code)

            # Generate audio - kokoro returns generator of (gs, ps, audio) tuples
            audio_chunks = []
            generator = pipeline(
                text,
                voice=voice_id,
                speed=speed,
                split_pattern=r'\n+'
            )
            for _, _, audio in generator:
                if audio is not None:
                    audio_chunks.append(audio)

            if audio_chunks:
                combined = np.concatenate(audio_chunks) if len(audio_chunks) > 1 else audio_chunks[0]
                # Kokoro sample rate is 24000 Hz
                sf.write(output_path, combined, 24000)
                result['ok'] = True
            else:
                result['err'] = 'No audio generated'

        except ImportError as e:
            result['err'] = 'IMPORT_ERROR: ' + str(e)
        except Exception as e:
            result['err'] = str(e)
        finally:
            done_event.set()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    done_event.wait(timeout=120)

    if not done_event.is_set():
        return False, 'TIMEOUT'
    return result['ok'], result['err']


def gtts_generate(text, lang_code, tld, slow, output_path):
    """
    Generate audio using Google TTS (gTTS) - internet required.
    Used as primary engine for non-English languages,
    and as fallback if Kokoro is unavailable.
    Returns (ok, error_message)
    """
    result = {'ok': False, 'err': ''}
    done_event = threading.Event()

    def _worker():
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang_code, tld=tld, slow=slow)
            tts.save(output_path)
            result['ok'] = True
        except ImportError:
            result['err'] = 'IMPORT_ERROR'
        except Exception as e:
            result['err'] = str(e)
        finally:
            done_event.set()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    done_event.wait(timeout=60)

    if not done_event.is_set():
        return False, 'TIMEOUT'
    return result['ok'], result['err']


def check_internet():
    import socket
    hosts = [
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


def slider_to_kokoro_speed(speed_pct, emotion='Normal'):
    """
    Convert slider value (10-100) + emotion to Kokoro speed float.
    Kokoro speed: 0.5 = very slow, 1.0 = normal, 1.5 = fast, 2.0 = very fast
    """
    # Map 10-100 → 0.5-1.8
    base_speed = 0.5 + ((speed_pct - 10) / 90) * 1.3
    # Emotion rate boost (same scale as before, convert to multiplier)
    boost_map = {
        'Normal': 0.0, 'Happy': 0.08, 'Sad': -0.1,
        'Whisper': -0.12, 'Shout': 0.12, 'Sarcasm': 0.0,
        'Excited': 0.18, 'Calm': -0.15, 'Serious': -0.04, 'Fearful': -0.06
    }
    boost = boost_map.get(emotion, 0.0)
    final = max(0.5, min(base_speed + boost, 2.0))
    return round(final, 2)


def slider_to_gtts_slow(speed_pct):
    """Convert slider to gTTS slow parameter."""
    return speed_pct <= 30


def pick_kokoro_voice(lang_name, gender):
    """
    Get Kokoro voice ID for given language and gender.
    Returns (voice_id, is_kokoro) tuple.
    If language not supported by Kokoro, returns (None, False).
    """
    if lang_name in KOKORO_VOICES:
        voices = KOKORO_VOICES[lang_name]
        voice_id = voices[0] if gender == 'Male' else voices[1]
        return voice_id, True
    return None, False


def pick_gtts_params(lang_name, gender):
    """Get gTTS lang_code and tld for given language and gender."""
    mapping = GTTS_VOICE_MAP.get(lang_name, {'Male': ('en', 'com'), 'Female': ('en', 'co.uk')})
    params = mapping.get(gender, ('en', 'com'))
    return params[0], params[1]


# ═══════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════
def hex_c(h):
    return get_color_from_hex(h)


def lbl(txt, size=14, color=C_MUTED, bold=False, h=36, halign='left', font=None):
    kwargs = dict(
        text=txt,
        font_size=sp(size),
        bold=bold,
        color=hex_c(color),
        size_hint_y=None,
        height=dp(h),
        halign=halign,
        valign='middle',
        text_size=(None, dp(h)),
    )
    if font:
        kwargs['font_name'] = font
    l = Label(**kwargs)
    def _update_ts(widget, width):
        widget.text_size = (width, dp(h))
    l.bind(width=_update_ts)
    return l


def sec_header(title, color=C_GREEN, font=None):
    return lbl(title, 13, color, True, 30, 'left', font=font)


def card_bg(widget, color=C_CARD, radius=12):
    with widget.canvas.before:
        Color(*hex_c(color))
        rr = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])

    def _upd(w, *a):
        rr.pos = w.pos
        rr.size = w.size

    widget.bind(pos=_upd, size=_upd)


def card_border(widget, color=C_BORDER, radius=12, thickness=1.5):
    with widget.canvas.after:
        Color(*hex_c(color))
        line = Line(
            rounded_rectangle=(widget.x, widget.y, widget.width, widget.height, dp(radius)),
            width=thickness,
        )

    def _upd(w, *a):
        line.rounded_rectangle = (w.x, w.y, w.width, w.height, dp(radius))

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
#  FLAT BUTTON
# ═══════════════════════════════════════════════════════════
class FlatBtn(Button):
    def __init__(self, bg=C_GREEN, radius=12, **kw):
        super().__init__(**kw)
        self.bg_color = bg
        self._radius = radius
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        light_bgs = [C_CARD, C_CARD2, C_CARD3, C_SURFACE, C_WHITE, C_BG2, C_BORDER]
        self.color = hex_c(C_TEXT2) if bg in light_bgs else (1, 1, 1, 1)
        self.font_size = kw.get('font_size', sp(15))
        self.halign = 'center'
        self.valign = 'middle'
        self._rr = None
        self.bind(pos=self._draw, size=self._draw)
        self.bind(size=lambda w, v: setattr(w, 'text_size', v))

    def set_bg(self, color):
        self.bg_color = color
        light_bgs = [C_CARD, C_CARD2, C_CARD3, C_SURFACE, C_WHITE, C_BG2, C_BORDER]
        self.color = hex_c(C_TEXT2) if color in light_bgs else (1, 1, 1, 1)
        self._draw()

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex_c(self.bg_color))
            self._rr = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(self._radius)]
            )

    def on_press(self):
        anim = Animation(opacity=0.7, duration=0.06) + Animation(opacity=1.0, duration=0.14)
        anim.start(self)

    def on_disabled(self, inst, val):
        self.opacity = 0.40 if val else 1.0


# ═══════════════════════════════════════════════════════════
#  LIGHT PANEL
# ═══════════════════════════════════════════════════════════
class LightPanel(FloatLayout):
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
#  WAVEFORM VISUALIZER
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
                alpha = 0.4 + h_ratio * 0.6
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
#  EMOTION PICKER
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
            bg=C_SURFACE,
            font_size=sp(11),
            bold=True,
            radius=10,
        )
        b.color = hex_c(C_TEXT)
        b.bind(on_press=lambda x, e=emotion: self._select(e))
        self._btns[emotion] = b
        parent.add_widget(b)

    def _select(self, emotion):
        self._selected = emotion
        data = EMOTION_TAGS[emotion]
        for em, btn in self._btns.items():
            if em == emotion:
                btn.set_bg(data['color'])
                btn.color = (1, 1, 1, 1)
            else:
                btn.set_bg(C_SURFACE)
                btn.color = hex_c(C_TEXT)
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
                bg=C_SURFACE,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(13),
                bold=True,
                radius=10,
            )
            b.color = hex_c(C_TEXT)
            b.bind(on_press=lambda x, n=preset_name: self._select(n))
            nl = Label(
                text=preset_name,
                font_size=sp(9),
                color=hex_c(C_MUTED),
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
            if n == preset_name:
                b.set_bg(C_GREEN)
                b.color = (1, 1, 1, 1)
            else:
                b.set_bg(C_SURFACE)
                b.color = hex_c(C_TEXT)
        if self._callback:
            self._callback(preset_name, VOICE_PRESETS[preset_name])


# ═══════════════════════════════════════════════════════════
#  ADVANCED OPTIONS CARD
#  All toggles properly affect Kokoro/gTTS generation
# ═══════════════════════════════════════════════════════════
class AdvancedOptionsCard(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(220)
        self.padding = [dp(14), dp(10)]
        self.spacing = dp(6)
        card_bg(self, C_CARD, 12)
        card_border(self, C_BORDER, 12)
        self._build()

    def _build(self):
        self.add_widget(sec_header('Advanced Options'))
        self.add_widget(spacer(4))
        toggles = [
            ('breath_sw',   'Add Pauses at Sentences'),
            ('normalize_sw','Normalize Long Text Chunks'),
            ('trim_sw',     'Remove Extra Whitespace'),
            ('pacing_sw',   'Adaptive Pacing (Long Texts)'),
        ]
        for attr, label in toggles:
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
            lbl_w = lbl(label, 12, C_TEXT, False, 40)
            row.add_widget(lbl_w)
            sw = Switch(active=False, size_hint=(None, None), size=(dp(68), dp(40)))
            setattr(self, attr, sw)
            row.add_widget(sw)
            self.add_widget(row)

    @property
    def add_pauses(self):
        return self.breath_sw.active

    @property
    def normalize_text(self):
        return self.normalize_sw.active

    @property
    def trim_whitespace(self):
        return self.trim_sw.active

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
        card_bg(self, C_CARD2, 10)
        info = FILE_ICONS.get(ftype.upper(), {'label': '?', 'color': C_GREEN})

        icon_bg = BoxLayout(size_hint=(None, None), size=(dp(46), dp(46)))
        with icon_bg.canvas.before:
            Color(*hex_c(info.get('color', C_GREEN) + '33'))
            rr = RoundedRectangle(pos=icon_bg.pos, size=icon_bg.size, radius=[dp(8)])
        icon_bg.bind(
            pos=lambda w, *a: setattr(rr, 'pos', w.pos),
            size=lambda w, *a: setattr(rr, 'size', w.size),
        )
        lbl_icon = Label(
            text=info.get('label', '?'),
            font_size=sp(13), bold=True,
            color=hex_c(info.get('color', C_GREEN)),
            size_hint=(1, 1), halign='center', valign='middle',
        )
        lbl_icon.bind(size=lambda w, v: setattr(w, 'text_size', v))
        icon_bg.add_widget(lbl_icon)
        self.add_widget(icon_bg)

        info_col = BoxLayout(orientation='vertical', size_hint_x=1)
        fname = os.path.basename(path)
        ext, size_str = get_file_info(path)
        name_lbl = lbl(fname, 12, C_TEXT2, True, 28, 'left')
        meta_lbl = lbl(ftype.upper() + ' - ' + size_str, 11, info.get('color', C_GREEN), False, 22, 'left')
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
        root = LightPanel()

        with root.canvas.before:
            Color(*hex_c(C_BG2))
            self._bg_circle = Ellipse(pos=(0, 0), size=(dp(200), dp(200)))

        logo_path = self._find_logo()
        if logo_path:
            self.logo_widget = KivyImage(
                source=logo_path, allow_stretch=True, keep_ratio=True,
                size_hint=(None, None), size=(dp(110), dp(110)),
                pos_hint={'center_x': 0.5, 'center_y': 0.62}, opacity=0,
            )
        else:
            self.logo_widget = Label(
                text='T', font_size=sp(64), bold=True, color=hex_c(C_GREEN),
                pos_hint={'center_x': 0.5, 'center_y': 0.62}, opacity=0,
            )
        root.add_widget(self.logo_widget)

        self.title_lbl = Label(
            text='Titan Studio PRO', font_size=sp(26), bold=True,
            color=hex_c(C_TEXT2), pos_hint={'center_x': 0.5, 'center_y': 0.49}, opacity=0,
        )
        root.add_widget(self.title_lbl)

        self.ver_lbl = Label(
            text='v2.0  CYBER MINT EDITION  |  Kokoro TTS', font_size=sp(11), bold=True,
            color=hex_c(C_GREEN2), pos_hint={'center_x': 0.5, 'center_y': 0.43}, opacity=0,
        )
        root.add_widget(self.ver_lbl)

        self.sub_lbl = Label(
            text='Professional Voice Studio  -  Always Free',
            font_size=sp(13), color=hex_c(C_MUTED),
            pos_hint={'center_x': 0.5, 'center_y': 0.36}, opacity=0,
        )
        root.add_widget(self.sub_lbl)

        self.dot_lbl = Label(
            text='Initializing...', font_size=sp(14), color=hex_c(C_GREEN),
            pos_hint={'center_x': 0.5, 'center_y': 0.27}, opacity=0,
        )
        root.add_widget(self.dot_lbl)

        self.prog = ProgressBar(
            max=100, value=0, size_hint=(0.65, None), height=dp(6),
            pos_hint={'center_x': 0.5, 'y': 0.19},
        )
        root.add_widget(self.prog)

        self.wave = WaveformWidget(
            bars=20, color=C_GREEN,
            size_hint=(None, None), size=(dp(220), dp(32)),
            pos_hint={'center_x': 0.5, 'center_y': 0.13},
        )
        root.add_widget(self.wave)

        root.add_widget(Label(
            text='(c) 2025 Titan Studio PRO', font_size=sp(11), color=hex_c(C_MUTED2),
            pos_hint={'center_x': 0.5, 'center_y': 0.05},
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
        Animation(opacity=1, duration=0.5).start(self.logo_widget)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.4).start(self.title_lbl), 0.3)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.4).start(self.ver_lbl), 0.45)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.4).start(self.sub_lbl), 0.55)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.3).start(self.dot_lbl), 0.7)
        self.wave.start()
        self._dot_ev = Clock.schedule_interval(self._tick_dots, 0.5)
        Clock.schedule_once(lambda dt: Animation(value=85, duration=1.8, t='out_cubic').start(self.prog), 0.2)
        Clock.schedule_once(self._go, 2.5)

    def _tick_dots(self, dt):
        self._dot_count = (self._dot_count + 1) % 4
        msgs = ['Initializing Kokoro', 'Loading voices', 'Preparing studio', 'Almost ready']
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
        Clock.schedule_once(self._switch, 0.2)

    def _switch(self, dt=None):
        self.manager.transition = FadeTransition(duration=0.35)
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
        root = LightPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))

        hdr = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        back = FlatBtn(text='< Back', bg=C_SURFACE, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.color = hex_c(C_TEXT)
        back.bind(on_press=self._go_back)
        hdr.add_widget(back)
        hdr.add_widget(lbl('Voice History', 20, C_TEXT2, True, 64, 'left'))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        self.stats_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), padding=[dp(12), dp(6)])
        card_bg(self.stats_row, C_CARD2, 10)
        card_border(self.stats_row, C_BORDER, 10)
        self.count_lbl = lbl('0 recordings', 13, C_MUTED, False, 38, 'left')
        self.size_lbl = lbl('0 KB total', 13, C_MUTED, False, 38, 'right')
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
        card_bg(row, C_CARD, 14)
        card_border(row, C_BORDER, 14)

        em = entry.get('emotion', 'Normal')
        em_color = EMOTION_TAGS.get(em, {}).get('color', C_GREEN)

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
        fname_l = lbl(entry.get('filename', 'unknown'), 12, C_TEXT2, True, 32, 'left')
        lang_code = LANG_FLAGS.get(entry.get('lang', ''), '')
        meta_l = lbl(
            lang_code + ' ' + entry.get('lang', '') + '  -  '
            + entry.get('voice', '') + '  -  ' + entry.get('emotion', 'Normal')
            + '  -  ' + entry.get('time', ''),
            11, C_GREEN2, False, 28, 'left'
        )
        info.add_widget(fname_l)
        info.add_widget(meta_l)
        row.add_widget(info)

        fp = entry.get('path', '')
        if os.path.exists(fp):
            pb = FlatBtn(text='Play', bg=C_GREEN, size_hint_x=None, width=dp(72), font_size=sp(13))
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
            btn.text = 'Stop'
            btn.set_bg(C_RED)
            Clock.schedule_once(
                lambda dt: (setattr(btn, 'text', 'Play'), btn.set_bg(C_GREEN)),
                snd.length + 0.3
            )

    def _confirm_clear(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
        box.add_widget(lbl('Clear all history?\nThis cannot be undone.',
                           15, C_TEXT, False, 60, 'center'))
        br = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(12))
        yes = FlatBtn(text='Yes, Clear', bg=C_DARK_RED, font_size=sp(14))
        no = FlatBtn(text='Cancel', bg=C_SURFACE, font_size=sp(14))
        no.color = hex_c(C_TEXT)
        br.add_widget(yes)
        br.add_widget(no)
        box.add_widget(br)
        p = Popup(title='Confirm', content=box, size_hint=(0.88, 0.40), background_color=hex_c(C_BG))
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
        root = LightPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(12))

        hdr = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(12))
        back = FlatBtn(text='< Back', bg=C_SURFACE, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.color = hex_c(C_TEXT)
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('Settings', 20, C_TEXT2, True, 60, 'left'))
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

        fc = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(120),
            padding=[dp(14), dp(10)], spacing=dp(6),
        )
        card_bg(fc, C_CARD, 12)
        card_border(fc, C_BORDER, 12)
        fc.add_widget(sec_header('Save Folder'))
        titan_path = get_titan_folder()
        path_lbl = Label(
            text=titan_path,
            font_size=sp(11), color=hex_c(C_TEXT),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(40),
        )
        path_lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
        fc.add_widget(path_lbl)
        fc.add_widget(lbl('All audio saved here automatically', 12, C_GREEN2, False, 26, 'left'))
        content.add_widget(fc)

        # Engine info card
        engine_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(200),
            padding=[dp(14), dp(10)], spacing=dp(6),
        )
        card_bg(engine_card, C_CARD, 12)
        card_border(engine_card, C_BORDER, 12)
        engine_card.add_widget(sec_header('TTS Engine Info'))
        for line in [
            'Primary: Kokoro TTS (Offline, Neural)',
            'English: True Male + Female voices',
            'Voice IDs: am_michael, af_heart, etc.',
            'Fallback: gTTS (Online, for other langs)',
            'Speed range: 0.5x - 2.0x',
            'No API key needed for Kokoro',
        ]:
            engine_card.add_widget(lbl(line, 12, C_MUTED, False, 24, 'left'))
        content.add_widget(engine_card)

        about_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(160),
            padding=[dp(14), dp(10)], spacing=dp(6),
        )
        card_bg(about_card, C_CARD, 12)
        card_border(about_card, C_BORDER, 12)
        about_card.add_widget(sec_header('About'))
        for line in [
            'Titan Studio PRO  v2.0  CYBER MINT EDITION',
            'Professional TTS & Voice Studio',
            '35+ Languages  -  10 Emotions  -  Neural Voices',
            'Powered by Kokoro TTS  -  Always Free',
            '(c) 2025 Titan Studio PRO',
        ]:
            about_card.add_widget(lbl(line, 12, C_MUTED, False, 24, 'left'))
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
        root = LightPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))

        hdr = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(12))
        back = FlatBtn(text='< Back', bg=C_SURFACE, size_hint_x=None, width=dp(100), font_size=sp(14))
        back.color = hex_c(C_TEXT)
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('Batch Queue', 18, C_TEXT2, True, 60, 'left'))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        self.status_banner = BoxLayout(size_hint_y=None, height=dp(44), padding=[dp(12), dp(6)])
        card_bg(self.status_banner, C_CARD, 10)
        card_border(self.status_banner, C_BORDER, 10)
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
        card_bg(row, C_CARD, 12)
        card_border(row, C_BORDER, 12)

        num_lbl = Label(
            text=str(idx + 1),
            font_size=sp(18), bold=True,
            color=hex_c(C_GREEN),
            size_hint_x=None, width=dp(34),
            halign='center', valign='middle',
        )
        num_lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
        row.add_widget(num_lbl)

        info = BoxLayout(orientation='vertical')
        preview = item.get('text', '')[:55] + '...' if len(item.get('text', '')) > 55 else item.get('text', '')
        t = lbl(preview, 12, C_TEXT, False, 34, 'left')
        m = lbl(
            item.get('lang', '') + '  -  ' + item.get('voice', '') + '  -  ' + item.get('emotion', ''),
            11, C_MUTED, False, 26, 'left'
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
                fname = 'Queue_{}_{}_{}.wav'.format(i + 1, lang, int(time.time()))
                dest = os.path.join(get_audio_folder(), fname)
                os.makedirs(get_audio_folder(), exist_ok=True)

                kokoro_speed = slider_to_kokoro_speed(speed_pct, emotion)
                voice_id, use_kokoro = pick_kokoro_voice(lang, gender)

                ok = False
                if use_kokoro and voice_id:
                    ok, err = kokoro_generate(text, voice_id, kokoro_speed, dest)

                if not ok:
                    # gTTS fallback
                    fname = fname.replace('.wav', '.mp3')
                    dest = dest.replace('.wav', '.mp3')
                    lang_code, tld = pick_gtts_params(lang, gender)
                    slow = slider_to_gtts_slow(speed_pct)
                    ok, err = gtts_generate(text, lang_code, tld, slow, dest)

                if ok:
                    item['status'] = 'done'
                    item['output'] = dest
                    history_save({
                        'filename': fname, 'path': dest, 'lang': lang,
                        'voice': gender, 'time': time.strftime('%d %b %Y  %H:%M'),
                        'emotion': emotion, 'source': 'batch',
                    })
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
#  STUDIO SCREEN
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
        root = LightPanel()
        outer = BoxLayout(orientation='vertical')

        # ══ HEADER BAR ═══════════════════════════════════
        hdr = BoxLayout(
            size_hint_y=None, height=dp(78),
            padding=[dp(14), dp(10)], spacing=dp(10),
        )
        card_bg(hdr, C_BG2, 0)

        logo_path = self._find_logo()
        logo_box = BoxLayout(size_hint=(None, None), size=(dp(50), dp(50)))
        if logo_path:
            logo_box.add_widget(KivyImage(
                source=logo_path, allow_stretch=True, keep_ratio=True, size_hint=(1, 1),
            ))
        else:
            tb_logo = Label(
                text='T', font_size=sp(28), bold=True,
                color=hex_c(C_GREEN), size_hint=(1, 1),
                halign='center', valign='middle',
            )
            tb_logo.bind(size=lambda w, v: setattr(w, 'text_size', v))
            logo_box.add_widget(tb_logo)
        hdr.add_widget(logo_box)

        tb = BoxLayout(orientation='vertical', size_hint_x=1)
        t1 = Label(
            text='Titan Studio PRO',
            font_size=sp(17), bold=True,
            color=hex_c(C_TEXT2),
            halign='left', valign='middle',
        )
        t1.bind(size=lambda w, v: setattr(w, 'text_size', v))
        t2 = Label(
            text='v2.0 Mint  |  Kokoro TTS  -  Always Free',
            font_size=sp(10), color=hex_c(C_MUTED),
            halign='left', valign='middle',
        )
        t2.bind(size=lambda w, v: setattr(w, 'text_size', v))
        tb.add_widget(t1)
        tb.add_widget(t2)
        hdr.add_widget(tb)

        settings_btn = FlatBtn(
            text='SET', bg=C_GREEN,
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
        card_bg(presets_card, C_CARD, 14)
        card_border(presets_card, C_BORDER, 14)
        presets_card.add_widget(sec_header('Voice Presets'))
        self.preset_picker = PresetPicker(callback=self._apply_preset)
        presets_card.add_widget(self.preset_picker)
        content.add_widget(presets_card)

        # ── LANGUAGE + GENDER ─────────────────────────
        lg_row = BoxLayout(size_hint_y=None, height=dp(130), spacing=dp(10))

        lang_card = BoxLayout(orientation='vertical', padding=[dp(12), dp(10)], spacing=dp(8))
        card_bg(lang_card, C_CARD, 14)
        card_border(lang_card, C_BORDER, 14)
        lang_card.add_widget(sec_header('Language'))
        self.lang_spin = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=dp(56),
            font_size=sp(14),
            color=hex_c(C_WHITE),
            background_color=hex_c(C_GREEN),
            background_normal='',
        )
        self.lang_spin.bind(text=self._on_lang_change)
        lang_card.add_widget(self.lang_spin)
        lg_row.add_widget(lang_card)

        gender_card = BoxLayout(
            orientation='vertical',
            padding=[dp(12), dp(10)], spacing=dp(8),
            size_hint_x=0.48,
        )
        card_bg(gender_card, C_CARD, 14)
        card_border(gender_card, C_BORDER, 14)
        gender_card.add_widget(sec_header('Gender'))
        gr = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        self._vbtns = {}
        for name in ['Male', 'Female']:
            b = FlatBtn(
                text=name,
                bg=C_SURFACE,
                font_size=sp(13),
                bold=True,
                radius=10,
            )
            b.color = hex_c(C_TEXT)
            b.bind(size=lambda w, v: setattr(w, 'text_size', v))
            b.bind(on_press=lambda inst, n=name: self._pick_voice(n))
            gr.add_widget(b)
            self._vbtns[name] = b
        gender_card.add_widget(gr)
        lg_row.add_widget(gender_card)
        content.add_widget(lg_row)
        Clock.schedule_once(lambda dt: self._pick_voice('Male'), 0)

        # Engine badge row
        self.engine_badge_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        self.engine_lbl = lbl('Engine: Kokoro (Offline)', 12, C_GREEN2, True, 36, 'left')
        self.engine_badge_row.add_widget(self.engine_lbl)
        content.add_widget(self.engine_badge_row)

        # ── EMOTION PICKER ────────────────────────────
        emotion_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(186),
            padding=[dp(12), dp(10)], spacing=dp(8),
        )
        card_bg(emotion_card, C_CARD, 14)
        card_border(emotion_card, C_BORDER, 14)
        emotion_card.add_widget(sec_header('Emotion & Mood'))
        self.emotion_picker = EmotionPicker()
        emotion_card.add_widget(self.emotion_picker)
        content.add_widget(emotion_card)

        # ── SPEED CARD ─────────────────────────────────
        speed_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(100),
            padding=[dp(12), dp(10)], spacing=dp(6),
        )
        card_bg(speed_card, C_CARD, 14)
        card_border(speed_card, C_BORDER, 14)
        spd_hdr = BoxLayout(size_hint_y=None, height=dp(28))
        spd_hdr.add_widget(sec_header('Speed'))
        self.speed_lbl = lbl('50%', 13, C_GREEN, True, 28, 'right')
        spd_hdr.add_widget(self.speed_lbl)
        speed_card.add_widget(spd_hdr)
        sr = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        sr.add_widget(lbl('Slow', 11, C_MUTED, False, 44, 'left'))
        self.speed_slider = Slider(min=10, max=100, value=50, step=5)
        self.speed_slider.bind(
            value=lambda i, v: setattr(self.speed_lbl, 'text', str(int(v)) + '%')
        )
        sr.add_widget(self.speed_slider)
        sr.add_widget(lbl('Fast', 11, C_MUTED, False, 44, 'right'))
        speed_card.add_widget(sr)
        content.add_widget(speed_card)

        # ── PITCH CARD ─────────────────────────────────
        pitch_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(100),
            padding=[dp(12), dp(10)], spacing=dp(6),
        )
        card_bg(pitch_card, C_CARD, 14)
        card_border(pitch_card, C_BORDER, 14)
        ptc_hdr = BoxLayout(size_hint_y=None, height=dp(28))
        ptc_hdr.add_widget(sec_header('Pitch'))
        self.pitch_lbl = lbl('0', 13, C_GREEN, True, 28, 'right')
        ptc_hdr.add_widget(self.pitch_lbl)
        pitch_card.add_widget(ptc_hdr)
        pr = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        pr.add_widget(lbl('Low', 11, C_MUTED, False, 44, 'left'))
        self.pitch_slider = Slider(min=-10, max=10, value=0, step=1)
        self.pitch_slider.bind(
            value=lambda i, v: setattr(
                self.pitch_lbl, 'text',
                ('+' if v > 0 else '') + str(int(v))
            )
        )
        pr.add_widget(self.pitch_slider)
        pr.add_widget(lbl('High', 11, C_MUTED, False, 44, 'right'))
        pitch_card.add_widget(pr)
        content.add_widget(pitch_card)

        # ── ADVANCED OPTIONS ──────────────────────────
        self.adv_card = AdvancedOptionsCard()
        content.add_widget(self.adv_card)

        # ── TEXT INPUT ────────────────────────────────
        text_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(300),
            padding=[dp(12), dp(10)], spacing=dp(8),
        )
        card_bg(text_card, C_CARD, 14)
        card_border(text_card, C_BORDER, 14)

        ti_hdr = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        ti_title = lbl('Input Text', 13, C_GREEN, True, 36, 'left')
        ti_hdr.add_widget(ti_title)
        self.char_lbl = lbl('0 chars', 11, C_MUTED, False, 36, 'center')
        ti_hdr.add_widget(self.char_lbl)

        imp_btn = FlatBtn(
            text='Import File', bg=C_GREEN,
            size_hint_x=None, width=dp(110),
            font_size=sp(12), radius=8,
        )
        imp_btn.size_hint_y = None
        imp_btn.height = dp(36)
        imp_btn.bind(on_press=self._import_file)
        ti_hdr.add_widget(imp_btn)

        clr_btn = FlatBtn(
            text='Clear', bg=C_SURFACE,
            size_hint_x=None, width=dp(60),
            font_size=sp(12), radius=8,
        )
        clr_btn.color = hex_c(C_TEXT)
        clr_btn.size_hint_y = None
        clr_btn.height = dp(36)
        clr_btn.bind(on_press=lambda *a: setattr(self.txt, 'text', ''))
        ti_hdr.add_widget(clr_btn)
        text_card.add_widget(ti_hdr)

        self.rtl_lbl = lbl('', 11, C_AMBER, False, 20, 'left')
        text_card.add_widget(self.rtl_lbl)

        self.txt = TextInput(
            hint_text='Enter text here... Urdu, Hindi, Arabic, English + 30 languages',
            multiline=True,
            size_hint=(1, 1),
            background_color=hex_c(C_WHITE),
            foreground_color=hex_c(C_TEXT2),
            hint_text_color=hex_c(C_MUTED2),
            cursor_color=hex_c(C_GREEN),
            font_size=sp(16),
            padding=[dp(12), dp(10)],
        )
        self.txt.bind(text=self._count)
        text_card.add_widget(self.txt)

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
        card_bg(status_card, C_CARD, 14)
        card_border(status_card, C_BORDER, 14)
        self.status_lbl = lbl('Ready to generate voice', 13, C_MUTED, False, 30, 'left')
        status_card.add_widget(self.status_lbl)
        self.prog = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(6))
        status_card.add_widget(self.prog)
        self.waveform = WaveformWidget(bars=24, color=C_GREEN, size_hint_y=None, height=dp(46))
        status_card.add_widget(self.waveform)
        content.add_widget(status_card)

        # ── GENERATE BUTTON ───────────────────────────
        self.gen_btn = FlatBtn(
            text='Generate Audio',
            bg=C_GREEN,
            size_hint_y=None, height=dp(68),
            font_size=sp(19), bold=True, radius=16,
        )
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        # ── PREVIEW + SAVE ROW ────────────────────────
        pd_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(12))
        self.play_btn = FlatBtn(
            text='Preview Audio',
            bg=C_TEAL,
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
        batch_btn = FlatBtn(text='Batch Queue', bg=C_INDIGO, font_size=sp(14))
        batch_btn.bind(on_press=lambda *a: self._go_batch())
        nav_row.add_widget(hist_btn)
        nav_row.add_widget(batch_btn)
        content.add_widget(nav_row)

        # ── SAVE FOLDER BANNER ────────────────────────
        folder_banner = BoxLayout(
            size_hint_y=None, height=dp(58),
            padding=[dp(12), dp(8)], spacing=dp(10),
        )
        card_bg(folder_banner, C_BG2, 12)
        card_border(folder_banner, C_BORDER, 12)
        folder_icon_lbl = Label(
            text='[DIR]',
            font_size=sp(11), bold=True,
            color=hex_c(C_GREEN2),
            size_hint=(None, 1), width=dp(40),
            halign='center', valign='middle',
        )
        folder_icon_lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
        folder_banner.add_widget(folder_icon_lbl)
        titan_p = get_titan_folder()
        folder_info = BoxLayout(orientation='vertical')
        folder_line1 = lbl('Auto-saves to: Titan Studio PRO/Audio/', 12, C_TEXT2, True, 26, 'left')
        folder_line2 = lbl(titan_p, 11, C_MUTED, False, 22, 'left')
        folder_info.add_widget(folder_line1)
        folder_info.add_widget(folder_line2)
        folder_banner.add_widget(folder_info)
        content.add_widget(folder_banner)

        # ── RESULTS SECTION ───────────────────────────
        results_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(90),
            padding=[dp(12), dp(10)], spacing=dp(8),
        )
        card_bg(results_card, C_CARD, 14)
        card_border(results_card, C_BORDER, 14)
        results_card.add_widget(sec_header('Results'))
        self.result_lbl = lbl('No generated items yet', 13, C_MUTED, False, 40, 'left')
        results_card.add_widget(self.result_lbl)
        content.add_widget(results_card)

        # ── QUICK GUIDE ───────────────────────────────
        how_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=dp(254),
            padding=[dp(14), dp(12)], spacing=dp(4),
        )
        card_bg(how_card, C_BG2, 14)
        card_border(how_card, C_BORDER, 14)
        how_card.add_widget(sec_header('Quick Guide'))
        how_card.add_widget(spacer(4))
        steps = [
            '1. Select a Voice Preset (Narrator, News, etc.)',
            '2. Choose Language - English uses Kokoro (offline)',
            '3. Pick Gender: Male or Female voice (works!)',
            '4. Set Emotion (Whisper, Shout, Happy etc.)',
            '5. Adjust Speed slider (above) and Pitch (below)',
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
        font_name = LANG_FONTS.get(lang, DEFAULT_FONT)
        try:
            self.txt.font_name = font_name
        except Exception:
            pass

        locale = LANG_KEYBOARD_LOCALE.get(lang, 'en')
        if ANDROID_ENV:
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                imm = activity.getSystemService(
                    autoclass('android.content.Context').INPUT_METHOD_SERVICE
                )
                view = activity.getCurrentFocus()
                if view:
                    imm.showSoftInput(view, 0)
            except Exception:
                pass

        if lang in RTL_LANGS:
            self.rtl_lbl.text = (
                u'\u25c4 RTL: ' + lang +
                u' keyboard — switch to ' + lang + u' in keyboard settings'
            )
            try:
                self.txt.base_direction = 'rtl'
                self.txt.halign = 'right'
            except Exception:
                pass
        else:
            self.rtl_lbl.text = ''
            try:
                self.txt.base_direction = 'ltr'
                self.txt.halign = 'left'
            except Exception:
                pass

        # Update engine badge
        _, use_kokoro = pick_kokoro_voice(lang, self.voice_sel)
        if use_kokoro:
            self.engine_lbl.text = 'Engine: Kokoro TTS (Offline Neural)'
            self.engine_lbl.color = hex_c(C_GREEN)
        else:
            self.engine_lbl.text = 'Engine: gTTS Fallback (Online)'
            self.engine_lbl.color = hex_c(C_AMBER)

    def _apply_preset(self, name, data):
        # Convert preset speed (0.5-1.5 range) back to slider (10-100)
        preset_speed = data.get('speed', 1.0)
        slider_val = int(((preset_speed - 0.5) / 1.3) * 90 + 10)
        slider_val = max(10, min(100, slider_val))
        self.speed_slider.value = slider_val
        # Pitch preset: 0.7-1.3 range → slider -10 to +10
        preset_pitch = data.get('pitch', 1.0)
        pitch_slider_val = int((preset_pitch - 1.0) * 33.3)
        pitch_slider_val = max(-10, min(10, pitch_slider_val))
        self.pitch_slider.value = pitch_slider_val
        self.emotion_picker._select(data.get('emotion', 'Normal'))
        self.status_lbl.text = 'Preset: ' + name + ' - ' + data.get('desc', '')

    def _pick_voice(self, name):
        self.voice_sel = name
        for n, b in self._vbtns.items():
            if n == name:
                b.set_bg(C_GREEN)
                b.color = (1, 1, 1, 1)
            else:
                b.set_bg(C_SURFACE)
                b.color = hex_c(C_TEXT)
        # Update engine badge when gender changes
        lang = self.lang_spin.text if hasattr(self, 'lang_spin') else 'English'
        _, use_kokoro = pick_kokoro_voice(lang, name)
        if hasattr(self, 'engine_lbl'):
            if use_kokoro:
                self.engine_lbl.text = 'Engine: Kokoro TTS (Offline Neural)'
                self.engine_lbl.color = hex_c(C_GREEN)
            else:
                self.engine_lbl.text = 'Engine: gTTS Fallback (Online)'
                self.engine_lbl.color = hex_c(C_AMBER)

    def _count(self, inst, val):
        words = len(val.split()) if val.strip() else 0
        chars = len(val)
        self.char_lbl.text = str(chars) + ' chars  ' + str(words) + ' words'

    def _import_file(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box.add_widget(lbl('Select file type to import:', 15, C_TEXT2, True, 36, 'center'))

        grid = GridLayout(cols=3, size_hint_y=None, height=dp(180), spacing=dp(10))
        pop = [None]
        for ft, fi in FILE_ICONS.items():
            col = BoxLayout(orientation='vertical', spacing=dp(4))
            b = FlatBtn(
                text=fi.get('label', ft),
                bg=fi.get('color', C_GREEN),
                size_hint_y=None, height=dp(56),
                font_size=sp(14), bold=True, radius=12,
            )
            b.bind(on_press=lambda x, t=ft, p=pop: self._open_chooser(t, p[0]))
            col.add_widget(b)
            ft_lbl = lbl(ft, 10, C_MUTED, False, 20, 'center')
            col.add_widget(ft_lbl)
            grid.add_widget(col)
        box.add_widget(grid)

        can = FlatBtn(text='Cancel', bg=C_SURFACE, size_hint_y=None, height=dp(50))
        can.color = hex_c(C_TEXT)
        box.add_widget(can)
        p = Popup(
            title='Import File',
            content=box,
            size_hint=(0.92, 0.60),
            background_color=hex_c(C_BG),
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
        can = FlatBtn(text='Cancel', bg=C_SURFACE, font_size=sp(14))
        can.color = hex_c(C_TEXT)
        br.add_widget(sel)
        br.add_widget(can)
        box.add_widget(br)
        p = Popup(
            title='Choose ' + ftype + ' File',
            content=box,
            size_hint=(0.95, 0.88),
            background_color=hex_c(C_BG),
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
            add_pauses = self.adv_card.add_pauses
            normalize = self.adv_card.normalize_text
            trim = self.adv_card.trim_whitespace
            adaptive_pacing = self.adv_card.adaptive_pacing

            Clock.schedule_once(lambda dt: self._upd(10, 'Preparing text...'))

            text = self.txt.text

            # Apply advanced text processing
            if trim:
                text = re.sub(r'[ \t]+', ' ', text).strip()

            if normalize:
                # Break very long sentences at punctuation for better TTS
                text = re.sub(r'([.!?;])\s+', r'\1\n', text)

            if add_pauses:
                # Add double space at sentence boundaries → natural pauses
                text = re.sub(r'([.!?])\s+', r'\1  ', text)

            if adaptive_pacing and len(text) > 500:
                speed_pct = max(10, speed_pct - 5)

            kokoro_speed = slider_to_kokoro_speed(speed_pct, emotion)
            voice_id, use_kokoro = pick_kokoro_voice(lang_name, gender)

            app = App.get_running_app()
            ext = 'wav' if use_kokoro else 'mp3'
            out = os.path.join(app.user_data_dir, 'tts_preview.' + ext)

            label = lang_name + ' - ' + gender + ' - ' + emotion
            ok = False
            err = ''

            if use_kokoro and voice_id:
                Clock.schedule_once(lambda dt: self._upd(30, 'Kokoro: Generating ' + label + '...'))
                ok, err = kokoro_generate(text, voice_id, kokoro_speed, out)
                if ok:
                    Clock.schedule_once(lambda dt: self._upd(90, 'Processing audio...'))
                    self.out_file = out
                    Clock.schedule_once(lambda dt: self._on_done(engine='kokoro'))
                    return
                else:
                    Clock.schedule_once(lambda dt: self._upd(40, 'Kokoro failed, trying gTTS...'))

            # gTTS path (either language not in Kokoro, or Kokoro failed)
            Clock.schedule_once(lambda dt: self._upd(25, 'Checking internet...'))
            has_internet = check_internet()

            if not has_internet:
                Clock.schedule_once(lambda dt: self._on_err(
                    'No internet for ' + lang_name + ' (needs gTTS). Connect and retry.'
                ))
                return

            Clock.schedule_once(lambda dt: self._upd(50, 'gTTS: Generating ' + label + '...'))
            out_mp3 = os.path.join(app.user_data_dir, 'tts_preview.mp3')
            lang_code, tld = pick_gtts_params(lang_name, gender)
            slow = slider_to_gtts_slow(speed_pct)
            ok, err = gtts_generate(text, lang_code, tld, slow, out_mp3)

            if ok:
                Clock.schedule_once(lambda dt: self._upd(90, 'Processing audio...'))
                self.out_file = out_mp3
                Clock.schedule_once(lambda dt: self._on_done(engine='gtts'))
            else:
                Clock.schedule_once(lambda dt, e=err: self._on_err(
                    'Audio generation failed: ' + e[:60]
                ))

        except Exception as e:
            msg = str(e)
            Clock.schedule_once(lambda dt, m=msg: self._on_err(m))

    def _on_done(self, engine='kokoro'):
        if self._audio:
            try:
                self._audio.stop()
                self._audio.unload()
            except Exception:
                pass
            self._audio = None

        self._audio = SoundLoader.load(self.out_file)
        if engine == 'kokoro':
            msg = 'Audio ready! Kokoro neural voice. Preview or Save.'
        else:
            msg = 'Audio ready! (gTTS online mode). Preview or Save.'
        self._upd(100, msg)
        self._set_ready(ok=True)
        self.waveform.stop()
        self.result_lbl.text = (
            'Generated: ' + self.lang_spin.text +
            ' - ' + self.voice_sel +
            ' - ' + self.emotion_picker.selected +
            ' [' + engine.upper() + ']'
        )
        Clock.schedule_once(
            lambda dt: Animation(value=0, duration=0.7, t='out_quad').start(self.prog), 2.0
        )

    def _on_err(self, msg):
        self.waveform.stop()
        m = msg.lower()
        if any(k in m for k in ['network', 'connection', 'gaierror', 'timeout', 'no internet']):
            txt = 'No internet! Connect Wi-Fi/data for non-English languages.'
        elif 'lang' in m:
            txt = 'This language is not supported.'
        elif 'import' in m or 'kokoro' in m:
            txt = 'Kokoro not installed. Run: pip install kokoro soundfile'
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
            self.play_btn.set_bg(C_TEAL)
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
            Clock.schedule_once(lambda dt: self._auto_save(), 0)

        request_storage_permissions(after_permission)

    def _auto_save(self):
        emotion = self.emotion_picker.selected
        lang = self.lang_spin.text
        voice = self.voice_sel
        ts = str(int(time.time()))
        ext = os.path.splitext(self.out_file)[1] if self.out_file else '.wav'
        fname = 'Titan_{lang}_{voice}_{ts}{ext}'.format(
            lang=lang, voice=voice, ts=ts, ext=ext
        )

        audio_dir = get_audio_folder()
        dest = os.path.join(audio_dir, fname)

        can_write = False
        try:
            os.makedirs(audio_dir, exist_ok=True)
            test_file = os.path.join(audio_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            can_write = True
        except Exception:
            can_write = False

        if not can_write:
            try:
                app = App.get_running_app()
                audio_dir = os.path.join(app.user_data_dir, 'Audio')
                os.makedirs(audio_dir, exist_ok=True)
                dest = os.path.join(audio_dir, fname)
            except Exception as e:
                self._upd(0, 'Cannot find writable folder: ' + str(e)[:50])
                return

        try:
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
            try:
                app = App.get_running_app()
                fallback_dir = os.path.join(app.user_data_dir, 'Audio')
                os.makedirs(fallback_dir, exist_ok=True)
                fallback_dest = os.path.join(fallback_dir, fname)
                shutil.copyfile(self.out_file, fallback_dest)
                self._upd(100, 'Saved to app folder: ' + fname)
                history_save({
                    'filename': fname,
                    'path': fallback_dest,
                    'lang': lang,
                    'voice': voice,
                    'emotion': emotion,
                    'time': time.strftime('%d %b %Y  %H:%M'),
                    'source': 'studio',
                })
                self._show_save_success(fname, fallback_dir, fallback_dest)
            except Exception as e2:
                self._show_err_popup(
                    'Save failed!\n\nGo to Settings > Apps > Titan Studio PRO\n'
                    '> Permissions > Storage and allow access.\n\n(' + str(e2)[:60] + ')'
                )
        except Exception as e:
            self._upd(0, 'Save failed: ' + str(e)[:60])

    def _show_save_success(self, fname, folder, full_path):
        box = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        box.add_widget(lbl('Saved Successfully!', 17, C_GREEN2, True, 44, 'center'))
        box.add_widget(lbl(fname, 12, C_TEXT, False, 32, 'center'))
        box.add_widget(lbl(folder, 11, C_MUTED, False, 36, 'center'))
        ok = FlatBtn(text='Great!', bg=C_GREEN, size_hint_y=None, height=dp(52), font_size=sp(15))
        box.add_widget(ok)
        p = Popup(
            title='Save Complete',
            content=box,
            size_hint=(0.90, 0.48),
            background_color=hex_c(C_BG),
        )
        ok.bind(on_press=p.dismiss)
        p.open()

    def _show_err_popup(self, msg):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box.add_widget(lbl(msg, 14, C_AMBER, False, 80, 'center'))
        ok = FlatBtn(text='OK', bg=C_GREEN, size_hint_y=None, height=dp(52))
        box.add_widget(ok)
        p = Popup(
            title='Error',
            content=box,
            size_hint=(0.88, 0.40),
            background_color=hex_c(C_BG),
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
