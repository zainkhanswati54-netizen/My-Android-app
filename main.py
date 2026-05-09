# ============================================================
# TITAN AI STUDIO PRO - main.py
# Version: 1.1.0  (Android Crash Fixed)
# Professional Voice Studio - Always Free
# ============================================================
#
# FIXES IN THIS VERSION:
#  - edge-tts replaced with gtts for Android compatibility
#  - asyncio removed (crashes Android)
#  - Storage path fixed for Android 10+
#  - Permissions requested BEFORE storage access
#  - SoundLoader fixed for Android
#  - Thread safety improved
# ============================================================

import os
import threading
import json
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.animation import Animation
from kivy.core.audio import SoundLoader

# ─── Platform Check ───────────────────────────────────────────
IS_ANDROID = False
try:
    import android
    from android.permissions import (
        request_permissions,
        check_permission,
        Permission,
    )
    IS_ANDROID = True
except Exception:
    IS_ANDROID = False

# ─── TTS Engine (Android safe — NO asyncio) ───────────────────
TTS_ENGINE = "none"
try:
    from gtts import gTTS
    TTS_ENGINE = "gtts"
except Exception:
    pass

# ─── ElevenLabs ───────────────────────────────────────────────
REQUESTS_AVAILABLE = False
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    pass

# ==============================================================
#  THEME / COLORS
# ==============================================================
COLORS = {
    "bg_dark":    get_color_from_hex("#0A0E1A"),
    "bg_card":    get_color_from_hex("#111827"),
    "bg_card2":   get_color_from_hex("#1A2235"),
    "blue":       get_color_from_hex("#2563EB"),
    "blue_light": get_color_from_hex("#3B82F6"),
    "purple":     get_color_from_hex("#7C3AED"),
    "green":      get_color_from_hex("#059669"),
    "red":        get_color_from_hex("#DC2626"),
    "text":       get_color_from_hex("#F9FAFB"),
    "text_sub":   get_color_from_hex("#9CA3AF"),
    "border":     get_color_from_hex("#1F2D44"),
    "selected":   get_color_from_hex("#2563EB"),
}

Window.clearcolor = COLORS["bg_dark"]

# ==============================================================
#  SAFE SAVE FOLDER SETUP  (Android crash fix)
# ==============================================================
def get_save_root():
    """Get safe writable directory for Android and desktop."""
    if IS_ANDROID:
        # Use app's private external files dir — no MANAGE_EXTERNAL_STORAGE needed
        try:
            from android.storage import app_storage_path
            base = app_storage_path()
        except Exception:
            # Fallback to internal app data dir
            from kivy.app import App as KivyApp
            base = KivyApp.get_running_app().user_data_dir if KivyApp.get_running_app() else "/sdcard"
        return os.path.join(base, "TitanAIStudio")
    else:
        return os.path.join(os.path.expanduser("~"), "TitanAIStudio")


def create_folders():
    """Create all required subfolders safely."""
    try:
        root = get_save_root()
        subfolders = ["Audio", "Cloned", "Imported", "Exports", "Presets", "Queue"]
        for sub in subfolders:
            path = os.path.join(root, sub)
            os.makedirs(path, exist_ok=True)
        return root
    except Exception as e:
        # Fallback to a definitely-writable location
        fallback = os.path.join(os.path.expanduser("~"), "TitanAIStudio")
        os.makedirs(fallback, exist_ok=True)
        return fallback

# Defer SAVE_ROOT init until after permissions on Android
SAVE_ROOT = None

# ==============================================================
#  VOICE ENGINE  (Android-safe, no asyncio)
# ==============================================================

# gTTS lang + speed mapping
GTTS_LANGS = {
    "male":   "en",
    "female": "en",
}

# Speed tiers for gTTS (only normal vs slow available)
def _gtts_slow(speed):
    return speed < 0.85


