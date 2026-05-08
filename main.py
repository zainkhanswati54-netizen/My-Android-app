# =============================================================
#  Titan AI Studio Pro — main.py  v7.0.0
#  Voice Cloning (Coqui TTS) + Admin Dashboard
#  Author: Titan AI Studio
# =============================================================

import os, json, threading, time, shutil, datetime, hashlib, platform
from pathlib import Path

# ── Kivy config (must be before kivy imports) ─────────────────
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.animation import Animation

# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────
APP_VERSION  = "7.0.0"
HISTORY_FILE = "history.json"
ADMIN_LOG    = "admin_log.json"
ADMIN_PASS   = "titan2026"       # Change this in production!
APP_ICON     = "AI.png"

LANGUAGES = {
    "English":  "en", "Urdu":    "ur", "Hindi":   "hi",
    "Arabic":   "ar", "French":  "fr", "Spanish": "es",
    "German":   "de", "Turkish": "tr", "Russian": "ru",
    "Chinese":  "zh", "Japanese":"ja", "Korean":  "ko",
}

# Coqui TTS model IDs (offline, no API key needed)
COQUI_MODELS = {
    "English (Natural)"    : "tts_models/en/ljspeech/tacotron2-DDC",
    "English (VITS HD)"    : "tts_models/en/vctk/vits",
    "English (Fast)"       : "tts_models/en/ljspeech/glow-tts",
    "Multilingual"         : "tts_models/multilingual/multi-dataset/xtts_v2",
    "German"               : "tts_models/de/thorsten/tacotron2-DDC",
    "Spanish"              : "tts_models/es/mai/tacotron2-DDC",
    "French"               : "tts_models/fr/mai/tacotron2-DDC",
}

SPEED_MAP = {"Slow": 0.75, "Normal": 1.0, "Fast": 1.3}

# ─────────────────────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────────────────────
def get_internal_storage():
    """Returns a writable path for audio files."""
    candidates = [
        Path("/sdcard/TitanAI"),
        Path.home() / "TitanAI",
        Path("/storage/emulated/0/TitanAI"),
        Path(os.getcwd()) / "TitanAI_output",
    ]
    for p in candidates:
        try:
            p.mkdir(parents=True, exist_ok=True)
            test = p / ".write_test"
            test.write_text("ok")
            test.unlink()
            return p
        except Exception:
            continue
    return Path(os.getcwd()) / "TitanAI_output"

SAVE_DIR = get_internal_storage()

def load_history():
    try:
        return json.loads(Path(HISTORY_FILE).read_text()) if Path(HISTORY_FILE).exists() else []
    except Exception:
        return []

