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
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

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
}

VOICE_PROFILES = {
    'Male':   {'tld': 'com',    'slow': False},
    'Female': {'tld': 'com.au', 'slow': False},
}

SPEED_MAP = {
    10:  True,
    20:  True,
    30:  True,
    40:  True,
    50:  False,
    60:  False,
    70:  False,
    80:  False,
    90:  False,
    100: False,
}


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


def read_txt(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return ''


def read_pdf(path):
    try:
        import zipfile
        if zipfile.is_zipfile(path):
            return ''
    except Exception:
        pass
    try:
        text = []
        with open(path, 'rb') as f:
            content = f.read().decode('latin-1', errors='ignore')
        import re
        parts = re.findall(r'BT(.*?)ET', content, re.DOTALL)
        for part in parts:
            matches = re.findall(r'\((.*?)\)', part)
            for m in matches:
                text.append(m)
        result = ' '.join(text)
        result = result.replace('\\n', '\n').replace('\\r', '')
        if len(result.strip()) > 10:
            return result.strip()
        return ''
    except Exception:
        return ''


def read_docx(path):
    try:
        import zipfile
        import re
        with zipfile.ZipFile(path, 'r') as z:
            if 'word/document.xml' in z.namelist():
                xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
                text = re.sub(r'<[^>]+>', ' ', xml)
                text = ' '.join(text.split())
                return text
        return ''
    except Exception:
        return ''


class FlatBtn(Button):
    def __init__(self, bg=C_BLUE, **kw):
        super().__init__(**kw)
        self.bg = bg
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
            RoundedRectangle(pos=self.pos, size=self.size, radius=[14])


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


def card_bg(widget, color=C_CARD, radius=12):
    with widget.canvas.before:
        Color(*get_color_from_hex(color))
        rr = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])

    def upd(w, *a, r=rr):
        r.pos = w.pos
        r.size = w.size

    widget.bind(pos=upd, size=upd)


def lbl(txt, size=13, color=C_MUTED, bold=False, h=32):
    return Label(
        text=txt,
        font_size=str(size) + 'sp',
        bold=bold,
        color=get_color_from_hex(color),
        size_hint_y=None,
        height=h,
        halign='left',
        valign='middle',
    )


class LoadingScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = DarkPanel()

        logo_box = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(200, 200),
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
        )

        logo_lbl = Label(
            text='SS',
            font_size='72sp',
            bold=True,
            color=get_color_from_hex(C_BLUE2),
        )
        logo_box.add_widget(logo_lbl)
        root.add_widget(logo_box)

        root.add_widget(Label(
            text='Titan AI Studio Pro',
            font_size='22sp',
            bold=True,
            color=get_color_from_hex(C_WHITE),
            pos_hint={'center_x': 0.5, 'center_y': 0.32},
        ))

        root.add_widget(Label(
            text='Your Personal Narrator, Always Free.',
            font_size='14sp',
            color=get_color_from_hex(C_MUTED),
            pos_hint={'center_x': 0.5, 'center_y': 0.26},
        ))

        self.dot_lbl = Label(
            text='Loading...',
            font_size='13sp',
            color=get_color_from_hex(C_BLUE2),
            pos_hint={'center_x': 0.5, 'center_y': 0.18},
        )
        root.add_widget(self.dot_lbl)

        self.add_widget(root)
        self._dots = 0

    def on_enter(self, *a):
        self._ev = Clock.schedule_interval(self._tick, 0.5)
        Clock.schedule_once(lambda dt: setattr(
            self.manager, 'current', 'studio'), 3.0)

    def on_leave(self, *a):
        if hasattr(self, '_ev'):
            self._ev.cancel()

    def _tick(self, dt):
        self._dots = (self._dots + 1) % 4
        self.dot_lbl.text = 'Loading' + '.' * (self._dots + 1)


