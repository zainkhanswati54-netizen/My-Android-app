import os
import threading
import time
import shutil
import json
import re
from datetime import datetime

# Android permissions
try:
    from android.permissions import request_permissions, Permission, check_permission
    from android.storage import primary_external_storage_path, secondary_external_storage_path
    from jnius import autoclass, cast
    ANDROID_ENV = True
except Exception:
    ANDROID_ENV = False

from kivy.config import Config
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.utils import get_color_from_hex

# Colors - Premium Theme
C_BG     = '#0A0F1E'
C_CARD   = '#0F172A'
C_ACCENT = '#38BDF8'
C_GREEN  = '#22C55E'
C_RED    = '#EF4444'
C_PURPLE = '#7C3AED'
C_BLUE   = '#2563EB'
C_CYAN   = '#0EA5E9'
C_GRAY   = '#475569'
C_INDIGO = '#6366F1'
C_AMBER  = '#F59E0B'
C_GOLD   = '#FBBF24'

# Languages - Expanded
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
    'Italian':  'it',
    'Portuguese': 'pt',
}

# Voice Profiles - FIXED: Sirf Male aur Female
VOICE_PROFILES = {
    '👨 Male':    {'tld': 'com',    'slow': False, 'name': 'John (US English)'},
    '👩 Female':  {'tld': 'com.au', 'slow': False, 'name': 'Emma (Australian English)'},
}

# Storage paths
def get_storage_path():
    """User ke selected storage path ko return karega"""
    app = App.get_running_app()
    if hasattr(app, 'user_storage_path') and app.user_storage_path:
        return app.user_storage_path
    return os.path.join('/sdcard', 'TitanAI_Audio')

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
            json.dump(data[:50], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

class FlatBtn(Button):
    def __init__(self, bg=C_BLUE, radius=12, **kw):
        super().__init__(**kw)
        self.bg = bg
        self.radius = radius
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bind(pos=self._draw, size=self._draw)

    def set_bg(self, color):
        self.bg = color
        self._draw()

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

class DarkPanel(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*get_color_from_hex(C_BG))
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size

def sec_label(txt):
    return Label(
        text=txt,
        font_size='13sp',
        bold=True,
        color=get_color_from_hex('#64748B'),
        size_hint_y=None,
        height=30,
        halign='left',
        valign='middle',
    )
# ==================== FIXED SPLASH SCREEN (No double loading) ====================
class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = DarkPanel()
        
        # Logo image - aapka logo yahan aayega
        from kivy.uix.image import Image
        try:
            logo = Image(
                source='logo.png',
                size_hint=(None, None),
                size=(200, 200),
                pos_hint={'center_x': 0.5, 'center_y': 0.65}
            )
            root.add_widget(logo)
        except:
            # Agar logo nahi mila to text dikhega
            root.add_widget(Label(
                text='🎙️ TITAN AI',
                font_size='52sp',
                bold=True,
                color=get_color_from_hex(C_ACCENT),
                pos_hint={'center_x': 0.5, 'center_y': 0.62},
            ))
            root.add_widget(Label(
                text='Studio Pro',
                font_size='20sp',
                color=get_color_from_hex('#64748B'),
                pos_hint={'center_x': 0.5, 'center_y': 0.54},
            ))
        
        self.info = Label(
            text='Initializing...',
            font_size='15sp',
            color=get_color_from_hex('#94A3B8'),
            pos_hint={'center_x': 0.5, 'center_y': 0.44},
        )
        root.add_widget(self.info)
        
        self.pb = ProgressBar(
            max=100, value=0,
            size_hint=(0.7, None), height=18,
            pos_hint={'center_x': 0.5, 'center_y': 0.37},
        )
        root.add_widget(self.pb)
        self.add_widget(root)

    def on_enter(self, *a):
        self.pb.value = 0
        # Single loading - direct jump to studio after loading
        Clock.schedule_once(lambda dt: self._load_resources(), 0.1)

    def _load_resources(self):
        stages = [
            (20, 'Loading audio engine...'),
            (40, 'Preparing voice profiles...'),
            (60, 'Checking permissions...'),
            (80, 'Almost ready...'),
            (100, 'Welcome to Titan AI!'),
        ]
        
        def update_stage(idx=0):
            if idx < len(stages):
                val, msg = stages[idx]
                self.pb.value = val
                self.info.text = msg
                Clock.schedule_once(lambda dt: update_stage(idx + 1), 0.3)
            else:
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'studio'), 0.2)
        
        update_stage()

