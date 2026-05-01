from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from plyer import tts # Native Text-to-Speech

class VoiceBotPro(App):
    def build(self):
        # Professional Background Color
        Window.clearcolor = (0.02, 0.05, 0.1, 1) # Dark Navy Blue
        
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        
        # Header
        self.header = Label(
            text='VOICE GENERATOR PRO', 
            font_size='32sp', 
            bold=True, 
            size_hint=(1, 0.2),
            color=(0, 0.7, 1, 1) # Cyan Blue
        )
        
        # Professional English Input Box
        self.txt_input = TextInput(
            hint_text='Enter English text to speak...', 
            multiline=True, 
            size_hint=(1, 0.4),
            font_size='20sp',
            background_color=(1, 1, 1, 0.9),
            foreground_color=(0, 0, 0, 1),
            padding=[15, 15]
        )
        
        # Speak Button Styling
        self.speak_btn = Button(
            text='SPEAK NOW', 
            size_hint=(1, 0.2),
            background_normal='',
            background_color=(0, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='22sp',
            bold=True
        )
        self.speak_btn.bind(on_press=self.speak_text)
        
        self.status = Label(text='Status: System Online', font_size='14sp', color=(0.5, 0.5, 0.5, 1))

        self.layout.add_widget(self.header)
        self.layout.add_widget(self.txt_input)
        self.layout.add_widget(self.speak_btn)
        self.layout.add_widget(self.status)
        
        return self.layout

    def speak_text(self, instance):
        text = self.txt_input.text
        if text.strip():
            try:
                # Plyer mobile ke native TTS engine ko call karega
                tts.speak(text)
                self.status.text = "Status: Speaking..."
            except Exception as e:
                self.status.text = f"Error: Hardware Not Responding"

if __name__ == '__main__':
    VoiceBotPro().run()