def generate_voice(text, gender="female", mood="normal", speed=1.0,
                   pitch=0, elevenlabs_key=None, callback=None):
    """
    Master voice generation. Runs in background thread.
    Android-safe: no asyncio, no edge-tts.
    """
    if SAVE_ROOT is None:
        if callback:
            Clock.schedule_once(lambda dt: callback(None, "Storage not ready yet. Try again."), 0)
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(SAVE_ROOT, "Audio", f"titan_{timestamp}.mp3")

    def _run():
        try:
            if elevenlabs_key and REQUESTS_AVAILABLE:
                _elevenlabs_generate(text, gender, out_path, elevenlabs_key)

            elif TTS_ENGINE == "gtts":
                slow = _gtts_slow(speed)
                tts = gTTS(text=text, lang=GTTS_LANGS.get(gender, "en"), slow=slow)
                tts.save(out_path)

            else:
                if callback:
                    Clock.schedule_once(
                        lambda dt: callback(None, "No TTS engine found.\nInstall gTTS: pip install gTTS"), 0
                    )
                return

            if callback:
                Clock.schedule_once(lambda dt: callback(out_path, None), 0)

        except Exception as e:
            if callback:
                Clock.schedule_once(lambda dt: callback(None, str(e)), 0)

    threading.Thread(target=_run, daemon=True).start()


def _elevenlabs_generate(text, gender, out_path, api_key):
    voice_id = "ErXwobaYiN019PkySvjV" if gender == "male" else "21m00Tcm4TlvDq8ikWAM"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(resp.content)
    else:
        raise Exception(f"ElevenLabs error {resp.status_code}: {resp.text}")


# ==============================================================
#  CUSTOM WIDGETS
# ==============================================================

class RoundedButton(Button):
    def __init__(self, bg_color=None, text_color=None, radius=dp(12), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS["blue"]
        self.text_color = text_color or COLORS["text"]
        self.radius = radius
        self.background_color = (0, 0, 0, 0)
        self.color = self.text_color
        self.bold = True
        self.font_size = dp(14)
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

    def on_press(self):
        anim = Animation(opacity=0.7, duration=0.05) + Animation(opacity=1.0, duration=0.05)
        anim.start(self)


class CirclePlayButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_playing = False
        self.background_color = (0, 0, 0, 0)
        self.size_hint = (None, None)
        self.size = (dp(64), dp(64))
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS["blue"])
            Ellipse(pos=self.pos, size=self.size)
        self.text = "⏸" if self.is_playing else "▶"
        self.color = COLORS["text"]
        self.font_size = dp(22)
        self.bold = True

    def toggle(self):
        self.is_playing = not self.is_playing
        self._draw()


class CardBox(BoxLayout):
    def __init__(self, bg=None, radius=dp(14), padding=dp(14), **kwargs):
        kwargs.setdefault("orientation", "vertical")
        super().__init__(padding=padding, **kwargs)
        self._bg_color = bg or COLORS["bg_card"]
        self._radius = radius
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])


class SectionLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = COLORS["blue_light"]
        self.bold = True
        self.font_size = dp(14)
        self.size_hint_y = None
        self.height = dp(28)
        self.halign = "left"
        self.valign = "middle"
        self.bind(size=lambda *a: setattr(self, "text_size", self.size))


class SubLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = COLORS["text_sub"]
        self.font_size = dp(12)
        self.size_hint_y = None
        self.height = dp(22)
        self.halign = "left"
        self.valign = "middle"
        self.bind(size=lambda *a: setattr(self, "text_size", self.size))