def save_history(history):
    try:
        Path(HISTORY_FILE).write_text(json.dumps(history, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[History] Save error: {e}")

def log_admin(event: str, data: dict = None):
    """Write event to admin log."""
    try:
        log = []
        if Path(ADMIN_LOG).exists():
            log = json.loads(Path(ADMIN_LOG).read_text())
        log.append({
            "ts": datetime.datetime.now().isoformat(),
            "event": event,
            "data": data or {}
        })
        Path(ADMIN_LOG).write_text(json.dumps(log, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[Admin Log] Error: {e}")

def get_stats():
    """Returns stats dict for Admin Dashboard."""
    history = load_history()
    admin_log = []
    if Path(ADMIN_LOG).exists():
        try:
            admin_log = json.loads(Path(ADMIN_LOG).read_text())
        except Exception:
            pass
    total_size = sum(
        Path(h["path"]).stat().st_size
        for h in history
        if h.get("path") and Path(h["path"]).exists()
    )
    voices_used = {}
    for h in history:
        v = h.get("voice", "Unknown")
        voices_used[v] = voices_used.get(v, 0) + 1
    return {
        "total_generated" : len(history),
        "total_size_mb"   : round(total_size / 1024 / 1024, 2),
        "voices_used"     : voices_used,
        "recent_events"   : admin_log[-20:][::-1],
        "app_version"     : APP_VERSION,
        "history_count"   : len(history),
    }

# ─────────────────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────────────────
C_BG      = (0.07, 0.07, 0.12, 1)
C_CARD    = (0.12, 0.12, 0.20, 1)
C_ACCENT  = (0.22, 0.47, 1.00, 1)
C_ACCENT2 = (0.55, 0.28, 1.00, 1)
C_GREEN   = (0.18, 0.80, 0.55, 1)
C_RED     = (0.95, 0.30, 0.30, 1)
C_ORANGE  = (1.00, 0.60, 0.15, 1)
C_TEXT    = (0.95, 0.95, 0.98, 1)
C_MUTED   = (0.58, 0.58, 0.70, 1)
C_BORDER  = (0.22, 0.22, 0.35, 1)
C_ADMIN   = (0.90, 0.60, 0.10, 1)

# ─────────────────────────────────────────────────────────────
#  WIDGET HELPERS
# ─────────────────────────────────────────────────────────────
def make_label(text, font_size=14, color=None, bold=False, halign="left", **kw):
    color = color or C_TEXT
    lbl = Label(
        text=text, font_size=sp(font_size), color=color,
        bold=bold, halign=halign, markup=True,
        size_hint_y=None, **kw
    )
    lbl.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
    lbl.bind(width=lambda i, v: setattr(i, "text_size", (v, None)))
    return lbl

def make_card(padding=dp(12), spacing=dp(8), orientation="vertical", **kw):
    from kivy.graphics import Color, RoundedRectangle
    box = BoxLayout(
        orientation=orientation, padding=padding,
        spacing=spacing, size_hint_y=None, **kw
    )
    with box.canvas.before:
        Color(*C_CARD)
        box._bg = RoundedRectangle(radius=[dp(10)])
    def _update(inst, val):
        inst._bg.pos  = inst.pos
        inst._bg.size = inst.size
    box.bind(pos=_update, size=_update)
    box.bind(minimum_height=box.setter("height"))
    return box

class FlatBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal   = ""
        self.background_down     = ""
        self.background_disabled_normal = ""
        self.background_color    = kw.pop("bg_color", C_ACCENT)
        self.color               = C_TEXT
        self.font_size           = sp(14)
        self.bold                = True
        self.size_hint_y         = None
        self.height              = dp(46)

    def on_press(self):
        Animation(opacity=0.6, d=0.07).start(self)

    def on_release(self):
        Animation(opacity=1.0, d=0.12).start(self)


def make_divider():
    from kivy.graphics import Color, Rectangle
    box = BoxLayout(size_hint_y=None, height=dp(1))
    with box.canvas:
        Color(*C_BORDER)
        box._line = Rectangle(pos=box.pos, size=box.size)
    box.bind(pos=lambda i, v: setattr(i._line, "pos", v),
             size=lambda i, v: setattr(i._line, "size", v))
    return box

# ─────────────────────────────────────────────────────────────
#  SCREENS
# ─────────────────────────────────────────────────────────────

# ── 1. SPLASH SCREEN ─────────────────────────────────────────
class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self._go_main, 2.5)

    def _go_main(self, dt):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "studio"

    def build_ui(self):
        root = FloatLayout()
        from kivy.graphics import Color, Rectangle
        with root.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                  size=lambda i, v: setattr(i._bg, "size", v))

        box = BoxLayout(orientation="vertical", spacing=dp(16),
                        size_hint=(0.7, None), pos_hint={"center_x": 0.5, "center_y": 0.52})
        box.bind(minimum_height=box.setter("height"))

        if Path(APP_ICON).exists():
            img = Image(source=APP_ICON, size_hint=(1, None), height=dp(120))
            box.add_widget(img)

        title = make_label("Titan AI Studio Pro", 28, C_ACCENT, bold=True, halign="center")
        sub   = make_label(f"v{APP_VERSION}  ·  Voice Cloning Edition", 13, C_MUTED, halign="center")
        box.add_widget(title)
        box.add_widget(sub)

        pb = ProgressBar(max=100, value=0, size_hint=(1, None), height=dp(4))
        box.add_widget(pb)

        root.add_widget(box)

        def _anim(dt):
            def _tick(t):
                pb.value = min(100, pb.value + 2.5)
            for i in range(40):
                Clock.schedule_once(lambda dt, i=i: _tick(i), i * 0.06)

        Clock.schedule_once(_anim, 0.1)
        self.add_widget(root)


# ── 2. STUDIO SCREEN (main TTS + Voice Cloning) ──────────────
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.current_sound  = None
        self.is_generating  = False
        self.cloned_voice   = None   # path to reference WAV for cloning
        self._history       = load_history()

    def on_enter(self):
        if not self.children:
            self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = BoxLayout(orientation="vertical", spacing=0)
        with root.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                  size=lambda i, v: setattr(i._bg, "size", v))

        # ── Header
        hdr = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(16), 0])
        from kivy.graphics import Color, Rectangle
        with hdr.canvas.before:
            Color(*C_CARD)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                 size=lambda i, v: setattr(i._bg, "size", v))

        hdr_title = Label(text="[b]🎙️ Titan AI Studio Pro[/b]", markup=True,
                          font_size=sp(17), color=C_ACCENT, size_hint_x=1)
        hdr.add_widget(hdr_title)

        # History button
        hist_btn = FlatBtn(text="📋 History", size_hint=(None, None),
                           width=dp(110), height=dp(36), bg_color=C_CARD)
        hist_btn.bind(on_release=lambda x: self._go("history"))
        hdr.add_widget(hist_btn)

        # Admin button
        admin_btn = FlatBtn(text="👨‍💼 Admin", size_hint=(None, None),
                            width=dp(90), height=dp(36), bg_color=C_ADMIN)
        admin_btn.bind(on_release=lambda x: self._go("admin_login"))
        hdr.add_widget(admin_btn)

        root.add_widget(hdr)

        # ── Scrollable content
        sv = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(10),
                            padding=[dp(12), dp(12)], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        # ── Card: Model Selection
        card_model = make_card()
        card_model.add_widget(make_label("🤖 Voice Model", 13, C_MUTED))
        self.model_spinner = Spinner(
            text="English (Natural)",
            values=list(COQUI_MODELS.keys()),
            size_hint=(1, None), height=dp(44),
            background_color=C_CARD, color=C_TEXT, font_size=sp(14)
        )
        card_model.add_widget(self.model_spinner)
        content.add_widget(card_model)

        # ── Card: Voice Cloning
        card_clone = make_card()
        clone_title = BoxLayout(size_hint_y=None, height=dp(28))
        clone_title.add_widget(make_label("🎤 Voice Cloning", 13, C_MUTED))
        clone_badge = Label(text="NEW", font_size=sp(11), color=C_GREEN,
                            bold=True, size_hint_x=None, width=dp(40))
        clone_title.add_widget(clone_badge)
        card_clone.add_widget(clone_title)

        self.clone_status = make_label("No reference voice loaded — will use default voice", 12, C_MUTED)
        card_clone.add_widget(self.clone_status)

        clone_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        load_ref_btn = FlatBtn(text="📂 Load Voice Sample", bg_color=(0.2, 0.4, 0.2, 1))
        load_ref_btn.bind(on_release=self._load_reference_voice)
        clear_ref_btn = FlatBtn(text="✕ Clear", size_hint=(None, 1),
                                width=dp(70), bg_color=C_RED)
        clear_ref_btn.bind(on_release=self._clear_reference)
        clone_row.add_widget(load_ref_btn)
        clone_row.add_widget(clear_ref_btn)
        card_clone.add_widget(clone_row)

        card_clone.add_widget(make_label(
            "ℹ️ Load a 10-30 second WAV/MP3 of any voice.\nThe AI will clone that voice for your text.",
            11, C_MUTED
        ))
        content.add_widget(card_clone)

        # ── Card: Speed
        card_speed = make_card()
        card_speed.add_widget(make_label("⚡ Speed", 13, C_MUTED))
        self.speed_spinner = Spinner(
            text="Normal",
            values=list(SPEED_MAP.keys()),
            size_hint=(1, None), height=dp(44),
            background_color=C_CARD, color=C_TEXT, font_size=sp(14)
        )
        card_speed.add_widget(self.speed_spinner)
        content.add_widget(card_speed)

        # ── Card: Text Input
        card_text = make_card()
        card_text.add_widget(make_label("📝 Text to Speak", 13, C_MUTED))
        self.text_input = TextInput(
            hint_text="Type or paste your text here...",
            multiline=True, font_size=sp(14),
            background_color=(0.08, 0.08, 0.15, 1),
            foreground_color=C_TEXT,
            cursor_color=C_ACCENT,
            hint_text_color=C_MUTED,
            size_hint=(1, None), height=dp(160)
        )
        card_text.add_widget(self.text_input)

        # Import buttons
        import_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        for label in ["📄 TXT", "📋 PDF", "📝 DOCX"]:
            b = FlatBtn(text=label, bg_color=(0.15, 0.15, 0.25, 1))
            b.font_size = sp(12)
            ext = label.split()[-1].lower()
            b.bind(on_release=lambda x, e=ext: self._import_file(e))
            import_row.add_widget(b)
        card_text.add_widget(import_row)
        content.add_widget(card_text)

        # ── Card: Output Format
        card_fmt = make_card()
        card_fmt.add_widget(make_label("💾 Output Format", 13, C_MUTED))
        fmt_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.fmt_mp3 = FlatBtn(text="MP3", bg_color=C_ACCENT)
        self.fmt_wav = FlatBtn(text="WAV", bg_color=(0.15, 0.15, 0.25, 1))
        self.fmt_mp3.bind(on_release=lambda x: self._set_format("mp3"))
        self.fmt_wav.bind(on_release=lambda x: self._set_format("wav"))
        fmt_row.add_widget(self.fmt_mp3)
        fmt_row.add_widget(self.fmt_wav)
        card_fmt.add_widget(fmt_row)
        self._output_format = "mp3"
        content.add_widget(card_fmt)

        # ── Status
        self.status_label = make_label("Ready — enter text and tap Generate", 13,
                                       C_MUTED, halign="center")
        content.add_widget(self.status_label)

        # ── Progress bar
        self.progress = ProgressBar(max=100, value=0, size_hint=(1, None), height=dp(5))
        content.add_widget(self.progress)

        # ── Generate button
        self.gen_btn = FlatBtn(text="⚡ Generate Audio", bg_color=C_ACCENT)
        self.gen_btn.height = dp(54)
        self.gen_btn.font_size = sp(17)
        self.gen_btn.bind(on_release=self._start_generate)
        content.add_widget(self.gen_btn)

        # ── Preview + Download row
        action_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self.preview_btn = FlatBtn(text="▶ Preview", bg_color=(0.10, 0.35, 0.20, 1))
        self.preview_btn.bind(on_release=self._preview_audio)
        self.download_btn = FlatBtn(text="⬇ Download", bg_color=C_GREEN)
        self.download_btn.bind(on_release=self._download_audio)
        action_row.add_widget(self.preview_btn)
        action_row.add_widget(self.download_btn)
        content.add_widget(action_row)

        sv.add_widget(content)
        root.add_widget(sv)
        self.add_widget(root)
        self._last_audio = None

    # ── Navigation
    def _go(self, screen):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = screen

    # ── Format selection
    def _set_format(self, fmt):
        self._output_format = fmt
        self.fmt_mp3.background_color = C_ACCENT if fmt == "mp3" else (0.15, 0.15, 0.25, 1)
        self.fmt_wav.background_color = C_ACCENT if fmt == "wav" else (0.15, 0.15, 0.25, 1)

    # ── Reference voice
    def _load_reference_voice(self, *a):
        try:
            from plyer import filechooser
            filechooser.open_file(
                title="Select Voice Sample (WAV/MP3)",
                filters=["*.wav", "*.mp3"],
                on_selection=self._on_ref_selected
            )
        except Exception:
            self._show_popup("ℹ️ File Chooser",
                             "On desktop, put your reference WAV file at:\n"
                             f"{SAVE_DIR / 'reference.wav'}\n\n"
                             "The app will auto-detect it.")
            ref = SAVE_DIR / "reference.wav"
            if ref.exists():
                self.cloned_voice = str(ref)
                self.clone_status.text = f"✅ Reference loaded: reference.wav"

    def _on_ref_selected(self, selection):
        if selection:
            self.cloned_voice = selection[0]
            name = Path(self.cloned_voice).name
            self.clone_status.text = f"✅ Reference loaded: {name}"
            self.clone_status.color = C_GREEN

    def _clear_reference(self, *a):
        self.cloned_voice = None
        self.clone_status.text = "No reference voice — using default voice"
        self.clone_status.color = C_MUTED

    # ── File import
    def _import_file(self, ext):
        self._show_popup("📂 Import", f"Place your .{ext} file in:\n{SAVE_DIR}\n\nThen rename it to 'import.{ext}'")
        p = SAVE_DIR / f"import.{ext}"
        if not p.exists():
            return
        try:
            if ext == "txt":
                self.text_input.text = p.read_text(errors="replace")
            elif ext == "pdf":
                try:
                    import PyPDF2
                    with open(p, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        self.text_input.text = "\n".join(page.extract_text() or "" for page in reader.pages)
                except ImportError:
                    self._show_popup("Error", "PyPDF2 not installed. Run: pip install PyPDF2")
            elif ext == "docx":
                try:
                    import docx
                    doc = docx.Document(str(p))
                    self.text_input.text = "\n".join(para.text for para in doc.paragraphs)
                except ImportError:
                    self._show_popup("Error", "python-docx not installed. Run: pip install python-docx")
        except Exception as e:
            self._show_popup("Import Error", str(e))

    # ── Generate audio
    def _start_generate(self, *a):
        if self.is_generating:
            return
        text = self.text_input.text.strip()
        if len(text) < 3:
            self._show_popup("⚠️ Input Error", "Please enter at least 3 characters.")
            return
        self.is_generating = True
        self.gen_btn.text = "⏳ Generating..."
        self.gen_btn.disabled = True
        self.progress.value = 0
        self._set_status("⚡ Starting Coqui TTS engine...", C_ORANGE)
        threading.Thread(target=self._worker, args=(text,), daemon=True).start()

    def _worker(self, text):
        try:
            self._update_progress(10, "🔧 Loading TTS model...")
            model_id = COQUI_MODELS[self.model_spinner.text]
            speed    = SPEED_MAP[self.speed_spinner.text]
            ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname    = f"Titan_{ts}.{self._output_format}"
            out_path = str(SAVE_DIR / fname)

            try:
                from TTS.api import TTS
                self._update_progress(30, "🤖 Initializing model (first run downloads ~200MB)...")
                tts = TTS(model_id)

                self._update_progress(60, "🎤 Synthesizing speech...")
                if self.cloned_voice and "xtts" in model_id.lower():
                    # ── Voice cloning mode (XTTS v2)
                    tts.tts_to_file(
                        text=text,
                        speaker_wav=self.cloned_voice,
                        language="en",
                        file_path=out_path,
                        speed=speed,
                    )
                else:
                    # ── Standard synthesis
                    tts.tts_to_file(text=text, file_path=out_path, speed=speed)

            except ImportError:
                # ── Fallback: gTTS (if Coqui not installed)
                self._update_progress(40, "⚠️ Coqui not found, using gTTS fallback...")
                from gtts import gTTS
                slow = (speed < 0.9)
                out_mp3 = out_path.replace(".wav", ".mp3")
                gTTS(text=text, slow=slow).save(out_mp3)
                out_path = out_mp3
                fname    = Path(out_mp3).name

            self._update_progress(90, "✅ Audio ready!")
            self._last_audio = out_path

            # Save history
            entry = {
                "filename" : fname,
                "path"     : out_path,
                "text"     : text[:120],
                "voice"    : self.model_spinner.text,
                "cloned"   : bool(self.cloned_voice),
                "format"   : self._output_format,
                "date"     : datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            self._history.insert(0, entry)
            self._history = self._history[:100]
            save_history(self._history)
            log_admin("generate", {
                "model": self.model_spinner.text,
                "cloned": bool(self.cloned_voice),
                "chars": len(text)
            })

            Clock.schedule_once(lambda dt: self._on_success(fname), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._on_error(err), 0)

    def _on_success(self, fname):
        self.is_generating = False
        self.gen_btn.disabled = False
        self.gen_btn.text = "⚡ Generate Audio"
        self.progress.value = 100
        self._set_status(f"✅ Generated: {fname}", C_GREEN)

    def _on_error(self, err):
        self.is_generating = False
        self.gen_btn.disabled = False
        self.gen_btn.text = "⚡ Generate Audio"
        self.progress.value = 0
        self._set_status("❌ Error occurred", C_RED)
        self._show_popup("❌ Generation Error", f"{err}\n\nMake sure you installed:\npip install TTS")

    # ── Preview
    def _preview_audio(self, *a):
        if not self._last_audio or not Path(self._last_audio).exists():
            self._show_popup("⚠️", "No audio generated yet. Tap Generate first.")
            return
        try:
            if self.current_sound:
                self.current_sound.stop()
            self.current_sound = SoundLoader.load(self._last_audio)
            if self.current_sound:
                self.current_sound.play()
                self.preview_btn.text = "⏹ Playing..."
                Clock.schedule_once(lambda dt: setattr(self.preview_btn, "text", "▶ Preview"),
                                    self.current_sound.length + 0.5)
        except Exception as e:
            self._show_popup("Playback Error", str(e))

    # ── Download
    def _download_audio(self, *a):
        if not self._last_audio or not Path(self._last_audio).exists():
            self._show_popup("⚠️", "No audio generated yet.")
            return
        try:
            downloads = Path.home() / "Downloads"
            downloads.mkdir(exist_ok=True)
            dest = downloads / Path(self._last_audio).name
            shutil.copy2(self._last_audio, dest)
            self._show_popup("✅ Saved!", f"File saved to:\n{dest}")
            log_admin("download", {"file": str(dest)})
        except Exception as e:
            self._show_popup("Error", str(e))

    # ── Helpers
    def _update_progress(self, val, msg):
        Clock.schedule_once(lambda dt: (
            setattr(self.progress, "value", val),
            self._set_status(msg, C_ORANGE)
        ), 0)

    def _set_status(self, msg, color=None):
        self.status_label.text  = msg
        self.status_label.color = color or C_MUTED

    def _show_popup(self, title, msg):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(make_label(msg, 13))
        btn = FlatBtn(text="OK")
        popup = Popup(title=title, content=content,
                      size_hint=(0.88, None), height=dp(260),
                      title_color=C_ACCENT, separator_color=C_ACCENT,
                      background_color=C_CARD)
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()


# ── 3. HISTORY SCREEN ────────────────────────────────────────
class HistoryScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                  size=lambda i, v: setattr(i._bg, "size", v))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(52), padding=[dp(12), 0])
        with hdr.canvas.before:
            Color(*C_CARD)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                 size=lambda i, v: setattr(i._bg, "size", v))
        back = FlatBtn(text="← Back", size_hint=(None, None), width=dp(90), height=dp(36))
        back.bind(on_release=lambda x: self._go_back())
        hdr.add_widget(back)
        hdr.add_widget(make_label("📋 Download History", 16, C_ACCENT, bold=True))
        clr = FlatBtn(text="🗑 Clear All", size_hint=(None, None), width=dp(100), height=dp(36), bg_color=C_RED)
        clr.bind(on_release=self._confirm_clear)
        hdr.add_widget(clr)
        root.add_widget(hdr)

        sv = ScrollView()
        lst = BoxLayout(orientation="vertical", spacing=dp(6),
                        padding=[dp(10), dp(10)], size_hint_y=None)
        lst.bind(minimum_height=lst.setter("height"))

        history = load_history()
        if not history:
            lst.add_widget(make_label("No history yet. Generate some audio!", 14, C_MUTED, halign="center"))
        else:
            for i, h in enumerate(history):
                card = self._make_item(h, i)
                lst.add_widget(card)
                Animation(opacity=1, d=0.3, t="out_quad").start(card)

        sv.add_widget(lst)
        root.add_widget(sv)
        self.add_widget(root)

    def _make_item(self, h, idx):
        card = make_card(padding=dp(10))
        card.opacity = 0
        row = BoxLayout(size_hint_y=None, height=dp(28))
        icon = "🎵" if h.get("cloned") else "🔊"
        row.add_widget(make_label(f"{icon} {h.get('filename', 'Unknown')}", 13, C_TEXT, bold=True))
        row.add_widget(make_label(h.get("date", ""), 11, C_MUTED, halign="right"))
        card.add_widget(row)
        card.add_widget(make_label(f"Model: {h.get('voice','?')} | Format: {h.get('format','mp3').upper()}", 11, C_MUTED))
        card.add_widget(make_label(f'"{h.get("text","")[:80]}..."', 11, C_MUTED))

        btn_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        play_btn = FlatBtn(text="▶ Play", bg_color=(0.10, 0.35, 0.20, 1))
        play_btn.bind(on_release=lambda x, p=h.get("path", ""): self._play(p))
        btn_row.add_widget(play_btn)

        dl_btn = FlatBtn(text="⬇", size_hint=(None, 1), width=dp(44), bg_color=C_GREEN)
        dl_btn.bind(on_release=lambda x, p=h.get("path", ""): self._download(p))
        btn_row.add_widget(dl_btn)
        card.add_widget(btn_row)
        return card

    def _play(self, path):
        if not path or not Path(path).exists():
            return
        try:
            s = SoundLoader.load(path)
            if s:
                s.play()
        except Exception:
            pass

    def _download(self, path):
        if not path or not Path(path).exists():
            return
        try:
            dest = Path.home() / "Downloads" / Path(path).name
            shutil.copy2(path, dest)
        except Exception as e:
            print(f"Download error: {e}")

    def _confirm_clear(self, *a):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(make_label("Clear all history? Files will not be deleted.", 13))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        popup = Popup(title="Confirm Clear", content=content,
                      size_hint=(0.8, None), height=dp(220),
                      title_color=C_RED, background_color=C_CARD)
        yes_btn = FlatBtn(text="Yes, Clear", bg_color=C_RED)
        no_btn  = FlatBtn(text="Cancel", bg_color=C_CARD)
        yes_btn.bind(on_release=lambda x: (save_history([]), popup.dismiss(), self.on_enter()))
        no_btn.bind(on_release=popup.dismiss)
        row.add_widget(yes_btn)
        row.add_widget(no_btn)
        content.add_widget(row)
        popup.open()

    def _go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "studio"


