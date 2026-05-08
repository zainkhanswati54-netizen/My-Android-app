# =============================================================
#  Titan AI Studio Pro — main.py  v7.1.0  CRASH FIXED
# =============================================================

import os, json, threading, time, shutil, datetime
from pathlib import Path

# ── Kivy config MUST be before any kivy import ───────────────
os.environ["KIVY_NO_ENV_CONFIG"] = "1"
os.environ["KIVY_AUDIO"] = "android"   # Fix audio on Android

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.animation import Animation

# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────
APP_VERSION  = "7.1.0"
HISTORY_FILE = "history.json"
ADMIN_LOG    = "admin_log.json"
ADMIN_PASS   = "titan2026"
APP_ICON     = "AI.png"

SPEED_MAP = {"Slow": True, "Normal": False, "Fast": False}

# ─────────────────────────────────────────────────────────────
#  SAFE STORAGE PATH
# ─────────────────────────────────────────────────────────────
def get_save_dir():
    """
    FIX #1: Android pe /sdcard crash karta hai without permission.
    App-private directory use karo — no permission needed.
    """
    from kivy.app import App as _App
    try:
        app = _App.get_running_app()
        if app and hasattr(app, 'user_data_dir'):
            p = Path(app.user_data_dir) / "audio"
            p.mkdir(parents=True, exist_ok=True)
            return p
    except Exception:
        pass
    # Fallback
    p = Path(os.getcwd()) / "TitanAI_output"
    p.mkdir(parents=True, exist_ok=True)
    return p

# ─────────────────────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────────────────────
def load_history():
    try:
        f = Path(HISTORY_FILE)
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []

def save_history(history):
    try:
        Path(HISTORY_FILE).write_text(
            json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        print(f"[History] {e}")

def log_admin(event, data=None):
    try:
        log = []
        p = Path(ADMIN_LOG)
        if p.exists():
            log = json.loads(p.read_text(encoding="utf-8"))
        log.append({
            "ts": datetime.datetime.now().isoformat(),
            "event": event,
            "data": data or {}
        })
        p.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[AdminLog] {e}")

def get_stats():
    history = load_history()
    log = []
    try:
        if Path(ADMIN_LOG).exists():
            log = json.loads(Path(ADMIN_LOG).read_text(encoding="utf-8"))
    except Exception:
        pass
    voices = {}
    for h in history:
        v = h.get("voice", "gTTS")
        voices[v] = voices.get(v, 0) + 1
    return {
        "total_generated": len(history),
        "voices_used": voices,
        "recent_events": log[-20:][::-1],
        "app_version": APP_VERSION,
        "history_count": len(history),
    }

# ─────────────────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────────────────
C_BG     = (0.07, 0.07, 0.12, 1)
C_CARD   = (0.12, 0.12, 0.20, 1)
C_ACCENT = (0.22, 0.47, 1.00, 1)
C_GREEN  = (0.18, 0.80, 0.55, 1)
C_RED    = (0.95, 0.30, 0.30, 1)
C_ORANGE = (1.00, 0.60, 0.15, 1)
C_TEXT   = (0.95, 0.95, 0.98, 1)
C_MUTED  = (0.58, 0.58, 0.70, 1)
C_BORDER = (0.22, 0.22, 0.35, 1)
C_ADMIN  = (0.90, 0.60, 0.10, 1)

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

def make_card(**kw):
    from kivy.graphics import Color, RoundedRectangle
    box = BoxLayout(
        orientation="vertical",
        padding=dp(12), spacing=dp(8),
        size_hint_y=None, **kw
    )
    with box.canvas.before:
        Color(*C_CARD)
        box._bg = RoundedRectangle(radius=[dp(10)])
    box.bind(
        pos=lambda i, v: setattr(i._bg, "pos", v),
        size=lambda i, v: setattr(i._bg, "size", v),
        minimum_height=box.setter("height")
    )
    return box

class FlatBtn(Button):
    def __init__(self, bg_color=None, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_down   = ""
        self.background_color  = bg_color or C_ACCENT
        self.color             = C_TEXT
        self.font_size         = sp(14)
        self.bold              = True
        self.size_hint_y       = None
        self.height            = dp(46)

def make_bg(widget):
    """Attach dark background to any widget."""
    from kivy.graphics import Color, Rectangle
    with widget.canvas.before:
        Color(*C_BG)
        widget._bg = __import__('kivy').graphics.Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(
        pos=lambda i, v: setattr(i._bg, "pos", v),
        size=lambda i, v: setattr(i._bg, "size", v)
    )

# ─────────────────────────────────────────────────────────────
#  SCREEN 1 — SPLASH
# ─────────────────────────────────────────────────────────────
class SplashScreen(Screen):
    def on_enter(self):
        self._build()
        Clock.schedule_once(self._go_main, 2.5)

    def _go_main(self, dt):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "studio"

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = FloatLayout()
        with root.canvas.before:
            Color(*C_BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(bg,"pos",v),
                  size=lambda i,v: setattr(bg,"size",v))

        box = BoxLayout(
            orientation="vertical", spacing=dp(16),
            size_hint=(0.75, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        box.bind(minimum_height=box.setter("height"))

        # App icon (safe load)
        if Path(APP_ICON).exists():
            from kivy.uix.image import Image
            box.add_widget(Image(source=APP_ICON, size_hint=(1,None), height=dp(110)))

        box.add_widget(make_label("Titan AI Studio Pro", 26, C_ACCENT, bold=True, halign="center"))
        box.add_widget(make_label(f"v{APP_VERSION}  ·  TTS Edition", 13, C_MUTED, halign="center"))

        pb = ProgressBar(max=100, value=0, size_hint=(1,None), height=dp(4))
        box.add_widget(pb)
        root.add_widget(box)
        self.add_widget(root)

        # Animate progress bar
        for i in range(40):
            Clock.schedule_once(lambda dt, i=i: setattr(pb, "value", min(100, pb.value + 2.5)), i * 0.06)


# ─────────────────────────────────────────────────────────────
#  SCREEN 2 — STUDIO (Main TTS)
# ─────────────────────────────────────────────────────────────
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.current_sound = None
        self.is_generating = False
        self._last_audio   = None
        self._history      = load_history()
        self._fmt          = "mp3"

    def on_enter(self):
        if not self.children:
            self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*C_BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(bg,"pos",v),
                  size=lambda i,v: setattr(bg,"size",v))

        # ── Header
        hdr = BoxLayout(size_hint_y=None, height=dp(54), padding=[dp(12),0], spacing=dp(6))
        with hdr.canvas.before:
            Color(*C_CARD)
            hbg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i,v: setattr(hbg,"pos",v),
                 size=lambda i,v: setattr(hbg,"size",v))
        hdr.add_widget(Label(text="[b]🎙️ Titan AI Studio[/b]", markup=True,
                             font_size=sp(16), color=C_ACCENT))
        h_btn = FlatBtn(text="📋", size_hint=(None,None), width=dp(46), height=dp(36), bg_color=C_CARD)
        h_btn.bind(on_release=lambda x: self._go("history"))
        a_btn = FlatBtn(text="👨‍💼", size_hint=(None,None), width=dp(46), height=dp(36), bg_color=C_ADMIN)
        a_btn.bind(on_release=lambda x: self._go("admin_login"))
        hdr.add_widget(h_btn)
        hdr.add_widget(a_btn)
        root.add_widget(hdr)

        # ── Scroll content
        sv = ScrollView()
        c  = BoxLayout(orientation="vertical", spacing=dp(10),
                       padding=[dp(12),dp(12)], size_hint_y=None)
        c.bind(minimum_height=c.setter("height"))

        # Language
        lang_card = make_card()
        lang_card.add_widget(make_label("🌐 Language", 12, C_MUTED))
        self.lang_spin = Spinner(
            text="English",
            values=["English","Urdu","Hindi","Arabic","French",
                    "Spanish","German","Turkish","Russian","Chinese","Japanese","Korean"],
            size_hint=(1,None), height=dp(44),
            background_color=C_CARD, color=C_TEXT, font_size=sp(14)
        )
        lang_card.add_widget(self.lang_spin)
        c.add_widget(lang_card)

        # Speed
        spd_card = make_card()
        spd_card.add_widget(make_label("⚡ Speed", 12, C_MUTED))
        self.spd_spin = Spinner(
            text="Normal", values=["Slow","Normal","Fast"],
            size_hint=(1,None), height=dp(44),
            background_color=C_CARD, color=C_TEXT, font_size=sp(14)
        )
        spd_card.add_widget(self.spd_spin)
        c.add_widget(spd_card)

        # Text input
        txt_card = make_card()
        txt_card.add_widget(make_label("📝 Text to Speak", 12, C_MUTED))
        self.txt_in = TextInput(
            hint_text="Yahan apna text likhein...",
            multiline=True, font_size=sp(14),
            background_color=(0.08,0.08,0.15,1),
            foreground_color=C_TEXT,
            cursor_color=C_ACCENT,
            hint_text_color=C_MUTED,
            size_hint=(1,None), height=dp(160)
        )
        txt_card.add_widget(self.txt_in)

        # Import buttons
        imp_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        for ext in ["txt","pdf","docx"]:
            b = FlatBtn(text=f"📄 {ext.upper()}", bg_color=(0.15,0.15,0.25,1))
            b.font_size = sp(12)
            b.bind(on_release=lambda x, e=ext: self._import(e))
            imp_row.add_widget(b)
        txt_card.add_widget(imp_row)
        c.add_widget(txt_card)

        # Format
        fmt_card = make_card()
        fmt_card.add_widget(make_label("💾 Format", 12, C_MUTED))
        fmt_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        self.btn_mp3 = FlatBtn(text="MP3", bg_color=C_ACCENT)
        self.btn_wav = FlatBtn(text="WAV", bg_color=(0.15,0.15,0.25,1))
        self.btn_mp3.bind(on_release=lambda x: self._set_fmt("mp3"))
        self.btn_wav.bind(on_release=lambda x: self._set_fmt("wav"))
        fmt_row.add_widget(self.btn_mp3)
        fmt_row.add_widget(self.btn_wav)
        fmt_card.add_widget(fmt_row)
        c.add_widget(fmt_card)

        # Status + Progress
        self.status_lbl = make_label("✅ Ready — text likhein aur Generate dabayein", 13, C_MUTED, halign="center")
        c.add_widget(self.status_lbl)
        self.prog = ProgressBar(max=100, value=0, size_hint=(1,None), height=dp(5))
        c.add_widget(self.prog)

        # Generate
        self.gen_btn = FlatBtn(text="⚡ Generate Audio", bg_color=C_ACCENT)
        self.gen_btn.height = dp(52)
        self.gen_btn.font_size = sp(16)
        self.gen_btn.bind(on_release=self._generate)
        c.add_widget(self.gen_btn)

        # Preview + Download
        act_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        prev_btn = FlatBtn(text="▶ Preview", bg_color=(0.10,0.35,0.20,1))
        prev_btn.bind(on_release=self._preview)
        dl_btn = FlatBtn(text="⬇ Save", bg_color=C_GREEN)
        dl_btn.bind(on_release=self._download)
        act_row.add_widget(prev_btn)
        act_row.add_widget(dl_btn)
        c.add_widget(act_row)

        sv.add_widget(c)
        root.add_widget(sv)
        self.add_widget(root)

    # ── Helpers
    def _go(self, s):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = s

    def _set_fmt(self, f):
        self._fmt = f
        self.btn_mp3.background_color = C_ACCENT if f=="mp3" else (0.15,0.15,0.25,1)
        self.btn_wav.background_color = C_ACCENT if f=="wav" else (0.15,0.15,0.25,1)

    def _set_status(self, msg, color=None):
        # FIX #2: Always update UI on main thread via Clock
        def _do(dt):
            self.status_lbl.text  = msg
            self.status_lbl.color = color or C_MUTED
        Clock.schedule_once(_do, 0)

    def _set_prog(self, v):
        Clock.schedule_once(lambda dt: setattr(self.prog, "value", v), 0)

    def _popup(self, title, msg):
        def _do(dt):
            box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
            box.add_widget(make_label(msg, 13))
            btn = FlatBtn(text="OK")
            p = Popup(title=title, content=box,
                      size_hint=(0.88,None), height=dp(280),
                      title_color=C_ACCENT, background_color=C_CARD)
            btn.bind(on_release=p.dismiss)
            box.add_widget(btn)
            p.open()
        Clock.schedule_once(_do, 0)

    # ── File import
    def _import(self, ext):
        # FIX #3: Safe file import with proper error handling
        try:
            from android.storage import primary_external_storage_path  # type: ignore
            base = Path(primary_external_storage_path()) / "TitanAI"
        except Exception:
            base = Path(os.getcwd())

        p = base / f"import.{ext}"
        if not p.exists():
            self._popup("📂 Import",
                        f"File nahi mila!\n\nYeh file rakho:\n{p}\n\nPhir dobara try karein.")
            return
        try:
            if ext == "txt":
                self.txt_in.text = p.read_text(errors="replace")
            elif ext == "pdf":
                import PyPDF2
                with open(p,"rb") as f:
                    r = PyPDF2.PdfReader(f)
                    self.txt_in.text = "\n".join(pg.extract_text() or "" for pg in r.pages)
            elif ext == "docx":
                import docx
                doc = docx.Document(str(p))
                self.txt_in.text = "\n".join(pr.text for pr in doc.paragraphs)
        except ImportError as e:
            self._popup("Error", f"Library missing:\n{e}")
        except Exception as e:
            self._popup("Import Error", str(e))

    # ── Generate Audio
    def _generate(self, *a):
        if self.is_generating:
            return
        text = self.txt_in.text.strip()
        if len(text) < 3:
            self._popup("⚠️", "Kam se kam 3 characters likhein.")
            return
        self.is_generating = True
        self.gen_btn.disabled = True
        self.gen_btn.text = "⏳ Ban raha hai..."
        self._set_prog(0)
        self._set_status("🔄 Shuru ho raha hai...", C_ORANGE)
        threading.Thread(target=self._worker, args=(text,), daemon=True).start()

    def _worker(self, text):
        """
        FIX #4: Coqui TTS Android pe crash karta hai.
        Sirf gTTS use karo Android pe — reliable aur lightweight.
        """
        try:
            self._set_prog(20)
            self._set_status("📦 TTS engine load ho raha hai...", C_ORANGE)

            lang_map = {
                "English":"en","Urdu":"ur","Hindi":"hi","Arabic":"ar",
                "French":"fr","Spanish":"es","German":"de","Turkish":"tr",
                "Russian":"ru","Chinese":"zh","Japanese":"ja","Korean":"ko",
            }
            lang = lang_map.get(self.lang_spin.text, "en")
            slow = (self.spd_spin.text == "Slow")

            save_dir = get_save_dir()
            ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"Titan_{ts}.mp3"   # gTTS always produces MP3
            out   = str(save_dir / fname)

            self._set_prog(40)
            self._set_status("🎤 Audio ban raha hai...", C_ORANGE)

            # FIX #5: gTTS needs internet — check connectivity gracefully
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(out)

            self._set_prog(90)
            self._last_audio = out

            entry = {
                "filename": fname,
                "path": out,
                "text": text[:120],
                "voice": f"gTTS-{self.lang_spin.text}",
                "format": "mp3",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            self._history.insert(0, entry)
            self._history = self._history[:100]
            save_history(self._history)
            log_admin("generate", {"lang": lang, "chars": len(text)})

            Clock.schedule_once(lambda dt: self._done(fname), 0)

        except Exception as e:
            err = str(e)
            # FIX #6: Network error ko clearly batao
            if "network" in err.lower() or "connection" in err.lower() or "failed" in err.lower():
                err = "Internet connection nahi hai!\ngTTS ke liye internet chahiye.\nWi-Fi ya mobile data on karein."
            Clock.schedule_once(lambda dt, e=err: self._fail(e), 0)

    def _done(self, fname):
        self.is_generating = False
        self.gen_btn.disabled = False
        self.gen_btn.text = "⚡ Generate Audio"
        self._set_prog(100)
        self._set_status(f"✅ Tayyar: {fname}", C_GREEN)

    def _fail(self, err):
        self.is_generating = False
        self.gen_btn.disabled = False
        self.gen_btn.text = "⚡ Generate Audio"
        self._set_prog(0)
        self._set_status("❌ Error aaya", C_RED)
        self._popup("❌ Error", err)

    # ── Preview
    def _preview(self, *a):
        if not self._last_audio or not Path(self._last_audio).exists():
            self._popup("⚠️", "Pehle audio generate karein.")
            return
        try:
            if self.current_sound:
                self.current_sound.stop()
            self.current_sound = SoundLoader.load(self._last_audio)
            if self.current_sound:
                self.current_sound.play()
        except Exception as e:
            self._popup("Playback Error", str(e))

    # ── Download / Save
    def _download(self, *a):
        if not self._last_audio or not Path(self._last_audio).exists():
            self._popup("⚠️", "Pehle audio generate karein.")
            return
        try:
            # Try Downloads folder, fall back to app dir
            try:
                from android.storage import primary_external_storage_path  # type: ignore
                dl = Path(primary_external_storage_path()) / "Download"
            except Exception:
                dl = Path.home() / "Downloads"
            dl.mkdir(parents=True, exist_ok=True)
            dest = dl / Path(self._last_audio).name
            shutil.copy2(self._last_audio, dest)
            self._popup("✅ Saved!", f"File save ho gayi:\n{dest}")
            log_admin("download", {"file": str(dest)})
        except Exception as e:
            self._popup("Save Error", str(e))


# ─────────────────────────────────────────────────────────────
#  SCREEN 3 — HISTORY
# ─────────────────────────────────────────────────────────────
class HistoryScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*C_BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(bg,"pos",v),
                  size=lambda i,v: setattr(bg,"size",v))

        hdr = BoxLayout(size_hint_y=None, height=dp(52), padding=[dp(10),0], spacing=dp(6))
        with hdr.canvas.before:
            Color(*C_CARD)
            hbg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i,v: setattr(hbg,"pos",v),
                 size=lambda i,v: setattr(hbg,"size",v))
        back = FlatBtn(text="← Wapas", size_hint=(None,None), width=dp(90), height=dp(36))
        back.bind(on_release=lambda x: self._back())
        hdr.add_widget(back)
        hdr.add_widget(make_label("📋 History", 15, C_ACCENT, bold=True))
        clr = FlatBtn(text="🗑 Clear", size_hint=(None,None), width=dp(80), height=dp(36), bg_color=C_RED)
        clr.bind(on_release=self._clear)
        hdr.add_widget(clr)
        root.add_widget(hdr)

        sv = ScrollView()
        lst = BoxLayout(orientation="vertical", spacing=dp(6),
                        padding=[dp(10),dp(10)], size_hint_y=None)
        lst.bind(minimum_height=lst.setter("height"))

        history = load_history()
        if not history:
            lst.add_widget(make_label("Abhi koi history nahi.\nAudio generate karein!", 14, C_MUTED, halign="center"))
        else:
            for h in history:
                card = make_card(padding=dp(10))
                card.add_widget(make_label(f"🎵 {h.get('filename','?')}", 13, C_TEXT, bold=True))
                card.add_widget(make_label(f"{h.get('date','')}  |  {h.get('voice','?')}", 11, C_MUTED))
                card.add_widget(make_label(f'"{h.get("text","")[:70]}..."', 11, C_MUTED))
                btn_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
                pb = FlatBtn(text="▶ Play", bg_color=(0.10,0.35,0.20,1))
                pb.bind(on_release=lambda x, p=h.get("path",""): self._play(p))
                db = FlatBtn(text="⬇", size_hint=(None,1), width=dp(44), bg_color=C_GREEN)
                db.bind(on_release=lambda x, p=h.get("path",""): self._dl(p))
                btn_row.add_widget(pb)
                btn_row.add_widget(db)
                card.add_widget(btn_row)
                lst.add_widget(card)

        sv.add_widget(lst)
        root.add_widget(sv)
        self.add_widget(root)

    def _play(self, path):
        try:
            if path and Path(path).exists():
                s = SoundLoader.load(path)
                if s: s.play()
        except Exception: pass

    def _dl(self, path):
        if not path or not Path(path).exists():
            return
        try:
            try:
                from android.storage import primary_external_storage_path  # type: ignore
                dl = Path(primary_external_storage_path()) / "Download"
            except Exception:
                dl = Path.home() / "Downloads"
            dl.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dl / Path(path).name)
        except Exception as e:
            print(f"DL error: {e}")

    def _clear(self, *a):
        save_history([])
        self.on_enter()

    def _back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "studio"