class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._sounds = []
        self._build()

    def _build(self):
        root = DarkPanel()
        outer = BoxLayout(orientation='vertical', padding=16, spacing=12)

        hdr = BoxLayout(size_hint_y=None, height=58, spacing=10)
        back = FlatBtn(text='Back', bg=C_GRAY,
                       size_hint_x=None, width=90, font_size='14sp')
        back.bind(on_press=lambda *a: setattr(
            self.manager, 'current', 'studio'))
        hdr.add_widget(back)
        hdr.add_widget(Label(
            text='Download History',
            font_size='20sp', bold=True,
            color=get_color_from_hex(C_ACCENT),
        ))
        outer.add_widget(hdr)

        sv = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None, spacing=8, padding=[0, 4])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)

        clr = FlatBtn(text='Clear All History', bg='#7F1D1D',
                      size_hint_y=None, height=52, font_size='14sp')
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
                text='No downloads yet.',
                color=get_color_from_hex(C_MUTED),
                size_hint_y=None, height=60,
            ))
            return
        for entry in data:
            row = BoxLayout(size_hint_y=None, height=78,
                            spacing=8, padding=[12, 4])
            card_bg(row, C_CARD2, 10)

            info = BoxLayout(orientation='vertical', size_hint_x=0.78)
            info.add_widget(Label(
                text=entry.get('filename', 'unknown'),
                font_size='13sp', bold=True,
                color=get_color_from_hex(C_WHITE),
                halign='left', valign='middle',
                size_hint_y=None, height=34,
            ))
            info.add_widget(Label(
                text=entry.get('lang', '') + '   ' +
                     entry.get('voice', '') + '   ' +
                     entry.get('time', ''),
                font_size='11sp',
                color=get_color_from_hex(C_GREEN),
                halign='left', valign='middle',
                size_hint_y=None, height=26,
            ))
            row.add_widget(info)

            fp = entry.get('path', '')
            if os.path.exists(fp):
                pb = FlatBtn(text='PLAY', bg=C_GREEN,
                             size_hint_x=None, width=65, font_size='12sp')
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


class StudioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._audio = None
        self.out_file = None
        self.voice_sel = 'Male'
        self.save_dir = ''
        self._build()

    def _build(self):
        root = DarkPanel()

        outer = BoxLayout(orientation='vertical')

        header = BoxLayout(
            size_hint_y=None, height=70,
            padding=[16, 8], spacing=12)
        card_bg(header, C_CARD, 0)

        logo_lbl = Label(
            text='SS',
            font_size='28sp', bold=True,
            color=get_color_from_hex(C_BLUE2),
            size_hint_x=None, width=50,
        )
        header.add_widget(logo_lbl)

        title_box = BoxLayout(orientation='vertical')
        title_box.add_widget(Label(
            text='Titan AI Studio Pro',
            font_size='18sp', bold=True,
            color=get_color_from_hex(C_WHITE),
            halign='left', valign='middle',
        ))
        title_box.add_widget(Label(
            text='Your Personal Narrator, Always Free.',
            font_size='11sp',
            color=get_color_from_hex(C_MUTED),
            halign='left', valign='middle',
        ))
        header.add_widget(title_box)
        outer.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[16, 12], spacing=14)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(lbl('Voice Language', 13, C_WHITE, True, 30))
        self.lang_spin = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=52,
            font_size='15sp',
            color=(1, 1, 1, 1),
            background_color=get_color_from_hex(C_BLUE),
        )
        content.add_widget(self.lang_spin)

        content.add_widget(lbl('Gender', 13, C_WHITE, True, 30))
        gender_row = BoxLayout(size_hint_y=None, height=52, spacing=12)
        self._vbtns = {}
        for name in VOICE_PROFILES:
            b = FlatBtn(text=name, bg=C_BLUE, font_size='15sp', bold=True)
            b.bind(on_press=lambda *a, n=name: self._pick_voice(n))
            gender_row.add_widget(b)
            self._vbtns[name] = b
        content.add_widget(gender_row)
        self._pick_voice('Male')

        content.add_widget(lbl('Speed', 13, C_WHITE, True, 30))
        speed_row = BoxLayout(size_hint_y=None, height=40, spacing=8)
        speed_row.add_widget(lbl('Slow', 12, C_MUTED, False, 40))
        self.speed_slider = Slider(
            min=10, max=100, value=50, step=10,
            size_hint_x=1,
        )
        self.speed_val_lbl = lbl('50%', 12, C_ACCENT, False, 40)
        self.speed_slider.bind(value=self._on_speed)
        speed_row.add_widget(self.speed_slider)
        speed_row.add_widget(lbl('Fast', 12, C_MUTED, False, 40))
        content.add_widget(speed_row)
        content.add_widget(self.speed_val_lbl)

        char_row = BoxLayout(size_hint_y=None, height=36, spacing=10)
        self.char_lbl = lbl('Input Text: 0 characters (0 lines)', 12, C_MUTED, False, 36)
        char_row.add_widget(self.char_lbl)
        imp_btn = FlatBtn(text='Import File', bg=C_BLUE2,
                          size_hint_x=None, width=110, font_size='13sp')
        imp_btn.bind(on_press=self._import_file)
        char_row.add_widget(imp_btn)
        content.add_widget(char_row)

        self.txt = TextInput(
            hint_text='Enter text to synthesize........',
            multiline=True,
            size_hint_y=None, height=220,
            background_color=get_color_from_hex(C_CARD2),
            foreground_color=get_color_from_hex(C_WHITE),
            hint_text_color=get_color_from_hex(C_MUTED),
            cursor_color=get_color_from_hex(C_ACCENT),
            font_size='16sp',
            padding=[14, 14],
        )
        self.txt.bind(text=self._count)
        content.add_widget(self.txt)

        self.status_lbl = lbl('Ready', 13, C_MUTED, False, 34)
        content.add_widget(self.status_lbl)

        self.prog = ProgressBar(max=100, value=0, size_hint_y=None, height=12)
        content.add_widget(self.prog)

        preview_dl_row = BoxLayout(size_hint_y=None, height=62, spacing=12)
        self.play_btn = FlatBtn(
            text='Preview Audio', bg=C_RED,
            font_size='14sp', disabled=True)
        self.play_btn.bind(on_press=self._play)
        self.dl_btn = FlatBtn(
            text='Download Voice', bg=C_GREEN,
            font_size='14sp', disabled=True)
        self.dl_btn.bind(on_press=self._download)
        preview_dl_row.add_widget(self.play_btn)
        preview_dl_row.add_widget(self.dl_btn)
        content.add_widget(preview_dl_row)

        self.gen_btn = FlatBtn(
            text='Generate Audio',
            bg=C_CARD2,
            size_hint_y=None, height=62,
            font_size='16sp', bold=True)
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        hist_btn = FlatBtn(
            text='Download History', bg=C_PURPLE,
            size_hint_y=None, height=54, font_size='14sp')
        hist_btn.bind(on_press=lambda *a: setattr(
            self.manager, 'current', 'history'))
        content.add_widget(hist_btn)

        usage_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=200,
            padding=[12, 10])
        card_bg(usage_box, C_CARD2, 12)
        usage_box.add_widget(lbl('Usage steps:', 13, C_WHITE, True, 28))
        steps = [
            '1. Select Voice Language from dropdown',
            '2. Choose Gender: Male or Female',
            '3. Adjust Speed using the slider',
            '4. Type or Import your text file',
            '5. Tap Generate Audio button',
            '6. Preview then Download your voice',
        ]
        for s in steps:
            usage_box.add_widget(lbl(s, 12, C_MUTED, False, 24))
        content.add_widget(usage_box)

        content.add_widget(Label(size_hint_y=None, height=20))

        scroll.add_widget(content)
        outer.add_widget(scroll)
        root.add_widget(outer)
        self.add_widget(root)

    def _pick_voice(self, name):
        self.voice_sel = name
        for n, b in self._vbtns.items():
            b.set_bg(C_BLUE if n == name else C_CARD2)

    def _on_speed(self, inst, val):
        self.speed_val_lbl.text = 'Speed: ' + str(int(val)) + '%'

    def _count(self, inst, val):
        lines = len(val.splitlines()) if val.strip() else 0
        chars = len(val)
        self.char_lbl.text = 'Input Text: ' + str(chars) + ' characters (' + str(lines) + ' lines)'

    def _import_file(self, *a):
        box = BoxLayout(orientation='vertical', padding=10, spacing=8)
        box.add_widget(lbl('Select file type to import:', 14, C_WHITE, True, 34))

        btn_row = BoxLayout(size_hint_y=None, height=52, spacing=10)
        pop = [None]

        for ftype in ['TXT', 'PDF', 'DOCX']:
            b = FlatBtn(text=ftype, bg=C_BLUE, font_size='14sp')
            b.bind(on_press=lambda x, t=ftype, p=pop: self._open_chooser(t, p[0]))
            btn_row.add_widget(b)

        box.add_widget(btn_row)
        cancel = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None, height=46)
        box.add_widget(cancel)

        p = Popup(
            title='Import File',
            content=box,
            size_hint=(0.9, 0.35),
            background_color=get_color_from_hex(C_CARD),
        )
        pop[0] = p
        cancel.bind(on_press=p.dismiss)
        p.open()

    def _open_chooser(self, ftype, prev_popup):
        if prev_popup:
            prev_popup.dismiss()

        filters_map = {
            'TXT':  ['*.txt'],
            'PDF':  ['*.pdf'],
            'DOCX': ['*.docx'],
        }

        start_path = '/'
        if ANDROID_ENV:
            try:
                start_path = primary_external_storage_path()
            except Exception:
                start_path = '/sdcard'

        fc = FileChooserListView(
            path=start_path,
            filters=filters_map.get(ftype, ['*.*']),
            size_hint=(1, 1),
        )

        box = BoxLayout(orientation='vertical', padding=8, spacing=8)
        box.add_widget(fc)

        btn_row = BoxLayout(size_hint_y=None, height=52, spacing=10)
        sel_btn = FlatBtn(text='Select', bg=C_GREEN, font_size='14sp')
        can_btn = FlatBtn(text='Cancel', bg=C_GRAY, font_size='14sp')
        btn_row.add_widget(sel_btn)
        btn_row.add_widget(can_btn)
        box.add_widget(btn_row)

        p = Popup(
            title='Choose ' + ftype + ' file',
            content=box,
            size_hint=(0.95, 0.88),
            background_color=get_color_from_hex(C_CARD),
        )

        def do_select(*a):
            if fc.selection:
                path = fc.selection[0]
                p.dismiss()
                self._read_file(path, ftype)

        sel_btn.bind(on_press=do_select)
        can_btn.bind(on_press=p.dismiss)
        p.open()

    def _read_file(self, path, ftype):
        self.status_lbl.text = 'Reading file...'
        self.prog.value = 20

        def worker():
            text = ''
            try:
                if ftype == 'TXT':
                    text = read_txt(path)
                elif ftype == 'PDF':
                    text = read_pdf(path)
                elif ftype == 'DOCX':
                    text = read_docx(path)
            except Exception as e:
                text = ''
                Clock.schedule_once(lambda dt: setattr(
                    self.status_lbl, 'text',
                    'File read error: ' + str(e)[:40]))

            def apply(dt):
                if text.strip():
                    self.txt.text = text
                    self.status_lbl.text = 'File imported! Text ready.'
                    self.prog.value = 100
                else:
                    self.status_lbl.text = 'Could not read file. Try TXT format.'
                    self.prog.value = 0

            Clock.schedule_once(apply)

        threading.Thread(target=worker, daemon=True).start()

    def _set_ready(self, audio_ok=True):
        self.gen_btn.disabled = False
        self.play_btn.disabled = not audio_ok
        self.dl_btn.disabled = not audio_ok

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
            self.status_lbl.text = 'Please enter text first!'
            return
        self._set_busy()
        self._upd(0, 'Starting generation...')
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            from gtts import gTTS

            Clock.schedule_once(lambda dt: self._upd(20, 'Connecting to server...'))

            lang = LANGUAGES.get(self.lang_spin.text, 'en')
            prof = VOICE_PROFILES.get(self.voice_sel, VOICE_PROFILES['Male'])
            speed_val = int(self.speed_slider.value)
            use_slow = speed_val <= 40

            Clock.schedule_once(lambda dt: self._upd(50, 'Generating voice...'))

            tts = gTTS(
                text=self.txt.text,
                lang=lang,
                tld=prof['tld'],
                slow=use_slow,
            )

            out = os.path.join(
                App.get_running_app().user_data_dir,
                'tts_output.mp3')

            Clock.schedule_once(lambda dt: self._upd(80, 'Saving audio...'))
            tts.save(out)
            self.out_file = out

            Clock.schedule_once(lambda dt: self._on_done())

        except Exception as exc:
            msg = str(exc)
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
        self._upd(100, 'Audio ready! Preview or Download.')
        self._set_ready(audio_ok=True)

    def _on_err(self, msg):
        m = msg.lower()
        if any(k in m for k in ['network', 'connection', 'gaierror', 'timeout']):
            txt = 'No internet! gTTS needs internet.'
        elif 'lang' in m:
            txt = 'This language+voice combo not supported.'
        else:
            txt = 'Error: ' + msg[:50]
        self._upd(0, txt)
        self._set_ready(audio_ok=False)

    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = 'Preview Audio'
        else:
            self._audio.play()
            self.play_btn.text = 'Stop Preview'

    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status_lbl.text = 'Generate audio first!'
            return
        self._show_save_dialog()

    def _show_save_dialog(self):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(lbl('Where to save?', 14, C_WHITE, True, 32))

        options = []
        if ANDROID_ENV:
            options = [
                ('Internal Storage', '/sdcard'),
                ('Downloads Folder', '/sdcard/Download'),
                ('Music Folder', '/sdcard/Music'),
                ('Documents Folder', '/sdcard/Documents'),
            ]
            try:
                ext = primary_external_storage_path()
                if ext and ext != '/sdcard':
                    options.append(('SD Card', ext))
                    options.append(('SD Card Downloads', os.path.join(ext, 'Download')))
            except Exception:
                pass
        else:
            home = os.path.expanduser('~')
            options = [
                ('Home Folder', home),
                ('Downloads', os.path.join(home, 'Downloads')),
                ('Desktop', os.path.join(home, 'Desktop')),
            ]

        sv = ScrollView(size_hint=(1, 1))
        btn_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None, spacing=8)
        btn_box.bind(minimum_height=btn_box.setter('height'))

        pop = [None]

        for label_txt, path in options:
            b = FlatBtn(
                text=label_txt + '\n' + path,
                bg=C_CARD2,
                size_hint_y=None, height=62,
                font_size='12sp',
            )
            b.bind(on_press=lambda x, p=path, pp=pop: self._do_save(p, pp[0]))
            btn_box.add_widget(b)

        sv.add_widget(btn_box)
        box.add_widget(sv)

        cancel = FlatBtn(text='Cancel', bg=C_GRAY, size_hint_y=None, height=48)
        box.add_widget(cancel)

        p = Popup(
            title='Save Audio File',
            content=box,
            size_hint=(0.92, 0.72),
            background_color=get_color_from_hex(C_CARD),
        )
        pop[0] = p
        cancel.bind(on_press=p.dismiss)
        p.open()

    def _do_save(self, dest_dir, popup):
        if popup:
            popup.dismiss()

        fname = 'Titan_' + self.lang_spin.text + '_' + str(int(time.time())) + '.mp3'
        dest = os.path.join(dest_dir, fname)

        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self.save_dir = dest_dir
            self.status_lbl.text = 'Saved: ' + fname

            history_save({
                'filename': fname,
                'path': dest,
                'lang': self.lang_spin.text,
                'voice': self.voice_sel,
                'time': time.strftime('%d %b %Y  %H:%M'),
            })

            box = BoxLayout(orientation='vertical', padding=16, spacing=12)
            box.add_widget(Label(
                text='File saved!\n\n' + fname + '\n\nLocation:\n' + dest_dir,
                color=get_color_from_hex(C_WHITE),
                font_size='13sp',
            ))
            ok = FlatBtn(text='OK', bg=C_GREEN, size_hint_y=None, height=52)
            box.add_widget(ok)
            p = Popup(
                title='Download Complete',
                content=box,
                size_hint=(0.88, 0.48),
                background_color=get_color_from_hex(C_CARD),
            )
            ok.bind(on_press=p.dismiss)
            p.open()

        except Exception as e:
            self.status_lbl.text = 'Save failed: ' + str(e)[:45]


class TitanApp(App):
    def build(self):
        self.title = 'Titan AI Studio Pro'
        sm = ScreenManager(transition=FadeTransition())
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
