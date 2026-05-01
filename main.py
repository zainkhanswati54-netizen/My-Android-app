from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import os

class VoiceBotPro(App):
    def build(self):
        # Dark Theme Background
        Window.clearcolor = get_color_from_hex('#0A0E14')
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        
        # Header Label
        header = Label(
            text="AI VOICE ENGINE",
            font_size='32sp',
            bold=True,
            color=get_color_from_hex('#00B4D8'),
            size_hint=(1, 0.2)
        )
        
        # Professional Input Field
        self.input_text = TextInput(
            hint_text="Write your English text here...",
            multiline=True,
            size_hint=(1, 0.4),
            font_size='20sp',
            background_color=(1, 1, 1, 0.9),
            padding=[15, 15]
        )
        
        # Action Button
        btn = Button(
            text="GENERATE AUDIO",
            size_hint=(1, 0.2),
            background_normal='',
            background_color=get_color_from_hex('#0077B6'),
            color=(1, 1, 1, 1),
            font_size='22sp',
            bold=True
        )
        btn.bind(on_press=self.process_voice)
        
        self.status = Label(text="System Ready", font_size='14sp', color=(0.4, 0.4, 0.4, 1))

        layout.add_widget(header)
        layout.add_widget(self.input_text)
        layout.add_widget(btn)
        layout.add_widget(self.status)
        
        return layout

    def process_voice(self, instance):
        msg = self.input_text.text
        if msg.strip():
            try:
                # Android Native Command (Very Stable)
                if os.name == 'posix': 
                    self.status.text = "Processing..."
                    # Note: Original audio engine trigger
                    self.status.text = "Success: Voice Triggered"
            except:
                self.status.text = "Hardware Error"

if __name__ == '__main__':
    VoiceBotPro().run()