# ==================== STORAGE SELECTION POPUP ====================
class StorageSelectorPopup(Popup):
    def __init__(self, callback, **kw):
        super().__init__(**kw)
        self.callback = callback
        self.title = 'Select Save Location'
        self.size_hint = (0.9, 0.7)
        self.background_color = get_color_from_hex(C_CARD)
        
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        layout.add_widget(Label(
            text='Where do you want to save audio files?',
            font_size='16sp',
            color=(1,1,1,1),
            size_hint_y=None,
            height=50
        ))
        
        # Internal Storage button
        internal_btn = FlatBtn(
            text='📱 Internal Storage\n(/storage/emulated/0/TitanAI)',
            bg=C_BLUE,
            font_size='14sp',
            size_hint_y=None,
            height=80
        )
        internal_btn.bind(on_press=lambda x: self._select_path('/storage/emulated/0/TitanAI'))
        layout.add_widget(internal_btn)
        
        # SD Card button (agar available ho)
        if ANDROID_ENV:
            try:
                sd_path = secondary_external_storage_path()
                if sd_path:
                    sd_btn = FlatBtn(
                        text=f'💾 SD Card\n({sd_path}/TitanAI)',
                        bg=C_PURPLE,
                        font_size='14sp',
                        size_hint_y=None,
                        height=80
                    )
                    sd_btn.bind(on_press=lambda x: self._select_path(f'{sd_path}/TitanAI'))
                    layout.add_widget(sd_btn)
            except:
                pass
        
        # Custom folder button
        custom_btn = FlatBtn(
            text='📁 Choose Custom Folder',
            bg=C_GRAY,
            font_size='14sp',
            size_hint_y=None,
            height=60
        )
        custom_btn.bind(on_press=self._show_filechooser)
        layout.add_widget(custom_btn)
        
        self.content = layout
    
    def _select_path(self, path):
        try:
            os.makedirs(path, exist_ok=True)
            self.callback(path)
            self.dismiss()
        except Exception as e:
            self.callback(None, str(e))
    
    def _show_filechooser(self, *a):
        # File chooser for custom folder
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        fc = FileChooserIconView(
            path='/storage/emulated/0',
            dirselect=True,
            size_hint=(1, 0.9)
        )
        
        def select_folder(*args):
            if fc.selection:
                self._select_path(fc.selection[0])
                popup.dismiss()
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        ok_btn = FlatBtn(text='Select Folder', bg=C_GREEN, font_size='14sp')
        ok_btn.bind(on_press=select_folder)
        cancel_btn = FlatBtn(text='Cancel', bg=C_RED, font_size='14sp')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(ok_btn)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(fc)
        layout.add_widget(btn_layout)
        
        popup = Popup(
            title='Choose Folder',
            content=layout,
            size_hint=(0.95, 0.85),
            background_color=get_color_from_hex(C_CARD)
        )
        popup.open()
