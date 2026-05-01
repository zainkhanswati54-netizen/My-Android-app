from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import webbrowser

class VoiceBotPro(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#0A0E14')
        layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        
        header = Label(text="AI VOICE ENGINE PRO", font_size='30sp', bold=True, 
                       color=get_color_from_hex('#00B4D8'), size_hint=(1, 0.2))
        
        self.input_text = TextInput(hint_text="Type your long English text here...", 
                                    multiline=True, size_hint=(1, 0.5), font_size='18sp')
        
        btn = Button(text="GENERATE & DOWNLOAD", size_hint=(1, 0.2), bold=True,
                          background_normal='', background_color=get_color_from_hex('#0077B6'))
        btn.bind(on_press=self.open_voice_engine)
        
        status = Label(text="Stable Version: Online", font_size='12sp', color=(0.4, 0.4, 0.4, 1))

        layout.add_widget(header)
        layout.add_widget(self.input_text)
        layout.add_widget(btn)
        layout.add_widget(status)
        
        return layout

    def open_voice_engine(self, instance):
        text = self.input_text.text
        if text.strip():
            # Ye link text ko seedha professional engine mein le jayega jahan se download bhi ho sakega
            url = f"https://translate.google.com/?sl=en&tl=en&text={text}&op=translate"
            webbrowser.open(url)

if __name__ == '__main__':
    VoiceBotPro().run()