class MoodButton(ToggleButton):
    def __init__(self, mood_name, icon, **kwargs):
        super().__init__(group="mood", **kwargs)
        self.mood_name = mood_name
        self.icon = icon
        self.text = f"{icon}\n{mood_name}"
        self.markup = True
        self.background_color = (0, 0, 0, 0)
        self.color = COLORS["text_sub"]
        self.font_size = dp(11)
        self.halign = "center"
        self.size_hint_y = None
        self.height = dp(60)
        self.bind(pos=self._draw, size=self._draw, state=self._on_state)
        Clock.schedule_once(self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        bg = COLORS["selected"] if self.state == "down" else COLORS["bg_card2"]
        with self.canvas.before:
            Color(*bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

    def _on_state(self, *args):
        self.color = COLORS["text"] if self.state == "down" else COLORS["text_sub"]
        self._draw()


class GenderButton(ToggleButton):
    def __init__(self, label, icon, gender_val, **kwargs):
        super().__init__(group="gender", **kwargs)
        self.gender_val = gender_val
        self.icon = icon
        self.text = f"{icon}  {label}"
        self.background_color = (0, 0, 0, 0)
        self.color = COLORS["text_sub"]
        self.font_size = dp(13)
        self.bold = True
        self.halign = "center"
        self.size_hint_y = None
        self.height = dp(48)
        self.bind(pos=self._draw, size=self._draw, state=self._on_state)
        Clock.schedule_once(self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        bg = COLORS["selected"] if self.state == "down" else COLORS["bg_card2"]
        with self.canvas.before:
            Color(*bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

    def _on_state(self, *args):
        self.color = COLORS["text"] if self.state == "down" else COLORS["text_sub"]
        self._draw()


# ==============================================================
#  SPLASH SCREEN
# ==============================================================

class SplashScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        with layout.canvas.before:
            Color(*COLORS["bg_dark"])
            self._rect = Rectangle(size=Window.size)
        layout.bind(
            size=lambda *a: setattr(self._rect, "size", layout.size),
            pos=lambda *a: setattr(self._rect, "pos", layout.pos),
        )

        logo_box = BoxLayout(orientation="vertical", spacing=dp(8))
        logo_box.add_widget(Widget())

        logo_lbl = Label(
            text="SG",
            font_size=dp(64),
            bold=True,
            color=COLORS["blue"],
            size_hint_y=None,
            height=dp(100),
        )
        logo_box.add_widget(logo_lbl)

        title = Label(
            text="Titan AI Studio Pro",
            font_size=dp(22),
            bold=True,
            color=COLORS["text"],
            size_hint_y=None,
            height=dp(36),
        )
        logo_box.add_widget(title)

        sub = Label(
            text="Professional Voice Studio  ·  Always Free",
            font_size=dp(13),
            color=COLORS["text_sub"],
            size_hint_y=None,
            height=dp(24),
        )
        logo_box.add_widget(sub)
        logo_box.add_widget(Widget())
        layout.add_widget(logo_box)
        self.add_widget(layout)

    def on_enter(self):
        # Give Android time to process permissions before going to main
        Clock.schedule_once(self._go_main, 2.5)

    def _go_main(self, dt):
        # Init storage after splash (permissions already requested)
        global SAVE_ROOT
        if SAVE_ROOT is None:
            SAVE_ROOT = create_folders()
        self.manager.current = "main"


# ==============================================================
#  MAIN SCREEN
# ==============================================================

class MainScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_gender = "female"
        self.selected_mood   = "normal"
        self.speed_val       = 1.0
        self.pitch_val       = 0
        self.last_audio_path = None
        self.current_sound   = None
        self.history         = []
        self.elevenlabs_key  = ""  # loaded on_enter

        root = BoxLayout(orientation="vertical")
        root.add_widget(self._build_header())

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(10),
                            padding=[dp(12), dp(8), dp(12), dp(16)],
                            size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(self._build_gender_row())
        content.add_widget(self._build_mood_row())
        content.add_widget(self._build_speed_pitch())
        content.add_widget(self._build_advanced())
        content.add_widget(self._build_text_input())
        content.add_widget(self._build_generate_section())
        content.add_widget(self._build_how_to())

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        # Load API key after storage is ready
        self.elevenlabs_key = self._load_api_key()
        # Update save path label
        if SAVE_ROOT and hasattr(self, "_save_sub"):
            self._save_sub.text = f"Saves to: {os.path.join(SAVE_ROOT, 'Audio')}"

    # ── HEADER ──────────────────────────────────────────────────
    def _build_header(self):
        header = BoxLayout(orientation="horizontal", size_hint_y=None,
                           height=dp(64), padding=[dp(12), dp(8)], spacing=dp(10))
        with header.canvas.before:
            Color(*COLORS["bg_card"])
            self._hdr_rect = Rectangle()
        header.bind(
            pos=lambda *a: setattr(self._hdr_rect, "pos", header.pos),
            size=lambda *a: setattr(self._hdr_rect, "size", header.size),
        )

        logo_box = BoxLayout(orientation="horizontal", size_hint_x=None,
                             width=dp(48), spacing=dp(4))
        logo_lbl = Label(text="SG", font_size=dp(20), bold=True, color=COLORS["blue"])
        logo_box.add_widget(logo_lbl)

        title_box = BoxLayout(orientation="vertical", spacing=0)
        title_box.add_widget(Label(text="Titan AI Studio Pro", font_size=dp(15),
                                   bold=True, color=COLORS["text"],
                                   halign="left", valign="bottom",
                                   text_size=(None, None)))
        title_box.add_widget(Label(text="Professional Voice Studio  ·  Always Free",
                                   font_size=dp(11), color=COLORS["text_sub"],
                                   halign="left", valign="top",
                                   text_size=(None, None)))

        settings_btn = RoundedButton(text="⚙", bg_color=COLORS["bg_card2"],
                                     size_hint=(None, None),
                                     size=(dp(44), dp(44)), radius=dp(10))
        settings_btn.bind(on_press=lambda *a: self.manager.navigate("settings"))

        header.add_widget(logo_box)
        header.add_widget(title_box)
        header.add_widget(Widget())
        header.add_widget(settings_btn)
        return header

    # ── GENDER ROW ──────────────────────────────────────────────
    def _build_gender_row(self):
        card = CardBox(size_hint_y=None, height=dp(72))
        card.add_widget(SectionLabel(text="♂♀  Voice Gender"))
        row = BoxLayout(orientation="horizontal", spacing=dp(8),
                        size_hint_y=None, height=dp(52))

        male_btn   = GenderButton("Male",   "♂", "male")
        female_btn = GenderButton("Female", "♀", "female", state="down")

        def on_gender(btn, state):
            if state == "down":
                self.selected_gender = btn.gender_val

        male_btn.bind(state=lambda b, s: on_gender(b, s))
        female_btn.bind(state=lambda b, s: on_gender(b, s))

        row.add_widget(male_btn)
        row.add_widget(female_btn)
        card.add_widget(row)
        return card

    # ── MOOD ROW ────────────────────────────────────────────────
    def _build_mood_row(self):
        card = CardBox(size_hint_y=None, height=dp(160))
        card.add_widget(SectionLabel(text="🎭  Emotions & Mood"))

        moods = [
            ("Normal",  "😐"), ("Happy",   "😊"), ("Sad",     "😢"),
            ("Whisper", "🤫"), ("Shout",   "📢"), ("Sarcasm", "😏"),
            ("Excited", "🤩"), ("Serious", "😐"),
        ]

        grid = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(130))
        first = True
        for name, icon in moods:
            btn = MoodButton(mood_name=name, icon=icon)
            if first:
                btn.state = "down"
                first = False

            def _mood_cb(b, state, n=name.lower()):
                if state == "down":
                    self.selected_mood = n

            btn.bind(state=_mood_cb)
            grid.add_widget(btn)

        card.add_widget(grid)
        return card

    # ── SPEED & PITCH ───────────────────────────────────────────
    def _build_speed_pitch(self):
        card = CardBox(size_hint_y=None, height=dp(160), spacing=dp(6))
        card.add_widget(SectionLabel(text="⚡  Speed  &  🎵  Pitch & Tone Shift"))

        row = BoxLayout(orientation="horizontal", spacing=dp(10),
                        size_hint_y=None, height=dp(110))

        spd_card = CardBox(bg=COLORS["bg_card2"])
        spd_hdr  = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
        spd_hdr.add_widget(SubLabel(text="Speed"))
        self._speed_lbl = Label(text="100%", font_size=dp(12),
                                 color=COLORS["blue_light"],
                                 size_hint_y=None, height=dp(24),
                                 halign="right", valign="middle")
        self._speed_lbl.bind(size=lambda *a: setattr(self._speed_lbl, "text_size", self._speed_lbl.size))
        spd_hdr.add_widget(self._speed_lbl)
        spd_card.add_widget(spd_hdr)

        spd_slider = Slider(min=0.5, max=2.0, value=1.0, step=0.05,
                            size_hint_y=None, height=dp(36))
        spd_slider.bind(value=self._on_speed)
        spd_card.add_widget(spd_slider)

        pch_card = CardBox(bg=COLORS["bg_card2"])
        pch_hdr  = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
        pch_hdr.add_widget(SubLabel(text="Pitch & Tone"))
        self._pitch_lbl = Label(text="0 st", font_size=dp(12),
                                 color=COLORS["blue_light"],
                                 size_hint_y=None, height=dp(24),
                                 halign="right", valign="middle")
        self._pitch_lbl.bind(size=lambda *a: setattr(self._pitch_lbl, "text_size", self._pitch_lbl.size))
        pch_hdr.add_widget(self._pitch_lbl)
        pch_card.add_widget(pch_hdr)

        pch_slider = Slider(min=-10, max=10, value=0, step=1,
                            size_hint_y=None, height=dp(36))
        pch_slider.bind(value=self._on_pitch)
        pch_card.add_widget(pch_slider)

        row.add_widget(spd_card)
        row.add_widget(pch_card)
        card.add_widget(row)
        return card

    def _on_speed(self, slider, val):
        self.speed_val = val
        self._speed_lbl.text = f"{int(val * 100)}%"

    def _on_pitch(self, slider, val):
        self.pitch_val = int(val)
        self._pitch_lbl.text = f"{int(val):+d} st"

    # ── ADVANCED OPTIONS ────────────────────────────────────────
    def _build_advanced(self):
        card = CardBox(size_hint_y=None, height=dp(210), spacing=dp(4))
        card.add_widget(SectionLabel(text="🔧  Advanced Options"))

        options = [
            ("Dynamic Breath Simulation", "breath"),
            ("Ultra-Low Latency Mode",    "latency"),
            ("SSML Markup Support",       "ssml"),
            ("Adaptive Pacing",           "pacing"),
        ]
        self._adv_switches = {}
        for label_text, key in options:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(38))
            lbl = Label(text=label_text, font_size=dp(13), color=COLORS["text"],
                        halign="left", valign="middle")
            lbl.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
            sw = Switch(active=False, size_hint_x=None, width=dp(70))
            self._adv_switches[key] = sw
            row.add_widget(lbl)
            row.add_widget(sw)
            card.add_widget(row)
        return card

    # ── TEXT INPUT ──────────────────────────────────────────────
    def _build_text_input(self):
        card = CardBox(size_hint_y=None, height=dp(180), spacing=dp(6))
        card.add_widget(SectionLabel(text="✍  Enter Text"))

        self._text_input = TextInput(
            hint_text="Type or paste your text here...",
            hint_text_color=COLORS["text_sub"],
            foreground_color=COLORS["text"],
            background_color=(0, 0, 0, 0),
            cursor_color=COLORS["blue"],
            font_size=dp(14),
            multiline=True,
            size_hint_y=None,
            height=dp(110),
        )
        with self._text_input.canvas.before:
            Color(*COLORS["bg_card2"])
            self._ti_rect = RoundedRectangle(radius=[dp(10)])
        self._text_input.bind(
            pos=lambda *a: setattr(self._ti_rect, "pos", self._text_input.pos),
            size=lambda *a: setattr(self._ti_rect, "size", self._text_input.size),
        )

        self._char_label = SubLabel(text="0 chars  ·  0 words  ·  0 lines")
        self._text_input.bind(text=self._update_counter)

        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36), spacing=dp(8))
        ssml_btn  = RoundedButton(text="⟨/⟩ Preview SSML", bg_color=COLORS["bg_card2"],
                                   size_hint_x=0.5, height=dp(36))
        queue_btn = RoundedButton(text="+ Add to Queue", bg_color=COLORS["purple"],
                                   size_hint_x=0.5, height=dp(36))
        queue_btn.bind(on_press=self._add_to_queue)
        row.add_widget(ssml_btn)
        row.add_widget(queue_btn)

        card.add_widget(self._text_input)
        card.add_widget(self._char_label)
        card.add_widget(row)
        return card

    def _update_counter(self, ti, text):
        chars = len(text)
        words = len(text.split()) if text.strip() else 0
        lines = text.count("\n") + 1 if text.strip() else 0
        self._char_label.text = f"{chars} chars  ·  {words} words  ·  {lines} lines"

    # ── GENERATE SECTION ────────────────────────────────────────
    def _build_generate_section(self):
        card = CardBox(size_hint_y=None, height=dp(280), spacing=dp(10))
        card.add_widget(SectionLabel(text="🎙  Generate Voice"))

        gen_btn = RoundedButton(
            text="  🎤  Generate Voice",
            bg_color=COLORS["blue"],
            size_hint_y=None,
            height=dp(54),
            font_size=dp(16),
        )
        gen_btn.bind(on_press=self._generate)
        card.add_widget(gen_btn)

        self._status_lbl = Label(
            text="Ready — Enter text and press Generate",
            font_size=dp(12),
            color=COLORS["text_sub"],
            size_hint_y=None,
            height=dp(24),
            halign="center",
        )
        self._status_lbl.bind(size=lambda *a: setattr(self._status_lbl, "text_size", self._status_lbl.size))
        card.add_widget(self._status_lbl)

        player_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                               height=dp(72), spacing=dp(16))
        player_row.add_widget(Widget())

        self._play_btn = CirclePlayButton()
        self._play_btn.bind(on_press=self._toggle_play)
        player_row.add_widget(self._play_btn)

        prog_box = BoxLayout(orientation="vertical", spacing=dp(4))
        self._prog_slider = Slider(min=0, max=100, value=0, size_hint_y=None, height=dp(30))
        self._time_label  = SubLabel(text="0:00 / 0:00", halign="center")
        prog_box.add_widget(self._prog_slider)
        prog_box.add_widget(self._time_label)
        player_row.add_widget(prog_box)

        save_btn = RoundedButton(text="💾 Save", bg_color=COLORS["green"],
                                  size_hint=(None, None), size=(dp(70), dp(54)),
                                  radius=dp(10))
        save_btn.bind(on_press=self._save_voice)
        player_row.add_widget(save_btn)
        player_row.add_widget(Widget())
        card.add_widget(player_row)

        hq_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                            height=dp(46), spacing=dp(8))
        hist_btn  = RoundedButton(text="📋 History",     bg_color=COLORS["purple"])
        batch_btn = RoundedButton(text="⏳ Batch Queue", bg_color=COLORS["bg_card2"])
        hist_btn.bind(on_press=self._show_history)
        hq_row.add_widget(hist_btn)
        hq_row.add_widget(batch_btn)
        card.add_widget(hq_row)

        save_path = os.path.join(SAVE_ROOT, "Audio") if SAVE_ROOT else "Initializing..."
        self._save_sub = SubLabel(text=f"Saves to: {save_path}", halign="left")
        card.add_widget(self._save_sub)
        return card

    # ── HOW TO USE ──────────────────────────────────────────────
    def _build_how_to(self):
        card = CardBox(size_hint_y=None, height=dp(180), spacing=dp(4))
        card.add_widget(SectionLabel(text="ℹ  How to Use"))
        steps = [
            "1. Choose a Voice Preset (Male / Female)",
            "2. Select Emotion / Mood for natural expression",
            "3. Adjust Speed and Pitch to your liking",
            "4. Type or import your text",
            "5. Tap Generate Voice — audio saves automatically",
            "6. Press ▶ to preview, 💾 to save permanently",
        ]
        for s in steps:
            card.add_widget(SubLabel(text=s))
        return card

    # ── ACTIONS ─────────────────────────────────────────────────
    def _generate(self, *args):
        text = self._text_input.text.strip()
        if not text:
            self._set_status("⚠  Please enter some text first!", error=True)
            return

        self._set_status("⏳  Generating voice... please wait")

        generate_voice(
            text=text,
            gender=self.selected_gender,
            mood=self.selected_mood,
            speed=self.speed_val,
            pitch=self.pitch_val,
            elevenlabs_key=self.elevenlabs_key if self.elevenlabs_key else None,
            callback=self._on_generated,
        )

    def _on_generated(self, path, error):
        if error:
            self._set_status(f"❌ Error: {error}", error=True)
            return
        self.last_audio_path = path
        self.history.append(path)
        self._set_status("✅  Generated! Saved to Audio/")
        self._load_audio(path)

    def _load_audio(self, path):
        """Safely load audio — Android needs a small delay."""
        if self.current_sound:
            try:
                self.current_sound.stop()
                self.current_sound.unload()
            except Exception:
                pass
            self.current_sound = None
        self._play_btn.is_playing = False
        self._play_btn._draw()
        # Schedule load to avoid blocking main thread on Android
        Clock.schedule_once(lambda dt: self._do_load(path), 0.1)

    def _do_load(self, path):
        try:
            self.current_sound = SoundLoader.load(path)
            if self.current_sound is None:
                self._set_status("⚠  Could not load audio for playback", error=True)
        except Exception as e:
            self._set_status(f"⚠  Audio load error: {e}", error=True)

    def _toggle_play(self, *args):
        if not self.current_sound:
            self._set_status("⚠  Generate audio first!", error=True)
            return
        try:
            if self._play_btn.is_playing:
                self.current_sound.stop()
            else:
                self.current_sound.play()
            self._play_btn.toggle()
        except Exception as e:
            self._set_status(f"⚠  Playback error: {e}", error=True)

    def _save_voice(self, *args):
        if not self.last_audio_path or not os.path.exists(self.last_audio_path):
            self._set_status("⚠  No audio to save yet!", error=True)
            return
        self._set_status(f"💾  Saved to: {self.last_audio_path}")

    def _add_to_queue(self, *args):
        text = self._text_input.text.strip()
        if not text:
            self._set_status("⚠  Enter text to add to queue", error=True)
            return
        if SAVE_ROOT is None:
            self._set_status("⚠  Storage not ready yet", error=True)
            return
        queue_file = os.path.join(SAVE_ROOT, "Queue", "queue.json")
        try:
            queue = []
            if os.path.exists(queue_file):
                with open(queue_file) as f:
                    queue = json.load(f)
            queue.append({
                "text":   text,
                "gender": self.selected_gender,
                "mood":   self.selected_mood,
                "speed":  self.speed_val,
                "pitch":  self.pitch_val,
                "added":  datetime.now().isoformat(),
            })
            with open(queue_file, "w") as f:
                json.dump(queue, f, indent=2)
            self._set_status(f"✅  Added to queue ({len(queue)} items)")
        except Exception as e:
            self._set_status(f"❌  Queue error: {e}", error=True)

    def _show_history(self, *args):
        content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10))
        if not self.history:
            content.add_widget(Label(text="No history yet.", color=COLORS["text_sub"]))
        else:
            scroll = ScrollView()
            inner  = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
            inner.bind(minimum_height=inner.setter("height"))
            for path in reversed(self.history[-20:]):
                fname = os.path.basename(path)
                row   = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
                lbl   = Label(text=fname, font_size=dp(12), color=COLORS["text"],
                              halign="left", valign="middle")
                lbl.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
                play_b = RoundedButton(text="▶", bg_color=COLORS["blue"],
                                       size_hint=(None, None), size=(dp(40), dp(36)))

                def _play(b, p=path):
                    self._load_audio(p)
                    Clock.schedule_once(lambda dt: self._toggle_play(), 0.2)

                play_b.bind(on_press=_play)
                row.add_widget(lbl)
                row.add_widget(play_b)
                inner.add_widget(row)
            scroll.add_widget(inner)
            content.add_widget(scroll)

        close_btn = RoundedButton(text="Close", bg_color=COLORS["red"],
                                   size_hint_y=None, height=dp(44))
        content.add_widget(close_btn)
        popup = Popup(title="History", content=content,
                      size_hint=(0.9, 0.7),
                      background_color=COLORS["bg_card"])
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _set_status(self, msg, error=False):
        self._status_lbl.text  = msg
        self._status_lbl.color = COLORS["red"] if error else COLORS["text_sub"]

    def _load_api_key(self):
        if SAVE_ROOT is None:
            return ""
        key_file = os.path.join(SAVE_ROOT, "Presets", "api_key.txt")
        try:
            if os.path.exists(key_file):
                with open(key_file) as f:
                    return f.read().strip()
        except Exception:
            pass
        return ""