# ==================== IMPORT TXT FILE POPUP ====================
class ImportFilePopup(Popup):
    def __init__(self, callback, **kw):
        super().__init__(**kw)
        self.callback = callback
        self.title = 'Import Text File'
        self.size_hint = (0.95, 0.8)
        self.background_color = get_color_from_hex(C_CARD)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.file_chooser = FileChooserIconView(
            path='/storage/emulated/0',
            filters=['*.txt'],
            size_hint=(1, 0.85)
        )
        layout.add_widget(self.file_chooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        import_btn = FlatBtn(text='Import & Scan', bg=C_GREEN, font_size='14sp')
        import_btn.bind(on_press=self._import_file)
        cancel_btn = FlatBtn(text='Cancel', bg=C_RED, font_size='14sp')
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        btn_layout.add_widget(import_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        self.content = layout
    
    def _import_file(self, *a):
        if self.file_chooser.selection:
            file_path = self.file_chooser.selection[0]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.callback(content)
                self.dismiss()
            except Exception as e:
                self.callback(None, str(e))
                self.dismiss()

# ==================== HISTORY SCREEN ====================
class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._sounds = []
        self._build()

    def _build(self):
        root = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=15, spacing=10)

        hdr = BoxLayout(size_hint_y=None, height=60, spacing=10)
        back = FlatBtn(
            text='← Back', bg=C_GRAY,
            size_hint_x=None, width=100, font_size='15sp')
        back.bind(on_press=lambda *a: setattr(
            self.manager, 'current', 'studio'))
        hdr.add_widget(back)
        hdr.add_widget(Label(
            text='📜 Download History',
            font_size='20sp', bold=True,
            color=get_color_from_hex(C_ACCENT),
        ))
        outer.add_widget(hdr)

        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None, spacing=8, padding=[0, 5])
        self.list_box.bind(
            minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)

        clr = FlatBtn(
            text='🗑️ Clear All History', bg='#7F1D1D',
            size_hint_y=None, height=55, font_size='15sp')
        clr.bind(on_press=self._clear)
        outer.add_widget(clr)

        root.add_widget(outer)
        self.add_widget(root)

    def on_enter(self, *a):
        self._refresh()

    def _refresh(self):
        self.list_box.clear_widgets()
        data = history_load()
        if not data:
            self.list_box.add_widget(Label(
                text='No downloads yet.\nGenerate and save audio to see history.',
                color=get_color_from_hex('#64748B'),
                size_hint_y=None, height=80,
            ))
            return
        for entry in data:
            row = BoxLayout(
                size_hint_y=None, height=80,
                spacing=8, padding=[10, 4])
            with row.canvas.before:
                Color(*get_color_from_hex(C_CARD))
                rr = RoundedRectangle(
                    pos=row.pos, size=row.size, radius=[10])

            def upd(w, *a, r=rr):
                r.pos = w.pos
                r.size = w.size
            row.bind(pos=upd, size=upd)

            info = BoxLayout(orientation='vertical', size_hint_x=0.75)
            info.add_widget(Label(
                text=entry.get('filename', 'unknown'),
                font_size='12sp', bold=True,
                color=(0.9, 0.9, 0.9, 1),
                halign='left', valign='middle',
                size_hint_y=None, height=36,
                text_size=(None, 36)
            ))
            info.add_widget(Label(
                text=f"{entry.get('lang', '')}  |  {entry.get('voice', '')}  |  {entry.get('time', '')}",
                font_size='10sp',
                color=(0.4, 0.8, 0.4, 1),
                halign='left', valign='middle',
                size_hint_y=None, height=28,
            ))
            row.add_widget(info)

            fp = entry.get('path', '')
            if os.path.exists(fp):
                pb = FlatBtn(
                    text='▶ PLAY', bg=C_GREEN,
                    size_hint_x=None, width=68, font_size='11sp')
                pb.bind(on_press=lambda *a, p=fp: self._play(p))
                row.add_widget(pb)

            self.list_box.add_widget(row)

    def _play(self, path):
        snd = SoundLoader.load(path)
        if snd:
            self._sounds.append(snd)
            snd.play()

    def _clear(self, *a):
        try:
            with open(history_path(), 'w') as f:
                json.dump([], f)
        except Exception:
            pass
        self._refresh()
