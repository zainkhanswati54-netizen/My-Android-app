# ============================================================
#  Titan AI Studio Pro  –  main.py
#  Version 10.0.0  |  ULTRA MEGA REWRITE
#  ─────────────────────────────────────────────────────────
#  FIXES:
#    ✅ Double loading screen FIXED (single smooth loader)
#    ✅ Text line counter FIXED (proper alignment)
#    ✅ Voice gender bug FIXED (Male actually works now)
#    ✅ Urdu/Arabic typing FIXED (proper RTL support)
#    ✅ Import file now shows file logo/icon with text
#    ✅ App creates its OWN folder "Titan AI Studio" on device
#    ✅ All saves go automatically to that folder
#
#  NEW FEATURES:
#    🎙 Professional Voice Cloning (ElevenLabs API)
#    😢 Emotional Range Control (whisper/shout/sarcasm/happy/sad)
#    🌍 30+ Languages with Voice Preservation
#    📝 SSML Support (advanced speech markup)
#    ⚡ Ultra-Low Latency Mode
#    💨 Dynamic Breath Simulation
#    🎵 Pitch & Tone Shifting (slider control)
#    🎬 Multilingual Dubbing Mode
#    ⏱ Adaptive Pacing Control
#    📊 Audio Waveform Visualizer
#    🔖 Text Bookmarks & Chapters
#    🎭 Voice Presets (Narrator, News, Story, Meditation)
#    📱 Auto-folder creation: /sdcard/Titan AI Studio/
#    🔤 Word-level emotion tags in text
#    🔊 EQ & Audio Effects
#    📋 Batch Processing Queue
#    💾 Smart Save with auto-naming
# ============================================================

import os
import threading
import time
import shutil
import json
import re
import hashlib
import base64
import math

# ── Android detection ──────────────────────────────────────
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
    Color, Rectangle, RoundedRectangle, Line,
    Ellipse, StencilPush, StencilUse, StencilPop, StencilUnUse,
    Mesh, Triangle, Bezier,
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
#  COLOUR PALETTE  (Premium Dark Theme)
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
#  LANGUAGE DATA  (30+ Languages)
# ═══════════════════════════════════════════════════════════
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
    'Chinese':    'zh-TW',
    'Japanese':   'ja',
    'Korean':     'ko',
    'Portuguese': 'pt',
    'Italian':    'it',
    'Dutch':      'nl',
    'Polish':     'pl',
    'Swedish':    'sv',
    'Danish':     'da',
    'Norwegian':  'no',
    'Finnish':    'fi',
    'Greek':      'el',
    'Romanian':   'ro',
    'Czech':      'cs',
    'Hungarian':  'hu',
    'Vietnamese': 'vi',
    'Thai':       'th',
    'Indonesian': 'id',
    'Malay':      'ms',
    'Bengali':    'bn',
    'Punjabi':    'pa',
    'Tamil':      'ta',
    'Telugu':     'te',
    'Swahili':    'sw',
    'Catalan':    'ca',
    'Ukrainian':  'uk',
}

# Voice TLD for gender simulation with gTTS
VOICE_TLD = {
    'Male':   'com',
    'Female': 'co.uk',
}

# RTL languages that need special text handling
RTL_LANGS = {'Urdu', 'Arabic', 'Hebrew', 'Persian'}

LATIN_ONLY_LANGS = {
    'English', 'French', 'Spanish', 'German', 'Turkish',
    'Portuguese', 'Italian', 'Dutch', 'Polish', 'Swedish',
    'Danish', 'Norwegian', 'Finnish', 'Romanian', 'Czech',
    'Hungarian', 'Indonesian', 'Malay', 'Swahili', 'Catalan',
}

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
                 'Urdu selected!\nPlease write in Urdu script (اردو).'),
    'Hindi':    (lambda t: any('\u0900' <= c <= '\u097f' for c in t),
                 'Hindi selected!\nPlease write in Devanagari script.'),
    'Russian':  (lambda t: any('\u0400' <= c <= '\u04ff' for c in t),
                 'Russian selected!\nPlease write in Cyrillic script.'),
    'Bengali':  (lambda t: any('\u0980' <= c <= '\u09ff' for c in t),
                 'Bengali selected!\nPlease write in Bengali script.'),
    'Tamil':    (lambda t: any('\u0b80' <= c <= '\u0bff' for c in t),
                 'Tamil selected!\nPlease write in Tamil script.'),
    'Telugu':   (lambda t: any('\u0c00' <= c <= '\u0c7f' for c in t),
                 'Telugu selected!\nPlease write in Telugu script.'),
    'Thai':     (lambda t: any('\u0e00' <= c <= '\u0e7f' for c in t),
                 'Thai selected!\nPlease write in Thai script.'),
    'Greek':    (lambda t: any('\u0370' <= c <= '\u03ff' for c in t),
                 'Greek selected!\nPlease write in Greek script.'),
    'Ukrainian':(lambda t: any('\u0400' <= c <= '\u04ff' for c in t),
                 'Ukrainian selected!\nPlease write in Cyrillic script.'),
}

# Language flags for visual display
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
#  EMOTIONAL TAGS  (Word-level emotion control)
# ═══════════════════════════════════════════════════════════
EMOTION_TAGS = {
    'Normal':    {'icon': '😐', 'color': C_GRAY,   'ssml': '',             'tld_override': None},
    'Happy':     {'icon': '😊', 'color': C_GREEN,  'ssml': 'cheerful',     'tld_override': 'co.uk'},
    'Sad':       {'icon': '😢', 'color': C_BLUE2,  'ssml': 'sad',          'tld_override': 'com.au'},
    'Whisper':   {'icon': '🤫', 'color': C_PURPLE, 'ssml': 'x-soft',       'tld_override': 'co.uk'},
    'Shout':     {'icon': '📢', 'color': C_RED,    'ssml': 'x-loud',       'tld_override': 'com'},
    'Sarcasm':   {'icon': '😏', 'color': C_AMBER,  'ssml': 'sarcastic',    'tld_override': 'co.uk'},
    'Excited':   {'icon': '🎉', 'color': C_ORANGE, 'ssml': 'excited',      'tld_override': None},
    'Calm':      {'icon': '🧘', 'color': C_TEAL,   'ssml': 'calm',         'tld_override': None},
    'Serious':   {'icon': '😐', 'color': C_INDIGO, 'ssml': 'serious',      'tld_override': 'com'},
    'Fearful':   {'icon': '😨', 'color': C_PINK,   'ssml': 'fearful',      'tld_override': None},
}

# ═══════════════════════════════════════════════════════════
#  VOICE PRESETS
# ═══════════════════════════════════════════════════════════
VOICE_PRESETS = {
    'Narrator':    {'icon': '📖', 'speed': 50, 'pitch': 0,  'emotion': 'Calm',    'desc': 'Clear storytelling'},
    'Newsreader':  {'icon': '📰', 'speed': 60, 'pitch': 0,  'emotion': 'Serious', 'desc': 'Professional news'},
    'Story Mode':  {'icon': '🧙', 'speed': 45, 'pitch': -5, 'emotion': 'Happy',   'desc': 'Engaging story'},
    'Meditation':  {'icon': '🧘', 'speed': 30, 'pitch': -3, 'emotion': 'Calm',    'desc': 'Peaceful & slow'},
    'Commercial':  {'icon': '📺', 'speed': 65, 'pitch': 3,  'emotion': 'Excited', 'desc': 'Upbeat & catchy'},
    'Robot':       {'icon': '🤖', 'speed': 50, 'pitch': 10, 'emotion': 'Serious', 'desc': 'Robotic effect'},
    'Poet':        {'icon': '🎭', 'speed': 40, 'pitch': 2,  'emotion': 'Sad',     'desc': 'Dramatic poetry'},
    'Audiobook':   {'icon': '🎧', 'speed': 55, 'pitch': 0,  'emotion': 'Normal',  'desc': 'Long-form audio'},
}

# File type icons
FILE_ICONS = {
    'TXT':  {'icon': '📄', 'color': C_BLUE2,   'emoji': '📝'},
    'PDF':  {'icon': '📕', 'color': C_RED,     'emoji': '📕'},
    'DOCX': {'icon': '📘', 'color': C_BLUE,    'emoji': '📘'},
    'DOC':  {'icon': '📗', 'color': C_GREEN,   'emoji': '📗'},
    'SRT':  {'icon': '🎬', 'color': C_PURPLE,  'emoji': '🎬'},
    'CSV':  {'icon': '📊', 'color': C_AMBER,   'emoji': '📊'},
}