# ==============================================================
#  SETTINGS SCREEN
# ==============================================================

class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        root.add_widget(self._build_header())

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(10),
                            padding=[dp(12), dp(8), dp(12), dp(16)],
                            size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(self._build_save_folder())
        content.add_widget(self._build_elevenlabs())
        content.add_widget(self._build_about())
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _build_header(self):
        header = BoxLayout(orientation="horizontal", size_hint_y=None,
                           height=dp(56), padding=[dp(12), dp(8)], spacing=dp(10))
        with header.canvas.before:
            Color(*COLORS["bg_card"])
            self._r = Rectangle()
        header.bind(
            pos=lambda *a: setattr(self._r, "pos", header.pos),
            size=lambda *a: setattr(self._r, "size", header.size),
        )
        back_btn = RoundedButton(text="← Back", bg_color=COLORS["bg_card2"],
                                  size_hint=(None, None), size=(dp(90), dp(40)))
        back_btn.bind(on_press=lambda *a: setattr(self.manager, "current", "main"))
        title = Label(text="⚙  Settings", font_size=dp(17), bold=True,
                      color=COLORS["blue_light"])
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Widget())
        return header

    def _build_save_folder(self):
        card = CardBox(size_hint_y=None, height=dp(200), spacing=dp(6))
        card.add_widget(SectionLabel(text="📁  App Save Folder"))
        save_path = SAVE_ROOT if SAVE_ROOT else "Initializing..."
        card.add_widget(SubLabel(text=save_path))
        card.add_widget(SubLabel(text="All audio saved here automatically"))
        card.add_widget(SectionLabel(text="📂  Folder Structure"))
        folders = [
            ("Audio/",    "Generated voice files"),
            ("Cloned/",   "Voice cloning results"),
            ("Imported/", "Imported documents"),
            ("Exports/",  "Exported projects"),
            ("Presets/",  "Custom voice presets"),
            ("Queue/",    "Batch processing queue"),
        ]
        for folder, desc in folders:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
            row.add_widget(Label(text=folder, font_size=dp(12), color=COLORS["blue_light"],
                                  halign="left", valign="middle",
                                  size_hint_x=0.35, text_size=(None, None)))
            row.add_widget(Label(text=desc, font_size=dp(12), color=COLORS["text_sub"],
                                  halign="left", valign="middle",
                                  text_size=(None, None)))
            card.add_widget(row)
        return card

    def _build_elevenlabs(self):
        card = CardBox(size_hint_y=None, height=dp(170), spacing=dp(8))
        card.add_widget(SectionLabel(text="🔑  ElevenLabs API (Voice Cloning)"))
        card.add_widget(SubLabel(text="For Professional Voice Cloning, enter your ElevenLabs API key:"))

        self._api_input = TextInput(
            hint_text="Paste API key here...",
            hint_text_color=COLORS["text_sub"],
            foreground_color=COLORS["text"],
            background_color=(0, 0, 0, 0),
            font_size=dp(13),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(42),
        )
        with self._api_input.canvas.before:
            Color(*COLORS["bg_card2"])
            self._api_rect = RoundedRectangle(radius=[dp(8)])
        self._api_input.bind(
            pos=lambda *a: setattr(self._api_rect, "pos", self._api_input.pos),
            size=lambda *a: setattr(self._api_rect, "size", self._api_input.size),
        )
        if SAVE_ROOT:
            key_file = os.path.join(SAVE_ROOT, "Presets", "api_key.txt")
            try:
                if os.path.exists(key_file):
                    with open(key_file) as f:
                        self._api_input.text = f.read().strip()
            except Exception:
                pass

        save_btn = RoundedButton(text="💾  Save API Key", bg_color=COLORS["blue"],
                                  size_hint_y=None, height=dp(44))
        save_btn.bind(on_press=self._save_api_key)
        card.add_widget(self._api_input)
        card.add_widget(save_btn)
        return card

    def _build_about(self):
        card = CardBox(size_hint_y=None, height=dp(80), spacing=dp(6))
        card.add_widget(SectionLabel(text="ℹ  About"))
        card.add_widget(SubLabel(text="Titan AI Studio Pro  v1.1.0  (Android Fixed)"))
        card.add_widget(SubLabel(text="Professional Voice Generation  ·  Always Free"))
        return card

    def _save_api_key(self, *args):
        if SAVE_ROOT is None:
            self._show_toast("Storage not ready yet!")
            return
        key = self._api_input.text.strip()
        key_file = os.path.join(SAVE_ROOT, "Presets", "api_key.txt")
        try:
            with open(key_file, "w") as f:
                f.write(key)
            self._show_toast("API key saved!")
        except Exception as e:
            self._show_toast(f"Error: {e}")

    def _show_toast(self, msg):
        popup = Popup(title="", content=Label(text=msg, color=COLORS["text"]),
                      size_hint=(0.6, 0.15),
                      background_color=COLORS["bg_card"])
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)


# ==============================================================
#  SCREEN MANAGER
# ==============================================================

class TitanSM(ScreenManager):
    def navigate(self, screen_name):
        self.current = screen_name


# ==============================================================
#  APP
# ==============================================================

class TitanAIStudioApp(App):

    def build(self):
        # Request Android permissions FIRST — before any storage access
        if IS_ANDROID:
            try:
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.INTERNET,
                    Permission.RECORD_AUDIO,
                ])
            except Exception:
                pass
        else:
            # Desktop: init storage immediately
            global SAVE_ROOT
            SAVE_ROOT = create_folders()

        sm = TitanSM(transition=FadeTransition(duration=0.25))
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.current = "splash"
        return sm

    def get_application_name(self):
        return "Titan AI Studio Pro"


# ==============================================================
if __name__ == "__main__":
    TitanAIStudioApp().run()