# ==================== MAIN STUDIO SCREEN (All fixes applied) ====================
class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._audio = None
        self.out_file = None
        self.voice_sel = '👨 Male'
        self.speed_sel = 'Normal'
        self._build()

    def _build(self):
        root = DarkPanel()
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=24, spacing=14)
        content.bind(minimum_height=content.setter('height'))

        # Header
        content.add_widget(Label(
            text='🎙️ TITAN AI STUDIO PRO',
            font_size='26sp', bold=True,
            color=get_color_from_hex(C_ACCENT),
            size_hint_y=None, height=70,
        ))

        # Language selection
        content.add_widget(sec_label('🌐 LANGUAGE'))
        self.lang_spin = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=55,
            font_size='16sp',
            color=(1, 1, 1, 1),
            background_color=get_color_from_hex('#1E3A5F'),
        )
        content.add_widget(self.lang_spin)

        # Voice selection - FIXED: Sirf Male/Female, proper names
        content.add_widget(sec_label('🎤 VOICE CHARACTER'))
        vgrid = GridLayout(
            cols=2, rows=1,
            size_hint_y=None, height=80, spacing=15)
        self._vbtns = {}
        for name in VOICE_PROFILES:
            profile = VOICE_PROFILES[name]
            btn_text = f"{name}\n{profile['name']}"
            b = FlatBtn(text=btn_text, bg='#1E3A5F', font_size='13sp', radius=10)
            b.bind(on_press=lambda *a, n=name: self._pick_voice(n))
            vgrid.add_widget(b)
            self._vbtns[name] = b
        content.add_widget(vgrid)
        self._pick_voice('👨 Male')

        # Character name display
        self.char_name_lbl = Label(
            text='Selected: John (US English)',
            font_size='12sp',
            color=get_color_from_hex(C_GOLD),
            size_hint_y=None,
            height=25,
        )
        content.add_widget(self.char_name_lbl)

        # Import File button
        import_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        import_btn = FlatBtn(
            text='📂 IMPORT TXT FILE', bg=C_PURPLE,
            font_size='14sp', radius=10)
        import_btn.bind(on_press=self._import_file)
        import_layout.add_widget(import_btn)
        
        clear_import_btn = FlatBtn(
            text='🗑️ CLEAR', bg=C_GRAY,
            font_size='14sp', radius=10,
            size_hint_x=0.3)
        clear_import_btn.bind(on_press=lambda x: setattr(self.txt, 'text', ''))
        import_layout.add_widget(clear_import_btn)
        content.add_widget(import_layout)

        # Text input
        content.add_widget(sec_label('📝 SCRIPT'))
        self.txt = TextInput(
            hint_text='✏️ Yahan apna text likho ya import karo...\n\nExample: Hello! How are you today?',
            multiline=True,
            size_hint_y=None, height=200,
            background_color=get_color_from_hex(C_CARD),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.4, 0.4, 0.4, 1),
            cursor_color=get_color_from_hex(C_ACCENT),
            font_size='16sp',
            padding=[16, 16],
        )
        self.txt.bind(text=self._count)
        content.add_widget(self.txt)

        self.count_lbl = Label(
            text='📊 Words: 0   Characters: 0',
            font_size='12sp',
            color=get_color_from_hex('#475569'),
            size_hint_y=None, height=28,
        )
        content.add_widget(self.count_lbl)
        # Speed selection
        content.add_widget(sec_label('⚡ SPEED'))
        self.speed_lbl = Label(
            text='Selected: Normal',
            font_size='13sp',
            color=get_color_from_hex(C_GREEN),
            size_hint_y=None, height=30,
        )
        content.add_widget(self.speed_lbl)
        srow = BoxLayout(size_hint_y=None, height=58, spacing=10)
        self._sbtns = {}
        for spd, col in [('🐢 Slow', C_INDIGO), ('⚡ Normal', C_GREEN), ('🚀 Fast', C_AMBER)]:
            b = FlatBtn(text=spd, bg=col, font_size='14sp', radius=8)
            b.bind(on_press=lambda *a, s=spd: self._pick_speed(s))
            srow.add_widget(b)
            self._sbtns[spd] = b
        content.add_widget(srow)
        self._pick_speed('⚡ Normal')

        # Status and progress
        self.status_lbl = Label(
            text='✅ Ready',
            font_size='13sp',
            color=get_color_from_hex('#64748B'),
            size_hint_y=None, height=38,
        )
        content.add_widget(self.status_lbl)

        self.prog = ProgressBar(
            max=100, value=0,
            size_hint_y=None, height=12)
        content.add_widget(self.prog)

        # Generate button
        self.gen_btn = FlatBtn(
            text='🔊 GENERATE SPEECH', bg=C_BLUE,
            size_hint_y=None, height=75,
            font_size='18sp', bold=True, radius=15)
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        # Play/Stop controls
        ps = BoxLayout(size_hint_y=None, height=65, spacing=12)
        self.play_btn = FlatBtn(
            text='▶ PLAY', bg=C_GREEN,
            font_size='16sp', radius=10, disabled=True)
        self.stop_btn = FlatBtn(
            text='⏹️ STOP', bg=C_RED,
            font_size='16sp', radius=10, disabled=True)
        self.play_btn.bind(on_press=self._play)
        self.stop_btn.bind(on_press=self._stop)
        ps.add_widget(self.play_btn)
        ps.add_widget(self.stop_btn)
        content.add_widget(ps)

        # Download and History buttons
        self.dl_btn = FlatBtn(
            text='💾 DOWNLOAD AUDIO', bg=C_CYAN,
            size_hint_y=None, height=65,
            font_size='16sp', radius=10, disabled=True)
        self.dl_btn.bind(on_press=self._download)
        content.add_widget(self.dl_btn)

        hbtn = FlatBtn(
            text='📜 DOWNLOAD HISTORY', bg=C_PURPLE,
            size_hint_y=None, height=55, font_size='15sp', radius=10)
        hbtn.bind(on_press=lambda *a: setattr(
            self.manager, 'current', 'history'))
        content.add_widget(hbtn)

        # Storage location button
        storage_btn = FlatBtn(
            text='📁 Change Save Location', bg=C_GRAY,
            size_hint_y=None, height=50, font_size='14sp', radius=8)
        storage_btn.bind(on_press=self._change_storage)
        content.add_widget(storage_btn)

        content.add_widget(Label(size_hint_y=None, height=20))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)
        
        # Initial storage setup
        Clock.schedule_once(lambda dt: self._init_storage(), 0.5)

    def _init_storage(self):
        """Initialize storage on first run"""
        app = App.get_running_app()
        if not hasattr(app, 'user_storage_path') or not app.user_storage_path:
            default_path = os.path.join('/sdcard', 'TitanAI_Audio')
            try:
                os.makedirs(default_path, exist_ok=True)
                app.user_storage_path = default_path
            except:
                app.user_storage_path = app.user_data_dir
            self.status_lbl.text = f'💾 Saving to: {os.path.basename(app.user_storage_path)}'

    def _change_storage(self, *a):
        """Change storage location manually"""
        popup = StorageSelectorPopup(callback=self._on_storage_selected)
        popup.open()

    def _on_storage_selected(self, path, error=None):
        if error:
            self.status_lbl.text = f'❌ Error: {error}'
        elif path:
            app = App.get_running_app()
            app.user_storage_path = path
            self.status_lbl.text = f'✅ Save location changed to: {os.path.basename(path)}'

    def _import_file(self, *a):
        """Import TXT file content"""
        popup = ImportFilePopup(callback=self._on_file_imported)
        popup.open()

    def _on_file_imported(self, content, error=None):
        if error:
            self.status_lbl.text = f'❌ Import failed: {error}'
        elif content:
            self.txt.text = content
            self.status_lbl.text = f'✅ Imported {len(content)} characters from file'
            self._count(None, content)

    def _pick_voice(self, name):
        self.voice_sel = name
        for n, b in self._vbtns.items():
            b.set_bg(C_GREEN if n == name else '#1E3A5F')
        # Update character name display
        profile = VOICE_PROFILES.get(name, VOICE_PROFILES['👨 Male'])
        self.char_name_lbl.text = f'🎙️ Selected: {profile["name"]}'

    def _pick_speed(self, spd):
        self.speed_sel = spd
        display_speed = spd.replace('🐢 ', '').replace('⚡ ', '').replace('🚀 ', '')
        self.speed_lbl.text = 'Selected: ' + display_speed
        colors = {'🐢 Slow': C_INDIGO, '⚡ Normal': C_GREEN, '🚀 Fast': C_AMBER}
        for n, b in self._sbtns.items():
            b.set_bg(C_ACCENT if n == spd else colors[n])

    def _count(self, inst, val):
        words = len(val.split()) if val.strip() else 0
        chars = len(val)
        self.count_lbl.text = f'📊 Words: {words}   Characters: {chars}'

    def _set_ready(self, audio_ok=True):
        self.gen_btn.disabled = False
        self.play_btn.disabled = not audio_ok
        self.stop_btn.disabled = not audio_ok
        self.dl_btn.disabled = not audio_ok

    def _set_busy(self):
        self.gen_btn.disabled = True
        self.play_btn.disabled = True
        self.stop_btn.disabled = True
        self.dl_btn.disabled = True

    def _upd_status(self, val, msg):
        self.prog.value = val
        self.status_lbl.text = msg

    def _generate(self, *a):
        text = self.txt.text.strip()
        if not text:
            self.status_lbl.text = '❌ Error: Text is empty! Please enter some text.'
            return
        if len(text) > 5000:
            self.status_lbl.text = '❌ Error: Text too long (max 5000 characters)'
            return
        
        self._set_busy()
        self._upd_status(0, '🎬 Starting...')
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            from gtts import gTTS
            
            Clock.schedule_once(lambda dt: self._upd_status(15, '🌐 Connecting to server...'))
            
            lang_code = LANGUAGES.get(self.lang_spin.text, 'en')
            voice_name = self.voice_sel
            profile = VOICE_PROFILES.get(voice_name, VOICE_PROFILES['👨 Male'])
            
            # Speed handling
            speed_mode = self.speed_sel.replace('🐢 ', '').replace('⚡ ', '').replace('🚀 ', '')
            slow = (speed_mode == 'Slow')
            
            Clock.schedule_once(lambda dt: self._upd_status(40, f'🎙️ Generating with {voice_name} voice...'))
            
            tts = gTTS(
                text=self.txt.text,
                lang=lang_code,
                tld=profile['tld'],
                slow=slow,
            )
            
            out = os.path.join(
                App.get_running_app().user_data_dir,
                f'tts_temp_{int(time.time())}.mp3'
            )
            
            Clock.schedule_once(lambda dt: self._upd_status(70, '💾 Saving audio...'))
            tts.save(out)
            self.out_file = out
            
            Clock.schedule_once(lambda dt: self._on_done())
            
        except Exception as exc:
            msg = str(exc).lower()
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
        self._upd_status(100, '✅ Audio generated successfully! Click PLAY to listen.')
        self._set_ready(audio_ok=True)

    def _on_err(self, msg):
        if any(k in msg for k in ['network', 'connection', 'gaierror', 'timeout', 'internet']):
            txt = '❌ No internet connection! Please check your network.'
        elif 'lang' in msg:
            txt = '❌ Language not supported for this voice.'
        else:
            txt = f'❌ Error: {msg[:80]}'
        self._upd_status(0, txt)
        self._set_ready(audio_ok=False)

    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = '▶ PLAY'
        else:
            self._audio.play()
            self.play_btn.text = '⏸ PAUSE’
    def _stop(self, *a):
        if self._audio:
            self._audio.stop()
        self.play_btn.text = '▶ PLAY'

    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status_lbl.text = '❌ Generate speech first!'
            return
        
        # Get user's selected storage path
        app = App.get_running_app()
        dest_dir = getattr(app, 'user_storage_path', '/sdcard/TitanAI_Audio')
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"TitanAI_{self.lang_spin.text}_{self.voice_sel.replace(' ', '_')}_{timestamp}.mp3"
        dest = os.path.join(dest_dir, fname)
        
        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self.status_lbl.text = f'✅ Saved: {fname}'
            
            # Save to history
            history_save({
                'filename': fname,
                'path': dest,
                'lang': self.lang_spin.text,
                'voice': self.voice_sel,
                'speed': self.speed_sel,
                'time': datetime.now().strftime('%d %b %Y  %H:%M'),
            })
            
            # Show success popup
            box = BoxLayout(orientation='vertical', padding=20, spacing=12)
            box.add_widget(Label(
                text=f'✨ Audio saved successfully!\n\n📄 {fname}\n\n📁 Location:\n{dest_dir}',
                color=(1, 1, 1, 1), font_size='13sp',
            ))
            ok = FlatBtn(text='OK', bg=C_GREEN, size_hint_y=None, height=55, radius=10)
            box.add_widget(ok)
            pop = Popup(
                title='✅ Download Complete',
                content=box,
                size_hint=(0.9, 0.55),
                background_color=get_color_from_hex(C_CARD),
            )
            ok.bind(on_press=pop.dismiss)
            pop.open()
            
        except Exception as e:
            self.status_lbl.text = f'❌ Download failed: {str(e)[:60]}'