# ─────────────────────────────────────────────────────────────
#  SCREEN 4 — ADMIN LOGIN
# ─────────────────────────────────────────────────────────────
class AdminLoginScreen(Screen):
    def on_enter(self):
        if not self.children:
            self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = FloatLayout()
        with root.canvas.before:
            Color(*C_BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(bg,"pos",v),
                  size=lambda i,v: setattr(bg,"size",v))

        box = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(24),
                        size_hint=(0.85,None), pos_hint={"center_x":0.5,"center_y":0.55})
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(make_label("👨‍💼 Admin Login", 22, C_ADMIN, bold=True, halign="center"))

        self.pw = TextInput(
            hint_text="Password", password=True, multiline=False,
            font_size=sp(15), background_color=(0.08,0.08,0.15,1),
            foreground_color=C_TEXT, hint_text_color=C_MUTED,
            size_hint=(1,None), height=dp(48)
        )
        box.add_widget(self.pw)

        self.err = make_label("", 12, C_RED, halign="center")
        box.add_widget(self.err)

        lb = FlatBtn(text="🔓 Login", bg_color=C_ADMIN)
        lb.bind(on_release=self._login)
        box.add_widget(lb)

        bb = FlatBtn(text="← Wapas", bg_color=C_CARD)
        bb.bind(on_release=lambda x: self._back())
        box.add_widget(bb)

        root.add_widget(box)
        self.add_widget(root)

    def _login(self, *a):
        if self.pw.text.strip() == ADMIN_PASS:
            log_admin("admin_login", {"status": "ok"})
            self.pw.text = ""
            self.err.text = ""
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "admin_dashboard"
        else:
            self.err.text = "❌ Galat password"
            log_admin("admin_login", {"status": "failed"})

    def _back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "studio"