# ── 4. ADMIN LOGIN SCREEN ─────────────────────────────────────
class AdminLoginScreen(Screen):
    def on_enter(self):
        if not self.children:
            self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = FloatLayout()
        with root.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                  size=lambda i, v: setattr(i._bg, "size", v))

        box = BoxLayout(orientation="vertical", spacing=dp(14),
                        padding=[dp(24), dp(24)], size_hint=(0.85, None),
                        pos_hint={"center_x": 0.5, "center_y": 0.55})
        box.bind(minimum_height=box.setter("height"))

        box.add_widget(make_label("👨‍💼 Admin Dashboard", 22, C_ADMIN, bold=True, halign="center"))
        box.add_widget(make_label("Enter admin password to continue", 13, C_MUTED, halign="center"))
        box.add_widget(make_divider())

        self.pw_input = TextInput(
            hint_text="Password",
            password=True, multiline=False,
            font_size=sp(16),
            background_color=(0.08, 0.08, 0.15, 1),
            foreground_color=C_TEXT,
            cursor_color=C_ADMIN,
            hint_text_color=C_MUTED,
            size_hint=(1, None), height=dp(48)
        )
        box.add_widget(self.pw_input)

        self.err_label = make_label("", 12, C_RED, halign="center")
        box.add_widget(self.err_label)

        login_btn = FlatBtn(text="🔓 Login", bg_color=C_ADMIN)
        login_btn.bind(on_release=self._login)
        box.add_widget(login_btn)

        back_btn = FlatBtn(text="← Back", bg_color=C_CARD)
        back_btn.bind(on_release=self._back)
        box.add_widget(back_btn)

        root.add_widget(box)
        self.add_widget(root)

    def _login(self, *a):
        pw = self.pw_input.text.strip()
        if pw == ADMIN_PASS:
            log_admin("admin_login", {"status": "success"})
            self.pw_input.text = ""
            self.err_label.text = ""
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "admin_dashboard"
        else:
            self.err_label.text = "❌ Incorrect password"
            log_admin("admin_login", {"status": "failed"})

    def _back(self, *a):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "studio"