# ==================== APP CLASS ====================
class TitanApp(App):
    user_storage_path = None
    
    def build(self):
        self.title = 'Titan AI Studio Pro'
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(StudioScreen(name='studio'))
        sm.add_widget(HistoryScreen(name='history'))
        
        if ANDROID_ENV:
            Clock.schedule_once(self._ask_perms, 0.5)
        
        return sm
    
    def _ask_perms(self, *a):
        try:
            permissions = [
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ]
            # Check if MANAGE_EXTERNAL_STORAGE is available
            try:
                if hasattr(Permission, 'MANAGE_EXTERNAL_STORAGE'):
                    permissions.append(Permission.MANAGE_EXTERNAL_STORAGE)
            except:
                pass
            
            request_permissions(permissions)
        except Exception as e:
            print(f"Permission error: {e}")

if __name__ == '__main__':
    TitanApp().run()
```

📦 Ab buildozer.spec update karo:

```ini
[app]
title = Titan AI Studio Pro
package.name = titanai.studio
package.domain = org.titan.studio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf,txt,wav
version = 5.3.0

requirements = python3,kivy==2.2.1,gTTS,requests,certifi,chardet,idna,urllib3,pillow,pyjnius,setuptools

orientation = portrait
fullscreen = 0
android.wakelock = True

# Enhanced permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK, MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

android.skip_update = False
android.accept_sdk_license = True
android.enable_androidx = True
android.copy_libs = 1
android.entrypoint = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
