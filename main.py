import os
import threading
import time
import shutil
import json

try:
    from android.permissions import request_permissions, Permission
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
from kivy.utils import get_color_from_hex

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
    'Child':  {'tld': 'co.uk',  'slow': True},
    'News':   {'tld': 'ca',     'slow': False},
    'Soft':   {'tld': 'co.in',  'slow': True},
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
            json.dump(data[:50], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


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
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])


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


class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = DarkPanel()
        root.add_widget(Label(
            text='TITAN AI',
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
            text='Loading...',
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
        self._ev = Clock.schedule_interval(self._tick, 0.035)

    def on_leave(self, *a):
        if hasattr(self, '_ev'):
            self._ev.cancel()

    def _tick(self, dt):
        self.pb.value = min(self.pb.value + 2, 100)
        v = self.pb.value
        if v == 30:
            self.info.text = 'Loading audio engine...'
        elif v == 60:
            self.info.text = 'Preparing voice profiles...'
        elif v == 85:
            self.info.text = 'Almost ready...'
        if v >= 100:
            self._ev.cancel()
            Clock.schedule_once(
                lambda dt: setattr(self.manager, 'current', 'studio'), 0.3)


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
            text='Back', bg=C_GRAY,
            size_hint_x=None, width=100, font_size='15sp')
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
            size_hint_y=None, spacing=8, padding=[0, 5])
        self.list_box.bind(
            minimum_height=self.list_box.setter('height'))
        sv.add_widget(self.list_box)
        outer.add_widget(sv)

        clr = FlatBtn(
            text='Clear All History', bg='#7F1D1D',
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
                text='No downloads yet.',
                color=get_color_from_hex('#64748B'),
                size_hint_y=None, height=60,
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

            info = BoxLayout(orientation='vertical', size_hint_x=0.80)
            info.add_widget(Label(
                text=entry.get('filename', 'unknown'),
                font_size='13sp', bold=True,
                color=(0.9, 0.9, 0.9, 1),
                halign='left', valign='middle',
                size_hint_y=None, height=36,
            ))
            info.add_widget(Label(
                text=(entry.get('lang', '') + '   ' +
                      entry.get('voice', '') + '   ' +
                      entry.get('time', '')),
                font_size='11sp',
                color=(0.4, 0.8, 0.4, 1),
                halign='left', valign='middle',
                size_hint_y=None, height=28,
            ))
            row.add_widget(info)

            fp = entry.get('path', '')
            if os.path.exists(fp):
                pb = FlatBtn(
                    text='PLAY', bg=C_GREEN,
                    size_hint_x=None, width=68, font_size='13sp')
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

        content.add_widget(Label(
            text='TITAN AI STUDIO PRO',
            font_size='28sp', bold=True,
            color=get_color_from_hex(C_ACCENT),
            size_hint_y=None, height=80,
        ))

        content.add_widget(sec_label('LANGUAGE'))
        self.lang_spin = Spinner(
            text='English',
            values=list(LANGUAGES.keys()),
            size_hint_y=None, height=55,
            font_size='16sp',
            color=(1, 1, 1, 1),
            background_color=get_color_from_hex('#1E3A5F'),
        )
        content.add_widget(self.lang_spin)

        content.add_widget(sec_label('VOICE TYPE'))
        vgrid = GridLayout(
            cols=3, rows=2,
            size_hint_y=None, height=130, spacing=8)
        self._vbtns = {}
        for name in VOICE_PROFILES:
            b = FlatBtn(text=name, bg='#1E3A5F', font_size='14sp')
            b.bind(on_press=lambda *a, n=name: self._pick_voice(n))
            vgrid.add_widget(b)
            self._vbtns[name] = b
        content.add_widget(vgrid)
        self._pick_voice('Male')

        content.add_widget(sec_label('SCRIPT'))
        self.txt = TextInput(
            hint_text='Yahan apna text likho...',
            multiline=True,
            size_hint_y=None, height=240,
            background_color=get_color_from_hex(C_CARD),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.4, 0.4, 0.4, 1),
            cursor_color=get_color_from_hex(C_ACCENT),
            font_size='17sp',
            padding=[16, 16],
        )
        self.txt.bind(text=self._count)
        content.add_widget(self.txt)

        self.count_lbl = Label(
            text='Words: 0   Chars: 0',
            font_size='12sp',
            color=get_color_from_hex('#475569'),
            size_hint_y=None, height=28,
        )
        content.add_widget(self.count_lbl)

        content.add_widget(sec_label('SPEED'))
        self.speed_lbl = Label(
            text='Selected: Normal',
            font_size='13sp',
            color=get_color_from_hex(C_GREEN),
            size_hint_y=None, height=30,
        )
        content.add_widget(self.speed_lbl)
        srow = BoxLayout(size_hint_y=None, height=58, spacing=10)
        self._sbtns = {}
        for spd, col in [('Slow', C_INDIGO), ('Normal', C_GREEN), ('Fast', C_AMBER)]:
            b = FlatBtn(text=spd, bg=col, font_size='15sp')
            b.bind(on_press=lambda *a, s=spd: self._pick_speed(s))
            srow.add_widget(b)
            self._sbtns[spd] = b
        content.add_widget(srow)
        self._pick_speed('Normal')

        self.status_lbl = Label(
            text='Ready',
            font_size='14sp', italic=True,
            color=get_color_from_hex('#64748B'),
            size_hint_y=None, height=38,
        )
        content.add_widget(self.status_lbl)

        self.prog = ProgressBar(
            max=100, value=0,
            size_hint_y=None, height=14)
        content.add_widget(self.prog)

        self.gen_btn = FlatBtn(
            text='GENERATE SPEECH', bg=C_BLUE,
            size_hint_y=None, height=85,
            font_size='18sp', bold=True)
        self.gen_btn.bind(on_press=self._generate)
        content.add_widget(self.gen_btn)

        ps = BoxLayout(size_hint_y=None, height=72, spacing=12)
        self.play_btn = FlatBtn(
            text='PLAY', bg=C_GREEN,
            font_size='16sp', disabled=True)
        self.stop_btn = FlatBtn(
            text='STOP', bg=C_RED,
            font_size='16sp', disabled=True)
        self.play_btn.bind(on_press=self._play)
        self.stop_btn.bind(on_press=self._stop)
        ps.add_widget(self.play_btn)
        ps.add_widget(self.stop_btn)
        content.add_widget(ps)

        self.dl_btn = FlatBtn(
            text='DOWNLOAD AUDIO', bg=C_CYAN,
            size_hint_y=None, height=78,
            font_size='17sp', disabled=True)
        self.dl_btn.bind(on_press=self._download)
        content.add_widget(self.dl_btn)

        hbtn = FlatBtn(
            text='DOWNLOAD HISTORY', bg=C_PURPLE,
            size_hint_y=None, height=68, font_size='16sp')
        hbtn.bind(on_press=lambda *a: setattr(
            self.manager, 'current', 'history'))
        content.add_widget(hbtn)

        cbtn = FlatBtn(
            text='CLEAR TEXT', bg=C_GRAY,
            size_hint_y=None, height=60, font_size='15sp')
        cbtn.bind(on_press=lambda *a: setattr(self.txt, 'text', ''))
        content.add_widget(cbtn)

        content.add_widget(Label(size_hint_y=None, height=30))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _pick_voice(self, name):
        self.voice_sel = name
        for n, b in self._vbtns.items():
            b.set_bg(C_GREEN if n == name else '#1E3A5F')

    def _pick_speed(self, spd):
        self.speed_sel = spd
        self.speed_lbl.text = 'Selected: ' + spd
        colors = {'Slow': C_INDIGO, 'Normal': C_GREEN, 'Fast': C_AMBER}
        for n, b in self._sbtns.items():
            b.set_bg(C_ACCENT if n == spd else colors[n])

    def _count(self, inst, val):
        w = len(val.split()) if val.strip() else 0
        self.count_lbl.text = 'Words: ' + str(w) + '   Chars: ' + str(len(val))

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
            self.status_lbl.text = 'Error: Text khaali hai!'
            return
        self._set_busy()
        self._upd_status(0, 'Starting...')
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            from gtts import gTTS
            Clock.schedule_once(
                lambda dt: self._upd_status(20, 'Connecting...'))
            lang = LANGUAGES.get(self.lang_spin.text, 'en')
            prof = VOICE_PROFILES.get(self.voice_sel, VOICE_PROFILES['Male'])
            slow = (self.speed_sel == 'Slow') or prof['slow']
            Clock.schedule_once(
                lambda dt: self._upd_status(50, 'Generating audio...'))
            tts = gTTS(
                text=self.txt.text,
                lang=lang,
                tld=prof['tld'],
                slow=slow,
            )
            out = os.path.join(
                App.get_running_app().user_data_dir,
                'tts_output.mp3')
            Clock.schedule_once(
                lambda dt: self._upd_status(80, 'Saving file...'))
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
        self._upd_status(100, 'Done! Play ya Download karo.')
        self._set_ready(audio_ok=True)

    def _on_err(self, msg):
        m = msg.lower()
        if any(k in m for k in ['network', 'connection', 'gaierror', 'timeout']):
            txt = 'Error: Internet nahi hai!'
        elif 'lang' in m:
            txt = 'Error: Is language ke saath yeh voice nahi chalti.'
        else:
            txt = 'Error: ' + msg[:55]
        self._upd_status(0, txt)
        self._set_ready(audio_ok=False)

    def _play(self, *a):
        if not self._audio:
            return
        if self._audio.state == 'play':
            self._audio.stop()
            self.play_btn.text = 'PLAY'
        else:
            self._audio.play()
            self.play_btn.text = 'PAUSE'

    def _stop(self, *a):
        if self._audio:
            self._audio.stop()
        self.play_btn.text = 'PLAY'

    def _download(self, *a):
        if not self.out_file or not os.path.exists(self.out_file):
            self.status_lbl.text = 'Error: Pehle speech generate karo!'
            return
        fname = 'Titan_' + self.lang_spin.text + '_' + str(int(time.time())) + '.mp3'
        dest_dir = '/sdcard/Download' if ANDROID_ENV else os.path.expanduser('~')
        dest = os.path.join(dest_dir, fname)
        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copyfile(self.out_file, dest)
            self.status_lbl.text = 'Saved: ' + fname
            history_save({
                'filename': fname,
                'path': dest,
                'lang': self.lang_spin.text,
                'voice': self.voice_sel,
                'speed': self.speed_sel,
                'time': time.strftime('%d %b %Y  %H:%M'),
            })
            box = BoxLayout(orientation='vertical', padding=20, spacing=12)
            box.add_widget(Label(
                text='File save ho gayi!\n\n' + fname + '\n\nLocation:\n' + dest_dir,
                color=(1, 1, 1, 1), font_size='14sp',
            ))
            ok = FlatBtn(text='OK', bg=C_GREEN, size_hint_y=None, height=55)
            box.add_widget(ok)
            pop = Popup(
                title='Download Complete',
                content=box,
                size_hint=(0.88, 0.50),
                background_color=get_color_from_hex(C_CARD),
            )
            ok.bind(on_press=pop.dismiss)
            pop.open()
        except Exception as e:
            self.status_lbl.text = 'Download failed: ' + str(e)[:50]

class TitanApp(App):
    def build(self):
        self.title = 'Titan AI Studio Pro'
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(StudioScreen(name='studio'))
        sm.add_widget(HistoryScreen(name='history'))
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


if __name__ == '__main__':
    TitanApp().run()
