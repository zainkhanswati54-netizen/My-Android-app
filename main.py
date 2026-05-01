from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from gtts import gTTS
import os

class VoiceApp(App):
    def build(self):
        # Background color aur styling
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Text Input Styling
        self.txt_input = TextInput(
            text='Kasay ho dost', 
            multiline=True, 
            size_hint=(1, 0.4),
            font_size='25sp',
            background_color=(1, 1, 1, 1)
        )
        
        # Professional Button
        speak_btn = Button(
            text='Awaz Suniye!', 
            size_hint=(1, 0.2),
            background_color=(0.05, 0.3, 0.4, 1), # Dark Blue
            color=(1, 1, 1, 1),
            font_size='22sp',
            bold=True
        )
        speak_btn.bind(on_press=self.generate_and_play)
        
        self.layout.add_widget(self.txt_input)
        self.layout.add_widget(speak_btn)
        return self.layout

    def generate_and_play(self, instance):
        text = self.txt_input.text
        if text.strip():
            filename = "speech.mp3"
            # Voice generate karna
            tts = gTTS(text=text, lang='hi')
            tts.save(filename)
            
            # Audio play karna
            sound = SoundLoader.load(filename)
            if sound:
                sound.play()