# ─────────────────────────────────────────────────────────────
#  SCREEN 5 — ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────
class AdminDashboardScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        from kivy.graphics import Color, Rectangle
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*C_BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(bg,"pos",v),
                  size=lambda i,v: setattr(bg,"size",v))

        hdr = BoxLayout(size_hint_y=None, height=dp(52), padding=[dp(10),0])
        with hdr.canvas.before:
            Color(*C_CARD)
            hbg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i,v: setattr(hbg,"pos",v),
                 size=lambda i,v: setattr(hbg,"size",v))
        back = FlatBtn(text="← Logout", size_hint=(None,None), width=dp(100), height=dp(36))
        back.bind(on_release=self._logout)
        hdr.add_widget(back)
        hdr.add_widget(make_label("👨‍💼 Admin Dashboard", 16, C_ADMIN, bold=True))
        root.add_widget(hdr)

        sv = ScrollView()
        c  = BoxLayout(orientation="vertical", spacing=dp(10),
                       padding=[dp(10),dp(10)], size_hint_y=None)
        c.bind(minimum_height=c.setter("height"))

        stats = get_stats()

        # Stats grid
        g = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(110))
        for lbl, val, col in [
            ("Total Generated", str(stats["total_generated"]), C_GREEN),
            ("App Version", f"v{stats['app_version']}", C_ACCENT),
            ("History Items", str(stats["history_count"]), C_ORANGE),
            ("Voices Used", str(len(stats["voices_used"])), (0.55,0.28,1,1)),
        ]:
            card = make_card(padding=dp(8))
            card.add_widget(make_label(lbl, 11, C_MUTED, halign="center"))
            card.add_widget(make_label(val, 20, col, bold=True, halign="center"))
            g.add_widget(card)
        c.add_widget(g)

        # Recent log
        log_card = make_card()
        log_card.add_widget(make_label("📋 Recent Activity", 13, C_ADMIN, bold=True))
        for e in stats["recent_events"][:10]:
            ts = e.get("ts","")[:16].replace("T"," ")
            ev = e.get("event","?")
            log_card.add_widget(make_label(f"[{ts}]  {ev}", 11, C_MUTED))
        c.add_widget(log_card)

        # Actions
        act_card = make_card()
        act_card.add_widget(make_label("⚙️ Actions", 13, C_ADMIN, bold=True))
        clr_btn = FlatBtn(text="🗑 Log Clear Karein", bg_color=C_RED)
        clr_btn.bind(on_release=self._clear_log)
        act_card.add_widget(clr_btn)
        c.add_widget(act_card)

        sv.add_widget(c)
        root.add_widget(sv)
        self.add_widget(root)

    def _logout(self, *a):
        log_admin("admin_logout")
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "studio"

    def _clear_log(self, *a):
        try:
            Path(ADMIN_LOG).write_text("[]", encoding="utf-8")
            self.on_enter()
        except Exception as e:
            print(f"Clear log error: {e}")


# ─────────────────────────────────────────────────────────────
#  APP ENTRY
# ─────────────────────────────────────────────────────────────
class TitanApp(App):
    title = "Titan AI Studio Pro"

    def build(self):
        # FIX #7: Window background set karo crash se bachne ke liye
        from kivy.core.window import Window
        Window.clearcolor = C_BG

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
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