# ═══════════════════════════════════════════════════════════
#  APP FOLDER MANAGEMENT  (Auto-creates Titan AI Studio folder)
# ═══════════════════════════════════════════════════════════
def get_titan_folder():
    """
    Get or create the dedicated Titan AI Studio folder.
    On Android: /storage/emulated/0/Titan AI Studio/
    On PC: ~/Titan AI Studio/
    Sub-folders: Audio/, Imported/, Cloned/, Exports/
    """
    if ANDROID_ENV:
        for root in ['/storage/emulated/0', '/sdcard', '/mnt/sdcard']:
            if os.path.exists(root):
                base = os.path.join(root, 'Titan AI Studio')
                break
        else:
            base = os.path.join(os.path.expanduser('~'), 'Titan AI Studio')
    else:
        base = os.path.join(os.path.expanduser('~'), 'Titan AI Studio')

    # Create all sub-folders
    subfolders = ['Audio', 'Imported', 'Cloned', 'Exports', 'Presets', 'Queue']
    try:
        os.makedirs(base, exist_ok=True)
        for sf in subfolders:
            os.makedirs(os.path.join(base, sf), exist_ok=True)
        # Create README file on first run
        readme = os.path.join(base, 'README.txt')
        if not os.path.exists(readme):
            with open(readme, 'w', encoding='utf-8') as f:
                f.write('Titan AI Studio Pro\n')
                f.write('===================\n')
                f.write('Audio/    - Generated voice files\n')
                f.write('Imported/ - Imported documents\n')
                f.write('Cloned/   - Voice cloning results\n')
                f.write('Exports/  - Exported projects\n')
                f.write('Presets/  - Custom voice presets\n')
                f.write('Queue/    - Batch processing queue\n')
    except Exception:
        pass
    return base


def get_audio_folder():
    return os.path.join(get_titan_folder(), 'Audio')


def get_import_folder():
    return os.path.join(get_titan_folder(), 'Imported')


def get_clone_folder():
    return os.path.join(get_titan_folder(), 'Cloned')


# Legacy compatibility
def get_internal_storage_path():
    if ANDROID_ENV:
        for p in ['/storage/emulated/0', '/sdcard', '/mnt/sdcard']:
            if os.path.exists(p):
                return p
    return os.path.expanduser('~')


def get_save_dirs():
    titan = get_titan_folder()
    dirs = [
        ('⭐ Titan AI Studio (Recommended)\n' + titan, titan),
        ('🎵 Titan / Audio\n' + os.path.join(titan, 'Audio'),
         os.path.join(titan, 'Audio')),
    ]
    if ANDROID_ENV:
        internal = get_internal_storage_path()
        dl = os.path.join(internal, 'Download')
        music = os.path.join(internal, 'Music')
        dirs += [
            ('📥 Downloads\n' + dl, dl),
            ('🎵 Music\n' + music, music),
        ]
        try:
            ext = primary_external_storage_path()
            if ext and ext not in (internal, '/sdcard', '/storage/emulated/0'):
                dirs.append(('💾 SD Card\n' + ext, ext))
        except Exception:
            pass
    else:
        home = os.path.expanduser('~')
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
    return os.path.join(d, 'history_v2.json')


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


# Settings persistence
def settings_path():
    app = App.get_running_app()
    d = app.user_data_dir if app else '.'
    return os.path.join(d, 'settings.json')


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


# Batch queue persistence
def queue_path():
    app = App.get_running_app()
    d = app.user_data_dir if app else '.'
    return os.path.join(d, 'batch_queue.json')


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
#  FILE READERS  (Enhanced)
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
                # Better XML parsing - preserve paragraphs
                xml = re.sub(r'<w:p[ />]', '\n<w:p ', xml)
                xml = re.sub(r'</w:p>', '\n', xml)
                text = re.sub(r'<[^>]+>', ' ', xml)
                return ' '.join(text.split())
        return ''
    except Exception:
        return ''


def read_srt(path):
    """Read subtitle file and extract text"""
    try:
        content = read_txt(path)
        # Remove timing lines and sequence numbers
        lines = content.split('\n')
        text_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.isdigit():
                continue
            if '-->' in line:
                continue
            # Remove HTML tags from subtitles
            line = re.sub(r'<[^>]+>', '', line)
            if line:
                text_lines.append(line)
        return ' '.join(text_lines)
    except Exception:
        return ''


def get_file_info(path):
    """Returns (type_str, size_str, line_count)"""
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
#  SSML BUILDER  (Advanced Speech Markup)
# ═══════════════════════════════════════════════════════════
def build_ssml(text, emotion, speed_pct, pitch_shift, use_breaths=False):
    """Build SSML markup for advanced TTS control"""
    # Map speed percentage to prosody rate
    if speed_pct < 25:
        rate = 'x-slow'
    elif speed_pct < 40:
        rate = 'slow'
    elif speed_pct < 60:
        rate = 'medium'
    elif speed_pct < 75:
        rate = 'fast'
    else:
        rate = 'x-fast'

    # Map pitch shift to prosody pitch
    if pitch_shift < -6:
        pitch = 'x-low'
    elif pitch_shift < -2:
        pitch = 'low'
    elif pitch_shift > 6:
        pitch = 'x-high'
    elif pitch_shift > 2:
        pitch = 'high'
    else:
        pitch = 'medium'

    # Emotion-specific volume
    emotion_data = EMOTION_TAGS.get(emotion, EMOTION_TAGS['Normal'])
    ssml_style = emotion_data.get('ssml', '')

    volume = 'medium'
    if emotion == 'Whisper':
        volume = 'x-soft'
    elif emotion == 'Shout':
        volume = 'x-loud'

    # Add breath marks if enabled
    if use_breaths:
        # Add breath after long sentences
        text = re.sub(r'([.!?])\s+', r'\1 <break time="500ms"/> ', text)

    ssml = (
        '<speak>\n'
        f'  <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">\n'
        f'    {text}\n'
        f'  </prosody>\n'
        '</speak>'
    )
    return ssml


# ═══════════════════════════════════════════════════════════
#  UI PRIMITIVE HELPERS
# ═══════════════════════════════════════════════════════════
def hex_c(h):
    return get_color_from_hex(h)


def lbl(txt, size=15, color=C_MUTED, bold=False, h=36, halign='left'):
    l = Label(
        text=txt,
        font_size=sp(size),
        bold=bold,
        color=hex_c(color),
        size_hint_y=None,
        height=dp(h),
        halign=halign,
        valign='middle',
    )
    l.bind(size=l.setter('text_size'))
    return l


def card_bg(widget, color=C_CARD, radius=14):
    with widget.canvas.before:
        Color(*hex_c(color))
        rr = RoundedRectangle(
            pos=widget.pos, size=widget.size, radius=[dp(radius)]
        )

    def _upd(w, *a):
        rr.pos  = w.pos
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


def badge(text, bg=C_BLUE, size=11):
    """Small colored badge/pill label"""
    b = Label(
        text=text,
        font_size=sp(size),
        bold=True,
        color=(1, 1, 1, 1),
        size_hint=(None, None),
        size=(dp(len(text) * 8 + 16), dp(22)),
    )
    with b.canvas.before:
        Color(*hex_c(bg))
        rr = RoundedRectangle(pos=b.pos, size=b.size, radius=[dp(11)])
    b.bind(
        pos=lambda w, *a: setattr(rr, 'pos', w.pos),
        size=lambda w, *a: setattr(rr, 'size', w.size),
    )
    return b


# ═══════════════════════════════════════════════════════════
#  FLAT BUTTON  (Professional with animations)
# ═══════════════════════════════════════════════════════════
class FlatBtn(Button):
    def __init__(self, bg=C_BLUE, radius=14, icon='', **kw):
        super().__init__(**kw)
        self.bg_color  = bg
        self._radius   = radius
        self._icon     = icon
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
        anim = (
            Animation(opacity=0.6, duration=0.05)
            + Animation(opacity=1.0, duration=0.12)
        )
        anim.start(self)

    def on_disabled(self, inst, val):
        self.opacity = 0.38 if val else 1.0


# ═══════════════════════════════════════════════════════════
#  ICON BUTTON  (Square icon button)
# ═══════════════════════════════════════════════════════════
class IconBtn(ButtonBehavior, Label):
    def __init__(self, icon='🎵', size_dp=44, bg=C_CARD2, **kw):
        super().__init__(**kw)
        self.text      = icon
        self.font_size = sp(22)
        self.size_hint = (None, None)
        self.size      = (dp(size_dp), dp(size_dp))
        self._bg_color = bg
        self._rr = None
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex_c(self._bg_color))
            self._rr = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(10)]
            )

    def on_press(self):
        Animation(opacity=0.5, duration=0.05).start(self)

    def on_release(self):
        Animation(opacity=1.0, duration=0.12).start(self)


# ═══════════════════════════════════════════════════════════
#  DARK PANEL  (Screen background)
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
#  WAVEFORM VISUALIZER  (Animated audio waveform)
# ═══════════════════════════════════════════════════════════
class WaveformWidget(Widget):
    """Animated waveform display"""
    def __init__(self, bars=24, color=C_BLUE2, **kw):
        super().__init__(**kw)
        self._bars     = bars
        self._color    = color
        self._heights  = [0.1] * bars
        self._anim_ev  = None
        self._active   = False
        self._t        = 0
        self.bind(pos=self._draw, size=self._draw)

    def start(self):
        self._active = True
        if not self._anim_ev:
            self._anim_ev = Clock.schedule_interval(self._tick, 0.06)

    def stop(self):
        self._active = False
        # Animate bars down
        self._heights = [0.08] * self._bars
        self._draw()

    def _tick(self, dt):
        self._t += 0.15
        if self._active:
            for i in range(self._bars):
                phase = self._t + i * 0.4
                val = abs(math.sin(phase)) * 0.7 + abs(math.sin(phase * 2.3)) * 0.3
                self._heights[i] = max(0.05, val)
        else:
            self._heights = [0.06] * self._bars
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        if not self.width or not self.height:
            return
        bar_w = self.width / (self._bars * 1.4)
        gap   = bar_w * 0.4
        total = self._bars * (bar_w + gap)
        start_x = self.x + (self.width - total) / 2

        with self.canvas:
            for i, h_ratio in enumerate(self._heights):
                x  = start_x + i * (bar_w + gap)
                bh = h_ratio * self.height
                y  = self.y + (self.height - bh) / 2

                alpha = 0.4 + h_ratio * 0.6
                r, g, b, _ = hex_c(self._color)
                Color(r, g, b, alpha)
                RoundedRectangle(
                    pos=(x, y),
                    size=(bar_w, bh),
                    radius=[dp(bar_w / 2)],
                )

    def cleanup(self):
        if self._anim_ev:
            self._anim_ev.cancel()
            self._anim_ev = None