# ── 5. ADMIN DASHBOARD SCREEN ────────────────────────────────
class AdminDashboardScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                  size=lambda i, v: setattr(i._bg, "size", v))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(52), padding=[dp(12), 0])
        with hdr.canvas.before:
            Color(*C_CARD)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                 size=lambda i, v: setattr(i._bg, "size", v))
        back = FlatBtn(text="← Logout", size_hint=(None, None), width=dp(100), height=dp(36))
        back.bind(on_release=self._logout)
        hdr.add_widget(back)
        hdr.add_widget(make_label("👨‍💼 Admin Dashboard", 16, C_ADMIN, bold=True))
        hdr.add_widget(Label(size_hint_x=None, width=dp(12)))
        root.add_widget(hdr)

        sv   = ScrollView()
        cont = BoxLayout(orientation="vertical", spacing=dp(10),
                         padding=[dp(10), dp(10)], size_hint_y=None)
        cont.bind(minimum_height=cont.setter("height"))

        stats = get_stats()

        # ── Stats cards
        stats_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(120))
        for label, value, color in [
            ("Total Generated", str(stats["total_generated"]), C_GREEN),
            ("Storage Used",    f"{stats['total_size_mb']} MB", C_ACCENT),
            ("App Version",     f"v{stats['app_version']}", C_ORANGE),
            ("History Items",   str(stats["history_count"]), C_ACCENT2),
        ]:
            c = make_card(padding=dp(8))
            c.add_widget(make_label(label, 11, C_MUTED, halign="center"))
            c.add_widget(make_label(value, 22, color, bold=True, halign="center"))
            stats_grid.add_widget(c)
        cont.add_widget(stats_grid)

        # ── Top voices used
        if stats["voices_used"]:
            vc = make_card()
            vc.add_widget(make_label("🎤 Top Voices Used", 13, C_ADMIN, bold=True))
            vc.add_widget(make_divider())
            for voice, count in sorted(stats["voices_used"].items(), key=lambda x: -x[1])[:5]:
                row = BoxLayout(size_hint_y=None, height=dp(26))
                row.add_widget(make_label(voice, 12, C_TEXT))
                row.add_widget(make_label(f"×{count}", 12, C_GREEN, halign="right"))
                vc.add_widget(row)
            cont.add_widget(vc)

        # ── Recent activity log
        log_card = make_card()
        log_card.add_widget(make_label("📋 Recent Activity", 13, C_ADMIN, bold=True))
        log_card.add_widget(make_divider())
        for entry in stats["recent_events"][:15]:
            ts    = entry.get("ts", "")[:16].replace("T", " ")
            event = entry.get("event", "?")
            data  = entry.get("data", {})
            detail = ""
            if event == "generate":
                detail = f"Model: {data.get('model','?')} | Chars: {data.get('chars','?')}"
            elif event == "download":
                detail = f"File: {Path(data.get('file','')).name}"
            elif event == "admin_login":
                detail = f"Status: {data.get('status','?')}"
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
            row.add_widget(make_label(f"[{ts}] {event}", 11, C_MUTED))
            row.add_widget(make_label(detail, 11, C_TEXT, halign="right"))
            log_card.add_widget(row)
            log_card.add_widget(make_divider())
        cont.add_widget(log_card)

        # ── Admin actions
        actions_card = make_card()
        actions_card.add_widget(make_label("⚙️ Admin Actions", 13, C_ADMIN, bold=True))

        export_btn = FlatBtn(text="📤 Export Logs to TXT", bg_color=(0.15, 0.25, 0.40, 1))
        export_btn.bind(on_release=self._export_logs)
        actions_card.add_widget(export_btn)

        clear_log_btn = FlatBtn(text="🗑 Clear Admin Log", bg_color=C_RED)
        clear_log_btn.bind(on_release=self._clear_log)
        actions_card.add_widget(clear_log_btn)

        cont.add_widget(actions_card)
        sv.add_widget(cont)
        root.add_widget(sv)
        self.add_widget(root)

    def _logout(self, *a):
        log_admin("admin_logout")
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "studio"

    def _export_logs(self, *a):
        try:
            out = SAVE_DIR / f"admin_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            log = json.loads(Path(ADMIN_LOG).read_text()) if Path(ADMIN_LOG).exists() else []
            lines = [f"[{e['ts']}] {e['event']} — {json.dumps(e['data'])}" for e in log]
            out.write_text("\n".join(lines))
            self._msg(f"Exported to:\n{out}")
        except Exception as e:
            self._msg(f"Export error: {e}")

    def _clear_log(self, *a):
        try:
            Path(ADMIN_LOG).write_text("[]")
            self._msg("Admin log cleared.")
            self.on_enter()
        except Exception as e:
            self._msg(str(e))

    def _msg(self, msg):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(make_label(msg, 13))
        btn = FlatBtn(text="OK")
        popup = Popup(title="Admin", content=content,
                      size_hint=(0.85, None), height=dp(220),
                      title_color=C_ADMIN, background_color=C_CARD)
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()


# ─────────────────────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────────────────────
class TitanApp(App):
    title = "Titan AI Studio Pro"

    def build(self):
        sm = ScreenManager()

        splash = SplashScreen(name="splash")
        splash.build_ui()
        sm.add_widget(splash)

        sm.add_widget(StudioScreen(name="studio"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(AdminLoginScreen(name="admin_login"))
        sm.add_widget(AdminDashboardScreen(name="admin_dashboard"))

        sm.current = "splash"
        log_admin("app_launch", {"version": APP_VERSION})
        return sm

    def get_application_icon(self):
        return APP_ICON if Path(APP_ICON).exists() else ""


if __name__ == "__main__":
    TitanApp().run()