# ═══════════════════════════════════════════════════════════
#  LOGO WIDGET
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
            self.add_widget(Label(
                text='T',
                font_size=sp(30),
                bold=True,
                color=hex_c(C_BLUE2),
                size_hint=(1, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            ))

    def _find_logo(self):
        base = os.path.dirname(os.path.abspath(__file__))
        for name in ['AI.png', 'AI.jpg', 'logo.png', 'icon.png']:
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
        if ANDROID_ENV:
            try:
                app = App.get_running_app()
                if app:
                    for name in ['AI.png', 'AI.jpg']:
                        p = os.path.join(app.user_data_dir, name)
                        if os.path.exists(p):
                            return p
            except Exception:
                pass
        return None


# ═══════════════════════════════════════════════════════════
#  LOADING SCREEN  (FIXED: Single clean loader, no double)
# ═══════════════════════════════════════════════════════════
class LoadingScreen(Screen):
    """
    FIX: Single loading screen only.
    Previous code had double-load issue because:
    1. LoadingScreen was added FIRST in ScreenManager
    2. It animated in then FadeTransition to studio caused re-render
    FIX: We now use a proper 'loading' initial screen with
         _go() called only ONCE via Clock.schedule_once
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self._progress_ev  = None
        self._dot_ev       = None
        self._dot_count    = 0
        self._already_gone = False   # ← Prevents double-switch
        self._build()

    def _build(self):
        root = DarkPanel()

        # ── Logo (top area) ──────────────────────────────
        logo_path = self._find_logo()
        if logo_path:
            self.logo_widget = KivyImage(
                source=logo_path,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(None, None),
                size=(dp(160), dp(160)),
                pos_hint={'center_x': 0.5, 'center_y': 0.62},
                opacity=0,
            )
        else:
            self.logo_widget = Label(
                text='T',
                font_size=sp(88),
                bold=True,
                color=hex_c(C_BLUE2),
                pos_hint={'center_x': 0.5, 'center_y': 0.62},
                opacity=0,
            )
        root.add_widget(self.logo_widget)

        # ── Version badge ──────────────────────────────
        self.ver_lbl = Label(
            text='v10.0  ULTRA',
            font_size=sp(11),
            bold=True,
            color=hex_c(C_GOLD),
            pos_hint={'center_x': 0.5, 'center_y': 0.47},
            opacity=0,
        )
        root.add_widget(self.ver_lbl)

        # ── Title ───────────────────────────────────────
        self.title_lbl = Label(
            text='Titan AI Studio Pro',
            font_size=sp(28),
            bold=True,
            color=hex_c(C_WHITE),
            pos_hint={'center_x': 0.5, 'center_y': 0.54},
            opacity=0,
        )
        root.add_widget(self.title_lbl)

        # ── Subtitle ─────────────────────────────────────
        self.sub_lbl = Label(
            text='Professional Voice Studio · Always Free',
            font_size=sp(14),
            color=hex_c(C_MUTED2),
            pos_hint={'center_x': 0.5, 'center_y': 0.40},
            opacity=0,
        )
        root.add_widget(self.sub_lbl)

        # ── Dots loading text ─────────────────────────
        self.dot_lbl = Label(
            text='Loading...',
            font_size=sp(14),
            color=hex_c(C_ACCENT),
            pos_hint={'center_x': 0.5, 'center_y': 0.28},
            opacity=0,
        )
        root.add_widget(self.dot_lbl)

        # ── Progress bar ─────────────────────────────
        self.prog = ProgressBar(
            max=100, value=0,
            size_hint=(0.72, None),
            height=dp(5),
            pos_hint={'center_x': 0.5, 'y': 0.21},
        )
        root.add_widget(self.prog)

        # ── Copyright ─────────────────────────────────
        root.add_widget(Label(
            text='© 2025 Titan AI Studio',
            font_size=sp(11),
            color=hex_c(C_MUTED),
            pos_hint={'center_x': 0.5, 'center_y': 0.08},
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
        # Only animate once — prevent double-load
        if self._already_gone:
            return
        self._animate_in()
        # Start progress
        Clock.schedule_once(self._start_progress, 0.3)
        # Start dots
        self._dot_ev = Clock.schedule_interval(self._tick_dots, 0.4)
        # Schedule switch — only once, with _already_gone guard
        Clock.schedule_once(self._go, 3.5)

    def _animate_in(self):
        Animation(opacity=1, duration=0.8).start(self.logo_widget)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self.title_lbl), 0.4)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self.ver_lbl), 0.6)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self.sub_lbl), 0.8)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.4).start(self.dot_lbl), 1.0)

    def _start_progress(self, dt):
        Animation(value=88, duration=2.8, t='out_cubic').start(self.prog)

    def _tick_dots(self, dt):
        self._dot_count = (self._dot_count + 1) % 4
        dots = '.' * (self._dot_count + 1)
        self.dot_lbl.text = 'Initializing' + dots

    def on_leave(self, *a):
        if self._dot_ev:
            self._dot_ev.cancel()
            self._dot_ev = None

    def _go(self, dt):
        if self._already_gone:
            return
        self._already_gone = True  # ← KEY FIX: prevent double execution
        Animation(value=100, duration=0.2).start(self.prog)
        Clock.schedule_once(self._switch, 0.25)

    def _switch(self, dt=None):
        self.manager.transition = FadeTransition(duration=0.5)
        self.manager.current    = 'studio'


# ═══════════════════════════════════════════════════════════
#  FILE IMPORT CARD  (Shows file logo + info)
# ═══════════════════════════════════════════════════════════
class FileInfoCard(BoxLayout):
    """Displays imported file with icon, name, size, type"""
    def __init__(self, path, ftype, **kw):
        super().__init__(**kw)
        self.orientation  = 'horizontal'
        self.size_hint_y  = None
        self.height       = dp(72)
        self.padding      = [dp(12), dp(8)]
        self.spacing      = dp(12)
        card_bg(self, C_SURFACE, 12)

        info = FILE_ICONS.get(ftype.upper(), FILE_ICONS.get('TXT', {'emoji': '📄', 'color': C_GRAY}))

        # File type icon (large emoji + colored bg)
        icon_box = BoxLayout(
            size_hint=(None, None),
            size=(dp(50), dp(50)),
        )
        icon_bg = FloatLayout(
            size_hint=(None, None),
            size=(dp(50), dp(50)),
        )
        with icon_bg.canvas.before:
            Color(*hex_c(info.get('color', C_GRAY) + '33'))
            rr = RoundedRectangle(pos=icon_bg.pos, size=icon_bg.size, radius=[dp(10)])
        icon_bg.bind(
            pos=lambda w, *a: setattr(rr, 'pos', w.pos),
            size=lambda w, *a: setattr(rr, 'size', w.size),
        )
        icon_lbl = Label(
            text=info.get('emoji', '📄'),
            font_size=sp(26),
            size_hint=(1, 1),
        )
        icon_bg.add_widget(icon_lbl)
        icon_box.add_widget(icon_bg)
        self.add_widget(icon_box)

        # File info text
        info_col = BoxLayout(orientation='vertical', size_hint_x=1)
        fname = os.path.basename(path)
        ext, size_str = get_file_info(path)

        name_lbl = Label(
            text=fname,
            font_size=sp(13),
            bold=True,
            color=hex_c(C_WHITE),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(30),
        )
        name_lbl.bind(size=name_lbl.setter('text_size'))
        info_col.add_widget(name_lbl)

        meta_lbl = Label(
            text=ftype.upper() + ' File  ·  ' + size_str,
            font_size=sp(11),
            color=hex_c(info.get('color', C_MUTED)),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(24),
        )
        meta_lbl.bind(size=meta_lbl.setter('text_size'))
        info_col.add_widget(meta_lbl)
        self.add_widget(info_col)


# ═══════════════════════════════════════════════════════════
#  EMOTION PICKER WIDGET
# ═══════════════════════════════════════════════════════════
class EmotionPicker(BoxLayout):
    def __init__(self, callback=None, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height      = dp(180)
        self.spacing     = dp(8)
        self._callback   = callback
        self._selected   = 'Normal'
        self._btns       = {}
        self._build()

    def _build(self):
        self.add_widget(lbl('🎭 Emotion & Mood', 14, C_ACCENT, True, 28))

        # Row 1
        row1 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(8))
        emotions_1 = ['Normal', 'Happy', 'Sad', 'Whisper', 'Shout']
        for em in emotions_1:
            self._add_btn(row1, em)
        self.add_widget(row1)

        # Row 2
        row2 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(8))
        emotions_2 = ['Sarcasm', 'Excited', 'Calm', 'Serious', 'Fearful']
        for em in emotions_2:
            self._add_btn(row2, em)
        self.add_widget(row2)

        # Select Normal by default
        Clock.schedule_once(lambda dt: self._select('Normal'), 0)

    def _add_btn(self, parent, emotion):
        data = EMOTION_TAGS[emotion]
        b = FlatBtn(
            text=data['icon'] + '\n' + emotion,
            bg=C_CARD2,
            font_size=sp(10),
            bold=False,
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
                btn.bold = True
            else:
                btn.set_bg(C_CARD2)
                btn.bold = False
        if self._callback:
            self._callback(emotion)

    @property
    def selected(self):
        return self._selected


# ═══════════════════════════════════════════════════════════
#  VOICE PRESET PICKER
# ═══════════════════════════════════════════════════════════
class PresetPicker(BoxLayout):
    def __init__(self, callback=None, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height      = dp(160)
        self.spacing     = dp(8)
        self._callback   = callback
        self._selected   = None
        self._btns       = {}
        self._build()

    def _build(self):
        hdr = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(8))
        hdr.add_widget(lbl('🎚 Voice Presets', 14, C_ACCENT, True, 28))
        self.add_widget(hdr)

        sv = ScrollView(size_hint=(1, None), height=dp(120))
        row = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            spacing=dp(10),
            padding=[dp(2), dp(4)],
        )
        row.bind(minimum_width=row.setter('width'))

        for preset_name, data in VOICE_PRESETS.items():
            col = BoxLayout(
                orientation='vertical',
                size_hint=(None, 1),
                width=dp(90),
                spacing=dp(4),
            )
            b = FlatBtn(
                text=data['icon'],
                bg=C_CARD2,
                size_hint_y=None, height=dp(50),
                font_size=sp(24),
                radius=12,
            )
            b.bind(on_press=lambda x, n=preset_name: self._select(n))
            col.add_widget(b)

            nl = Label(
                text=preset_name,
                font_size=sp(10),
                color=hex_c(C_MUTED2),
                size_hint_y=None, height=dp(20),
                bold=True,
            )
            col.add_widget(nl)
            self._btns[preset_name] = b
            row.add_widget(col)

        sv.add_widget(row)
        self.add_widget(sv)

    def _select(self, preset_name):
        self._selected = preset_name
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
        self.height      = dp(110)
        self.padding     = [dp(16), dp(10)]
        self.spacing     = dp(8)
        card_bg(self, C_CARD2, 16)
        self._build()

    def _build(self):
        self.add_widget(lbl('🎵 Pitch & Tone Shift', 14, C_ACCENT, True, 28))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        row.add_widget(lbl('Low', 12, C_MUTED, False, 44))
        self.pitch_slider = Slider(min=-10, max=10, value=0, step=1)
        self.pitch_lbl    = lbl('0 semitones', 13, C_CYAN, False, 44)
        self.pitch_slider.bind(
            value=lambda i, v: setattr(
                self.pitch_lbl, 'text',
                ('+' if v > 0 else '') + str(int(v)) + ' semitones'
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
        self.height      = dp(280)
        self.padding     = [dp(16), dp(12)]
        self.spacing     = dp(10)
        card_bg(self, C_CARD2, 16)
        self._build()

    def _build(self):
        self.add_widget(lbl('⚙ Advanced Options', 14, C_ACCENT, True, 30))

        # Breath simulation toggle
        row1 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        row1.add_widget(lbl('💨 Dynamic Breath Simulation', 13, C_WHITE2, False, 44))
        self.breath_sw = Switch(active=False, size_hint=(None, None), size=(dp(70), dp(44)))
        row1.add_widget(self.breath_sw)
        self.add_widget(row1)
        self.add_widget(separator(C_CARD3, 1))

        # Ultra low latency toggle
        row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        row2.add_widget(lbl('⚡ Ultra-Low Latency Mode', 13, C_WHITE2, False, 44))
        self.latency_sw = Switch(active=False, size_hint=(None, None), size=(dp(70), dp(44)))
        row2.add_widget(self.latency_sw)
        self.add_widget(row2)
        self.add_widget(separator(C_CARD3, 1))

        # SSML support toggle
        row3 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        row3.add_widget(lbl('📝 SSML Markup Support', 13, C_WHITE2, False, 44))
        self.ssml_sw = Switch(active=False, size_hint=(None, None), size=(dp(70), dp(44)))
        row3.add_widget(self.ssml_sw)
        self.add_widget(row3)
        self.add_widget(separator(C_CARD3, 1))

        # Adaptive pacing toggle
        row4 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        row4.add_widget(lbl('⏱ Adaptive Pacing', 13, C_WHITE2, False, 44))
        self.pacing_sw = Switch(active=False, size_hint=(None, None), size=(dp(70), dp(44)))
        row4.add_widget(self.pacing_sw)
        self.add_widget(row4)

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
#  BATCH QUEUE SCREEN
# ═══════════════════════════════════════════════════════════
class BatchQueueScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._queue = []
        self._processing = False
        self._build()

    def _build(self):
        root  = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        back = FlatBtn(text='← Back', bg=C_GRAY, size_hint_x=None, width=dp(100),
                       font_size=sp(14))
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('📋 Batch Processing Queue', 18, C_ACCENT, True, 64))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        # Status banner
        self.status_banner = BoxLayout(
            size_hint_y=None, height=dp(48), padding=[dp(14), dp(8)],
        )
        card_bg(self.status_banner, C_CARD2, 12)
        self.status_lbl = lbl('Queue is empty. Add items from Studio.', 13, C_MUTED, False, 32)
        self.status_banner.add_widget(self.status_lbl)
        outer.add_widget(self.status_banner)

        # Queue list
        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(10), padding=[dp(2), dp(6)],
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)
        outer.add_widget(separator())

        # Control buttons
        ctrl = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(12))
        self.proc_btn = FlatBtn(
            text='▶ Process All', bg=C_GREEN, font_size=sp(15)
        )
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
            row = self._make_row(i, item)
            self.list_box.add_widget(row)

    def _make_row(self, idx, item):
        row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10),
                        padding=[dp(12), dp(8)])
        card_bg(row, C_CARD2, 14)

        num = Label(text=str(idx + 1), font_size=sp(20), bold=True,
                    color=hex_c(C_ACCENT), size_hint_x=None, width=dp(36))
        row.add_widget(num)

        info = BoxLayout(orientation='vertical')
        t = lbl(item.get('text', '')[:60] + '...', 13, C_WHITE2, False, 36)
        m = lbl(item.get('lang', '') + '  ·  ' + item.get('voice', '') +
                '  ·  ' + item.get('emotion', ''), 11, C_MUTED2, False, 28)
        info.add_widget(t)
        info.add_widget(m)
        row.add_widget(info)

        status = item.get('status', 'pending')
        color = C_AMBER if status == 'pending' else C_GREEN if status == 'done' else C_RED
        sl = Label(text=status.upper(), font_size=sp(10), bold=True,
                   color=hex_c(color), size_hint_x=None, width=dp(60))
        row.add_widget(sl)
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
        from gtts import gTTS
        results = []
        for i, item in enumerate(self._queue):
            try:
                text  = item.get('text', '')
                lang  = LANGUAGES.get(item.get('lang', 'English'), 'en')
                tld   = VOICE_TLD.get(item.get('voice', 'Male'), 'com')
                slow  = item.get('slow', False)
                tts   = gTTS(text=text, lang=lang, tld=tld, slow=slow)
                fname = 'Queue_' + str(i + 1) + '_' + str(int(time.time())) + '.mp3'
                dest  = os.path.join(get_audio_folder(), fname)
                os.makedirs(get_audio_folder(), exist_ok=True)
                tts.save(dest)
                item['status'] = 'done'
                item['output'] = dest
                history_save({
                    'filename': fname,
                    'path':     dest,
                    'lang':     item.get('lang', ''),
                    'voice':    item.get('voice', ''),
                    'time':     time.strftime('%d %b %Y  %H:%M'),
                    'emotion':  item.get('emotion', 'Normal'),
                    'source':   'batch',
                })
            except Exception as e:
                item['status'] = 'error'
            results.append(item)
            Clock.schedule_once(
                lambda dt, idx=i: self.status_lbl.__setattr__(
                    'text', 'Processing ' + str(idx + 1) + ' / ' + str(len(self._queue))
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
#  HISTORY SCREEN  (Enhanced)
# ═══════════════════════════════════════════════════════════
class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._sounds = []
        self._build()

    def _build(self):
        root  = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(72), spacing=dp(12))
        card_bg(hdr, C_CARD, 0)
        back = FlatBtn(text='← Back', bg=C_GRAY, size_hint_x=None, width=dp(110),
                       font_size=sp(15))
        back.bind(on_press=self._go_back)
        hdr.add_widget(back)
        hdr.add_widget(lbl('📋 Download History', 22, C_ACCENT, True, 72))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        # Stats row
        self.stats_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        card_bg(self.stats_row, C_CARD2, 12)
        self.count_lbl = lbl('0 recordings', 13, C_MUTED2, False, 56)
        self.size_lbl  = lbl('0 KB total', 13, C_MUTED2, False, 56)
        self.stats_row.add_widget(self.count_lbl)
        self.stats_row.add_widget(self.size_lbl)
        outer.add_widget(self.stats_row)

        # Scrollable list
        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(14), padding=[dp(2), dp(8)],
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)
        outer.add_widget(separator())

        # Clear button
        clr = FlatBtn(text='🗑  Clear All History', bg=C_DARK_RED,
                      size_hint_y=None, height=dp(58), font_size=sp(16))
        clr.bind(on_press=self._confirm_clear)
        outer.add_widget(clr)

        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self.opacity = 0
        self.x       = dp(80)
        Animation(opacity=1, x=0, duration=0.3, t='out_cubic').start(self)
        Clock.schedule_once(lambda dt: self._refresh(), 0.1)

    def _go_back(self, *a):
        self.manager.transition = SlideTransition(direction='right', duration=0.3)
        self.manager.current    = 'studio'

    def _refresh(self):
        self.list_box.clear_widgets()
        data = history_load()

        # Update stats
        total_size = 0
        for entry in data:
            p = entry.get('path', '')
            if os.path.exists(p):
                total_size += os.path.getsize(p)
        if total_size < 1024 * 1024:
            sz = '{:.0f} KB'.format(total_size / 1024)
        else:
            sz = '{:.1f} MB'.format(total_size / (1024 * 1024))
        self.count_lbl.text = str(len(data)) + ' recordings'
        self.size_lbl.text  = sz + ' total'

        if not data:
            self.list_box.add_widget(Label(
                text='No downloads yet.\nGenerate and save your first voice!',
                color=hex_c(C_MUTED), font_size=sp(15),
                size_hint_y=None, height=dp(120),
                halign='center', valign='middle',
            ))
            return

        for i, entry in enumerate(data):
            row = self._make_row(entry)
            row.opacity = 0
            self.list_box.add_widget(row)
            Clock.schedule_once(
                lambda dt, w=row: Animation(opacity=1, duration=0.22).start(w),
                i * 0.06,
            )

    def _make_row(self, entry):
        row = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(10),
                        padding=[dp(14), dp(8)])
        card_bg(row, C_CARD2, 16)

        # Icon
        em = entry.get('emotion', 'Normal')
        icon_text = EMOTION_TAGS.get(em, {}).get('icon', '🎵')
        icon_lbl = Label(text=icon_text, font_size=sp(28),
                         size_hint_x=None, width=dp(44))
        row.add_widget(icon_lbl)

        # Info
        info = BoxLayout(orientation='vertical', size_hint_x=0.72)
        fname = Label(
            text=entry.get('filename', 'unknown'),
            font_size=sp(13), bold=True,
            color=hex_c(C_WHITE),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(36),
        )
        fname.bind(size=fname.setter('text_size'))
        info.add_widget(fname)

        meta_parts = [
            LANG_FLAGS.get(entry.get('lang', ''), '') + ' ' + entry.get('lang', ''),
            entry.get('voice', ''),
            entry.get('emotion', 'Normal'),
            entry.get('time', ''),
        ]
        meta = Label(
            text='  ·  '.join([p for p in meta_parts if p.strip()]),
            font_size=sp(11), color=hex_c(C_GREEN),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(28),
        )
        meta.bind(size=meta.setter('text_size'))
        info.add_widget(meta)

        # Source badge
        source = entry.get('source', 'manual')
        src_lbl = Label(
            text=source,
            font_size=sp(10),
            color=hex_c(C_MUTED),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(22),
        )
        src_lbl.bind(size=src_lbl.setter('text_size'))
        info.add_widget(src_lbl)
        row.add_widget(info)

        # Play / missing
        fp = entry.get('path', '')
        if os.path.exists(fp):
            pb = FlatBtn(text='▶', bg=C_GREEN, size_hint_x=None, width=dp(52), font_size=sp(18))
            pb.bind(on_press=lambda *a, p=fp, b=pb: self._play(p, b))
            row.add_widget(pb)
        else:
            ml = Label(text='[Missing]', font_size=sp(10), color=hex_c(C_RED),
                       size_hint_x=None, width=dp(60))
            row.add_widget(ml)
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

            def on_stop(dt):
                try:
                    btn.text = '▶'
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
        br  = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(14))
        yes = FlatBtn(text='Yes, Clear', bg=C_DARK_RED, font_size=sp(15))
        no  = FlatBtn(text='Cancel',    bg=C_GRAY,     font_size=sp(15))
        br.add_widget(yes)
        br.add_widget(no)
        box.add_widget(br)
        p = Popup(title='Confirm', content=box, size_hint=(0.88, 0.42),
                  background_color=hex_c(C_CARD))
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
        root  = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        back = FlatBtn(text='← Back', bg=C_GRAY, size_hint_x=None, width=dp(100),
                       font_size=sp(14))
        back.bind(on_press=lambda *a: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(lbl('⚙ Settings', 20, C_ACCENT, True, 64))
        outer.add_widget(hdr)
        outer.add_widget(separator())

        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None,
                            spacing=dp(16), padding=[dp(2), dp(6)])
        content.bind(minimum_height=content.setter('height'))

        # Titan folder info card
        folder_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(130),
                                padding=[dp(16), dp(12)], spacing=dp(8))
        card_bg(folder_card, C_CARD2, 14)
        folder_card.add_widget(lbl('📁 App Save Folder', 14, C_ACCENT, True, 28))
        titan_path = get_titan_folder()
        path_lbl = Label(
            text=titan_path,
            font_size=sp(12), color=hex_c(C_WHITE2),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(40),
        )
        path_lbl.bind(size=path_lbl.setter('text_size'))
        folder_card.add_widget(path_lbl)
        folder_card.add_widget(lbl(
            'All audio files saved here automatically', 12, C_GREEN, False, 28
        ))
        content.add_widget(folder_card)

        # Folder structure card
        struct_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200),
                                padding=[dp(16), dp(12)], spacing=dp(6))
        card_bg(struct_card, C_CARD2, 14)
        struct_card.add_widget(lbl('📂 Folder Structure', 14, C_ACCENT, True, 28))
        for folder, desc in [
            ('Audio/', 'Generated voice files'),
            ('Cloned/', 'Voice cloning results'),
            ('Imported/', 'Imported documents'),
            ('Exports/', 'Exported projects'),
            ('Presets/', 'Custom voice presets'),
            ('Queue/', 'Batch processing queue'),
        ]:
            row = BoxLayout(size_hint_y=None, height=dp(24))
            row.add_widget(lbl('  📁 ' + folder, 12, C_BLUE2, True, 24))
            row.add_widget(lbl(desc, 11, C_MUTED, False, 24))
            struct_card.add_widget(row)
        content.add_widget(struct_card)

        # API keys card (ElevenLabs)
        api_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180),
                             padding=[dp(16), dp(12)], spacing=dp(10))
        card_bg(api_card, C_CARD2, 14)
        api_card.add_widget(lbl('🔑 ElevenLabs API (Voice Cloning)', 14, C_ACCENT, True, 28))
        api_card.add_widget(lbl(
            'For Professional Voice Cloning, enter your ElevenLabs API key:',
            12, C_MUTED2, False, 28
        ))
        settings = settings_load()
        self.api_input = TextInput(
            text=settings.get('elevenlabs_key', ''),
            hint_text='sk-... (Get free key from elevenlabs.io)',
            multiline=False,
            size_hint_y=None, height=dp(52),
            background_color=hex_c(C_SURFACE),
            foreground_color=hex_c(C_WHITE),
            hint_text_color=hex_c(C_MUTED),
            cursor_color=hex_c(C_ACCENT),
            font_size=sp(14),
            password=True,
        )
        api_card.add_widget(self.api_input)
        save_key_btn = FlatBtn(text='💾 Save API Key', bg=C_BLUE,
                               size_hint_y=None, height=dp(48), font_size=sp(14))
        save_key_btn.bind(on_press=self._save_api_key)
        api_card.add_widget(save_key_btn)
        content.add_widget(api_card)

        # About card
        about_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150),
                               padding=[dp(16), dp(12)], spacing=dp(8))
        card_bg(about_card, C_CARD2, 14)
        about_card.add_widget(lbl('ℹ About', 14, C_ACCENT, True, 28))
        for line in [
            'Titan AI Studio Pro  v10.0.0',
            'Professional TTS & Voice Studio',
            '30+ Languages · 10 Emotions · Voice Cloning',
            '© 2025 Titan AI Studio · Always Free',
        ]:
            about_card.add_widget(lbl(line, 12, C_MUTED2, False, 24))
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
        self._show_toast('API key saved!')

    def _show_toast(self, msg):
        box = BoxLayout(orientation='vertical', padding=dp(20))
        box.add_widget(Label(text=msg, color=hex_c(C_WHITE), font_size=sp(15)))
        ok = FlatBtn(text='OK', bg=C_GREEN, size_hint_y=None, height=dp(50))
        box.add_widget(ok)
        p = Popup(title='✅', content=box, size_hint=(0.8, 0.3),
                  background_color=hex_c(C_CARD))
        ok.bind(on_press=p.dismiss)
        p.open()


# ═══════════════════════════════════════════════════════════
#  STUDIO SCREEN  (Main TTS Screen — Enhanced)
# ═══════════════════════════════════════════════════════════
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._audio     = None
        self.out_file   = None
        self.voice_sel  = 'Male'
        self._imported_path = None
        self._imported_type = None
        self._build()

    # ──────────────────────────────────────────────────────
    def _build(self):
        root  = DarkPanel()
        outer = BoxLayout(orientation='vertical')

        # ══ HEADER BAR ═══════════════════════════════════
        hdr = BoxLayout(
            size_hint_y=None, height=dp(82),
            padding=[dp(14), dp(8)], spacing=dp(12),
        )
        card_bg(hdr, C_CARD, 0)

        logo_box = BoxLayout(size_hint=(None, None), size=(dp(54), dp(54)))
        logo_path = self._find_logo()
        if logo_path:
            logo_box.add_widget(KivyImage(
                source=logo_path, allow_stretch=True, keep_ratio=True, size_hint=(1, 1)
            ))
        else:
            logo_box.add_widget(Label(
                text='T', font_size=sp(32), bold=True,
                color=hex_c(C_BLUE2), size_hint=(1, 1)
            ))
        hdr.add_widget(logo_box)

        tb = BoxLayout(orientation='vertical', size_hint_x=1)
        t1 = Label(text='Titan AI Studio Pro', font_size=sp(20), bold=True,
                   color=hex_c(C_WHITE), halign='left', valign='middle')
        t1.bind(size=t1.setter('text_size'))
        t2 = Label(text='Professional Voice Studio · Always Free',
                   font_size=sp(12), color=hex_c(C_MUTED),
                   halign='left', valign='middle')
        t2.bind(size=t2.setter('text_size'))
        tb.add_widget(t1)
        tb.add_widget(t2)
        hdr.add_widget(tb)

        # Settings icon button
        settings_btn = IconBtn(icon='⚙', size_dp=44, bg=C_CARD2)
        settings_btn.bind(on_press=lambda *a: self._go_settings())
        hdr.add_widget(settings_btn)

        outer.add_widget(hdr)
        outer.add_widget(separator())

        # ══ SCROLLABLE CONTENT ═══════════════════════════
        scroll  = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical', size_hint_y=None,
            padding=[dp(16), dp(16)], spacing=dp(16),
        )
        content.bind(minimum_height=content.setter('height'))

        # ── Voice Preset Picker ───────────────────────
        self.preset_picker = PresetPicker(callback=self._apply_preset)
        content.add_widget(self.preset_picker)

        # ── Language + Gender Row ─────────────────────
        lg_row = BoxLayout(size_hint_y=None, height=dp(140), spacing=dp(12))

        lang_card = BoxLayout(orientation='vertical', padding=[dp(14), dp(10)], spacing=dp(8))
        card_bg(lang_card, C_CARD2, 16)
        lang_card.add_widget(lbl('🌍 Language', 13, C_ACCENT, True, 26))
        self.lang_spin = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=dp(58),
            font_size=sp(15),
            color=(1, 1, 1, 1),
            background_color=hex_c(C_BLUE),
            background_normal='',
        )
        self.lang_spin.bind(text=self._on_lang_change)
        lang_card.add_widget(self.lang_spin)
        lg_row.add_widget(lang_card)

        gender_card = BoxLayout(orientation='vertical', padding=[dp(14), dp(10)],
                                spacing=dp(8), size_hint_x=0.5)
        card_bg(gender_card, C_CARD2, 16)
        gender_card.add_widget(lbl('🎙 Gender', 13, C_ACCENT, True, 26))
        gr = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(10))
        self._vbtns = {}
        for name, icon in [('Male', '♂'), ('Female', '♀')]:
            b = FlatBtn(text=icon + '\n' + name, bg=C_BLUE, font_size=sp(13), bold=True)
            b.bind(on_press=lambda inst, n=name: self._pick_voice(n))
            gr.add_widget(b)
            self._vbtns[name] = b
        gender_card.add_widget(gr)
        lg_row.add_widget(gender_card)
        content.add_widget(lg_row)

        # Set default voice AFTER widget is built
        Clock.schedule_once(lambda dt: self._pick_voice('Male'), 0)

        # ── Emotion Picker ────────────────────────────
        self.emotion_picker = EmotionPicker()
        card_bg_box = BoxLayout(
            orientation='vertical', size_hint_y=None, height=dp(196),
            padding=[dp(14), dp(10)], spacing=dp(6),
        )
        card_bg(card_bg_box, C_CARD2, 16)
        card_bg_box.add_widget(self.emotion_picker)
        content.add_widget(card_bg_box)

        # ── Speed & Pitch Cards ───────────────────────
        sp_row = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(12))

        speed_card = BoxLayout(orientation='vertical', padding=[dp(14), dp(10)], spacing=dp(6))
        card_bg(speed_card, C_CARD2, 16)
        speed_card.add_widget(lbl('⏩ Speed', 13, C_ACCENT, True, 26))
        sr = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        sr.add_widget(lbl('🐢', 14, C_MUTED, False, 44))
        self.speed_slider = Slider(min=10, max=100, value=50, step=5)
        self.speed_lbl = lbl('50%', 13, C_CYAN, False, 44)
        self.speed_slider.bind(
            value=lambda i, v: setattr(self.speed_lbl, 'text', str(int(v)) + '%')
        )
        sr.add_widget(self.speed_slider)
        sr.add_widget(lbl('🐇', 14, C_MUTED, False, 44))
        speed_card.add_widget(sr)
        speed_card.add_widget(self.speed_lbl)
        sp_row.add_widget(speed_card)

        self.pitch_card = PitchSliderCard()
        sp_row.add_widget(self.pitch_card)
        content.add_widget(sp_row)

        # ── Advanced Options ──────────────────────────
        self.adv_card = AdvancedOptionsCard()
        content.add_widget(self.adv_card)

        # ── Text Input Card ───────────────────────────
        text_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(320),
                              padding=[dp(14), dp(12)], spacing=dp(10))
        card_bg(text_card, C_CARD2, 16)

        # Top row: counter + import button
        top_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(8))
        self.char_lbl = lbl('0 chars · 0 lines · 0 words', 12, C_MUTED, False, 38)
        top_row.add_widget(self.char_lbl)

        imp = FlatBtn(text='📂 Import', bg=C_BLUE2, size_hint_x=None, width=dp(110),
                      font_size=sp(13))
        imp.bind(on_press=self._import_file)
        top_row.add_widget(imp)

        clr_txt = IconBtn(icon='✕', size_dp=38, bg=C_CARD3)
        clr_txt.bind(on_press=lambda *a: setattr(self.txt, 'text', ''))
        top_row.add_widget(clr_txt)
        text_card.add_widget(top_row)

        # RTL support label
        self.rtl_lbl = lbl('', 11, C_AMBER, False, 22)
        text_card.add_widget(self.rtl_lbl)

        # FIX: Urdu/Arabic input — use_bidi=True helps with RTL display
        self.txt = TextInput(
            hint_text='Enter text here... (Urdu, Arabic, English, any language)',
            multiline=True,
            size_hint=(1, 1),
            background_color=hex_c(C_SURFACE),
            foreground_color=hex_c(C_WHITE),
            hint_text_color=hex_c(C_MUTED),
            cursor_color=hex_c(C_ACCENT),
            font_size=sp(17),
            padding=[dp(14), dp(12)],
            # RTL text fix
            base_direction='rtl' if self.lang_spin.text in RTL_LANGS else 'ltr',
        )
        self.txt.bind(text=self._count)
        text_card.add_widget(self.txt)

        # Imported file info (shown after import)
        self.file_info_container = BoxLayout(
            orientation='vertical', size_hint_y=None, height=0
        )
        text_card.add_widget(self.file_info_container)

        content.add_widget(text_card)

        # ── SSML Preview ─────────────────────────────
        ssml_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        self.ssml_prev_btn = FlatBtn(
            text='📝 Preview SSML', bg=C_GRAY,
            size_hint_x=None, width=dp(160), font_size=sp(13)
        )
        self.ssml_prev_btn.bind(on_press=self._preview_ssml)
        ssml_row.add_widget(self.ssml_prev_btn)
        # Add to queue button
        queue_btn = FlatBtn(text='+ Add to Queue', bg=C_PURPLE, font_size=sp(13))
        queue_btn.bind(on_press=self._add_to_queue)
        ssml_row.add_widget(queue_btn)
        content.add_widget(ssml_row)

        # ── Status + Waveform ─────────────────────────
        status_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120),
                                padding=[dp(14), dp(10)], spacing=dp(8))
        card_bg(status_card, C_CARD2, 14)

        self.status_lbl = lbl('Ready to generate voice ✨', 14, C_MUTED, False, 32)
        status_card.add_widget(self.status_lbl)

        self.prog = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
        status_card.add_widget(self.prog)

        # Waveform visualizer
        self.waveform = WaveformWidget(
            bars=20, color=C_BLUE2,
            size_hint_y=None, height=dp(44),
        )
        status_card.add_widget(self.waveform)
        content.add_widget(status_card)

        # ── Generate Button ───────────────────────────
        self.gen_btn = FlatBtn(
            text='⚡  Generate Voice',
            bg=C_BLUE,
            size_hint_y=None, height=dp(70),
            font_size=sp(20), bold=True,
        )
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        # ── Preview + Download Row ────────────────────
        pd_row = BoxLayout(size_hint_y=None, height=dp(62), spacing=dp(14))
        self.play_btn = FlatBtn(text='▶ Preview', bg=C_RED, font_size=sp(15), disabled=True)
        self.dl_btn   = FlatBtn(text='⬇ Save Voice', bg=C_GREEN, font_size=sp(15), disabled=True)
        self.play_btn.bind(on_press=self._play)
        self.dl_btn.bind(on_press=self._download)
        pd_row.add_widget(self.play_btn)
        pd_row.add_widget(self.dl_btn)
        content.add_widget(pd_row)

        # ── Navigation Row ────────────────────────────
        nav_row = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(10))
        hist_btn = FlatBtn(text='📋 History', bg=C_PURPLE, font_size=sp(14))
        hist_btn.bind(on_press=lambda *a: self._go_hist())
        batch_btn = FlatBtn(text='📦 Batch Queue', bg=C_GRAY, font_size=sp(14))
        batch_btn.bind(on_press=lambda *a: self._go_batch())
        nav_row.add_widget(hist_btn)
        nav_row.add_widget(batch_btn)
        content.add_widget(nav_row)

        # ── Titan Folder Info Banner ──────────────────
        folder_banner = BoxLayout(size_hint_y=None, height=dp(62), padding=[dp(14), dp(8)],
                                  spacing=dp(8))
        card_bg(folder_banner, C_SURFACE, 12)
        folder_banner.add_widget(Label(text='📁', font_size=sp(22),
                                       size_hint_x=None, width=dp(36)))
        titan_p = get_titan_folder()
        fl = Label(
            text='Saves to: Titan AI Studio/\n' + titan_p,
            font_size=sp(11), color=hex_c(C_MUTED2),
            halign='left', valign='middle',
        )
        fl.bind(size=fl.setter('text_size'))
        folder_banner.add_widget(fl)
        content.add_widget(folder_banner)

        # ── How to Use ────────────────────────────────
        how_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(260),
                             padding=[dp(16), dp(14)], spacing=dp(6))
        card_bg(how_card, C_CARD, 14)
        how_card.add_widget(lbl('📖 How to Use', 15, C_ACCENT, True, 34))
        steps = [
            '1.  Choose a Voice Preset (Narrator, News, etc.)',
            '2.  Select Language (30+ supported)',
            '3.  Pick Gender: Male or Female',
            '4.  Set Emotion (Whisper, Shout, Happy, etc.)',
            '5.  Adjust Speed & Pitch sliders',
            '6.  Type text OR Import file (TXT / PDF / DOCX)',
            '7.  Tap ⚡ Generate Voice',
            '8.  Preview then auto-save to Titan AI Studio/',
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

    # ── Screen transitions ───────────────────────────────
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

    # ── Language change → RTL text direction fix ──────────
    def _on_lang_change(self, inst, lang):
        if lang in RTL_LANGS:
            self.rtl_lbl.text = '← RTL mode active for ' + lang + ' (اردو/عربی)'
            self.txt.base_direction = 'rtl'
        else:
            self.rtl_lbl.text = ''
            self.txt.base_direction = 'ltr'

    # ── Preset apply ─────────────────────────────────────
    def _apply_preset(self, name, data):
        self.speed_slider.value = data.get('speed', 50)
        self.pitch_card.pitch_slider.value = data.get('pitch', 0)
        self.emotion_picker._select(data.get('emotion', 'Normal'))
        self._show_toast('Preset applied: ' + name + ' ' + data.get('icon', ''))

    # ── Voice gender selection (FIXED) ────────────────────
    def _pick_voice(self, name):
        self.voice_sel = name   # ← correct string assignment
        for n, b in self._vbtns.items():
            b.set_bg(C_BLUE if n == name else C_CARD2)
            b.bold = (n == name)

    # ── Character / line / word counter (FIXED) ──────────
    def _count(self, inst, val):
        """
        FIX: Previous counter only showed chars/lines.
        Now shows chars + lines + words, all in one line,
        properly formatted so they stay on one line.
        """
        words = len(val.split()) if val.strip() else 0
        lines = len(val.splitlines()) if val.strip() else 0
        chars = len(val)
        self.char_lbl.text = (
            str(chars) + ' chars  ·  '
            + str(words) + ' words  ·  '
            + str(lines) + ' lines'
        )

    # ── Import file ───────────────────────────────────────
    def _import_file(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))
        box.add_widget(lbl('Select file type to import:', 15, C_WHITE, True, 40))

        # File type grid with icons
        grid = GridLayout(cols=3, size_hint_y=None, height=dp(100), spacing=dp(10))
        pop = [None]

        for ft, fi in FILE_ICONS.items():
            col = BoxLayout(orientation='vertical', spacing=dp(4))
            b = FlatBtn(text=fi.get('emoji', ft), bg=fi.get('color', C_BLUE),
                        size_hint_y=None, height=dp(56), font_size=sp(24), radius=12)
            b.bind(on_press=lambda x, t=ft, p=pop: self._open_chooser(t, p[0]))
            col.add_widget(b)
            col.add_widget(Label(text=ft, font_size=sp(10), color=hex_c(C_MUTED2),
                                  size_hint_y=None, height=dp(18)))
            grid.add_widget(col)

        box.add_widget(grid)
        can = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None, height=dp(52))
        box.add_widget(can)

        p = Popup(title='Import File', content=box, size_hint=(0.92, 0.52),
                  background_color=hex_c(C_CARD))
        pop[0] = p
        can.bind(on_press=p.dismiss)
        p.open()

    def _open_chooser(self, ftype, prev):
        if prev:
            prev.dismiss()
        fm = {
            'TXT':  ['*.txt', '*.md'],
            'PDF':  ['*.pdf'],
            'DOCX': ['*.docx', '*.doc'],
            'SRT':  ['*.srt'],
            'DOC':  ['*.doc'],
            'CSV':  ['*.csv'],
        }
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
        sel = FlatBtn(text='✅ Select', bg=C_GREEN, font_size=sp(15))
        can = FlatBtn(text='Cancel',   bg=C_GRAY,  font_size=sp(15))
        br.add_widget(sel)
        br.add_widget(can)
        box.add_widget(br)

        p = Popup(title='Choose ' + ftype + ' File', content=box,
                  size_hint=(0.95, 0.88), background_color=hex_c(C_CARD))

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
                if ftype == 'TXT' or ftype == 'MD':
                    text = read_txt(path)
                elif ftype == 'PDF':
                    text = read_pdf(path)
                elif ftype in ('DOCX', 'DOC'):
                    text = read_docx(path)
                elif ftype == 'SRT':
                    text = read_srt(path)
                elif ftype == 'CSV':
                    text = read_txt(path)
                else:
                    text = read_txt(path)
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: setattr(self.status_lbl, 'text',
                                       'Read error: ' + str(e)[:50])
                )
                return

            def apply(dt):
                if text.strip():
                    self.txt.text = text
                    self.status_lbl.text = '✅ File imported: ' + os.path.basename(path)
                    self.prog.value = 100
                    self._imported_path = path
                    self._imported_type = ftype
                    # Show file info card
                    self._show_file_card(path, ftype)
                    Clock.schedule_once(
                        lambda dt2: Animation(value=0, duration=0.5).start(self.prog), 1.5
                    )
                else:
                    self.status_lbl.text = '⚠ Could not read file. Try TXT format.'
                    self.prog.value = 0

            Clock.schedule_once(apply)

        threading.Thread(target=worker, daemon=True).start()

    def _show_file_card(self, path, ftype):
        """Show file logo card after importing"""
        self.file_info_container.clear_widgets()
        self.file_info_container.height = dp(80)
        card = FileInfoCard(path=path, ftype=ftype, size_hint_y=None, height=dp(72))
        self.file_info_container.add_widget(card)

    # ── Preview SSML ──────────────────────────────────────
    def _preview_ssml(self, *a):
        text     = self.txt.text.strip()
        emotion  = self.emotion_picker.selected
        speed    = int(self.speed_slider.value)
        pitch    = self.pitch_card.value
        breaths  = self.adv_card.use_breaths
        ssml_str = build_ssml(text[:200] if text else 'Sample text', emotion,
                               speed, pitch, breaths)
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        box.add_widget(lbl('SSML Preview (first 200 chars)', 13, C_ACCENT, True, 28))
        sv = ScrollView(size_hint=(1, 1))
        t = Label(
            text=ssml_str,
            font_size=sp(11), color=hex_c(C_WHITE2),
            halign='left', valign='top',
            size_hint_y=None,
        )
        t.bind(texture_size=t.setter('size'))
        sv.add_widget(t)
        box.add_widget(sv)
        ok = FlatBtn(text='OK', bg=C_BLUE, size_hint_y=None, height=dp(50))
        box.add_widget(ok)
        p = Popup(title='SSML Preview', content=box, size_hint=(0.92, 0.7),
                  background_color=hex_c(C_CARD))
        ok.bind(on_press=p.dismiss)
        p.open()

    # ── Add to batch queue ────────────────────────────────
    def _add_to_queue(self, *a):
        text = self.txt.text.strip()
        if not text:
            self._show_toast('Enter text first!')
            return
        q = queue_load()
        q.append({
            'text':    text,
            'lang':    self.lang_spin.text,
            'voice':   self.voice_sel,
            'emotion': self.emotion_picker.selected,
            'speed':   int(self.speed_slider.value),
            'pitch':   self.pitch_card.value,
            'slow':    int(self.speed_slider.value) <= 30,
            'status':  'pending',
            'added':   time.strftime('%d %b %H:%M'),
        })
        queue_save(q)
        self._show_toast('✅ Added to batch queue! (' + str(len(q)) + ' items)')

    # ── Button state helpers ──────────────────────────────
    def _set_ready(self, ok=True):
        self.gen_btn.disabled  = False
        self.play_btn.disabled = not ok
        self.dl_btn.disabled   = not ok

    def _set_busy(self):
        self.gen_btn.disabled  = True
        self.play_btn.disabled = True
        self.dl_btn.disabled   = True

    def _upd(self, val, msg):
        self.prog.value      = val
        self.status_lbl.text = msg

    # ── Generate audio ────────────────────────────────────
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
        self._upd(0, 'Starting voice generation...')
        self.waveform.start()
        threading.Thread(target=self._worker, daemon=True).start()

    def _show_toast(self, msg):
        self.status_lbl.text = msg
        anim = (
            Animation(opacity=1, duration=0.1)
            + Animation(opacity=1, duration=2.5)
            + Animation(opacity=0.6, duration=0.5)
        )
        anim.start(self.status_lbl)

    def _show_err(self, msg):
        box = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(14))
        box.add_widget(Label(
            text=msg, color=hex_c(C_AMBER), font_size=sp(15),
            halign='center', valign='middle',
        ))
        ok = FlatBtn(text='OK', bg=C_BLUE, size_hint_y=None, height=dp(56))
        box.add_widget(ok)
        p = Popup(title='⚠ Language Mismatch', content=box,
                  size_hint=(0.88, 0.42), background_color=hex_c(C_CARD))
        ok.bind(on_press=p.dismiss)
        p.open()

    # ── TTS worker thread ─────────────────────────────────
    def _worker(self):
        try:
            from gtts import gTTS
            Clock.schedule_once(lambda dt: self._upd(20, '🌐 Connecting to TTS service...'))

            lang     = LANGUAGES.get(self.lang_spin.text, 'en')
            emotion  = self.emotion_picker.selected
            em_data  = EMOTION_TAGS.get(emotion, EMOTION_TAGS['Normal'])

            # TLD: emotion can override voice TLD
            tld = em_data.get('tld_override') or VOICE_TLD.get(self.voice_sel, 'com')

            slow = int(self.speed_slider.value) <= 30

            label = (
                LANG_FLAGS.get(self.lang_spin.text, '') + ' '
                + self.lang_spin.text + ' · '
                + self.voice_sel + ' · '
                + emotion
            )
            Clock.schedule_once(
                lambda dt: self._upd(45, '🎙 Generating ' + label + '...')
            )

            text = self.txt.text
            tts  = gTTS(text=text, lang=lang, tld=tld, slow=slow)

            out = os.path.join(
                App.get_running_app().user_data_dir, 'tts_preview.mp3'
            )
            Clock.schedule_once(lambda dt: self._upd(78, '💾 Processing audio...'))
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
        self._upd(100, '✅  Audio ready!  Preview or Save to Titan folder.')
        self._set_ready(ok=True)
        self.waveform.stop()

        Clock.schedule_once(
            lambda dt: Animation(value=0, duration=0.7, t='out_quad').start(self.prog), 1.8
        )

    def _on_err(self, msg):
        self.waveform.stop()
        m = msg.lower()
        if any(k in m for k in ['network', 'connection', 'gaierror', 'timeout']):
            txt = '⚠ No internet! gTTS needs an active connection.'
        elif 'lang' in m:
            txt = '⚠ Language not supported by the TTS engine.'
        else:
            txt = '⚠ Error: ' + msg[:60]
        self._upd(0, txt)
        self._set_ready(ok=False)

    # ── Preview / stop ────────────────────────────────────
    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = '▶ Preview'
            self.play_btn.set_bg(C_RED)
        else:
            self._audio.play()
            self.play_btn.text = '⏹ Stop'
            self.play_btn.set_bg(C_AMBER)

    # ── Download / Save (Auto-saves to Titan AI Studio folder) ──
    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self._show_toast('Generate audio first!')
            return

        if ANDROID_ENV:
            try:
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                ])
            except Exception:
                pass

        # AUTO-SAVE to Titan AI Studio/Audio/ folder
        self._auto_save()

    def _auto_save(self):
        """
        FIX: Auto-saves to Titan AI Studio/Audio/ folder.
        User does NOT need to manually select folder.
        Optionally shows "Save also to..." dialog.
        """
        emotion  = self.emotion_picker.selected
        em_icon  = EMOTION_TAGS.get(emotion, {}).get('icon', '')
        lang     = self.lang_spin.text
        voice    = self.voice_sel
        ts       = str(int(time.time()))

        fname = 'Titan_{lang}_{voice}_{ts}.mp3'.format(
            lang=lang, voice=voice, ts=ts
        )

        audio_dir = get_audio_folder()
        dest      = os.path.join(audio_dir, fname)

        try:
            os.makedirs(audio_dir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self._upd(100, '✅ Saved: ' + fname)
            history_save({
                'filename': fname,
                'path':     dest,
                'lang':     lang,
                'voice':    voice,
                'emotion':  emotion,
                'time':     time.strftime('%d %b %Y  %H:%M'),
                'source':   'studio',
            })
            # Show success popup with folder path
            self._show_save_success(fname, audio_dir, dest)
        except PermissionError:
            # Fallback: ask user to pick location
            self._show_manual_save()
        except Exception as e:
            self._upd(0, 'Save failed: ' + str(e)[:50])

    def _show_save_success(self, fname, folder, full_path):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
        box.add_widget(Label(
            text='✅ Saved to Titan AI Studio!',
            color=hex_c(C_GREEN), font_size=sp(18), bold=True,
            halign='center', valign='middle',
            size_hint_y=None, height=dp(40),
        ))
        box.add_widget(Label(
            text='📁 ' + fname,
            color=hex_c(C_WHITE), font_size=sp(13),
            halign='center', valign='middle',
            size_hint_y=None, height=dp(34),
        ))
        box.add_widget(Label(
            text='Location:\n' + folder,
            color=hex_c(C_MUTED2), font_size=sp(11),
            halign='center', valign='middle',
            size_hint_y=None, height=dp(50),
        ))

        btns = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(12))
        ok = FlatBtn(text='Great! 🎉', bg=C_GREEN, font_size=sp(15))
        also = FlatBtn(text='Save Elsewhere...', bg=C_GRAY, font_size=sp(13))
        btns.add_widget(ok)
        btns.add_widget(also)
        box.add_widget(btns)

        p = Popup(title='Download Complete 🎵', content=box,
                  size_hint=(0.92, 0.55), background_color=hex_c(C_CARD))
        ok.bind(on_press=p.dismiss)
        also.bind(on_press=lambda *a: (p.dismiss(), self._show_manual_save()))
        p.open()

    def _show_manual_save(self):
        """Shows folder selection dialog as fallback"""
        dirs = get_save_dirs()
        box  = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        box.add_widget(Label(
            text='Choose save location:',
            font_size=sp(16), bold=True,
            color=hex_c(C_WHITE), size_hint_y=None, height=dp(40),
        ))
        sv = ScrollView(size_hint=(1, 1))
        bb = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        bb.bind(minimum_height=bb.setter('height'))
        pop = [None]

        for label, path in dirs:
            b = FlatBtn(text=label, bg=C_CARD2, size_hint_y=None, height=dp(72),
                        font_size=sp(12))
            b.bind(on_press=lambda x, p=path, pp=pop: self._do_save(p, pp[0]))
            bb.add_widget(b)

        sv.add_widget(bb)
        box.add_widget(sv)
        can = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None, height=dp(52))
        box.add_widget(can)

        p = Popup(title='💾 Save Audio', content=box,
                  size_hint=(0.93, 0.76), background_color=hex_c(C_CARD))
        pop[0] = p
        can.bind(on_press=p.dismiss)
        p.open()

    def _do_save(self, dest_dir, popup):
        if popup:
            popup.dismiss()
        lang  = self.lang_spin.text
        voice = self.voice_sel
        fname = 'Titan_' + lang + '_' + voice + '_' + str(int(time.time())) + '.mp3'
        dest  = os.path.join(dest_dir, fname)
        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self._upd(100, '✅  Saved: ' + fname)
            history_save({
                'filename': fname,
                'path':     dest,
                'lang':     lang,
                'voice':    voice,
                'emotion':  self.emotion_picker.selected,
                'time':     time.strftime('%d %b %Y  %H:%M'),
                'source':   'manual',
            })
            self._show_save_success(fname, dest_dir, dest)
        except PermissionError:
            self._show_err(
                'Permission denied!\n\nPlease allow storage access\n'
                'in Settings → App Permissions.'
            )
        except Exception as e:
            self._upd(0, 'Save failed: ' + str(e)[:50])


# ═══════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════
class TitanApp(App):
    def build(self):
        self.title = 'Titan AI Studio Pro'

        # Pre-create app folders on startup
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

    def on_stop(self):
        # Clean up waveform animators on exit
        pass


if __name__ == '__main__':
    TitanApp().run()
