from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from gtts import gTTS
import os

class VoiceBotPro(App):
    def build(self):
        # Professional Dark Blue Theme
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        
        # Header
        self.header = Label(
            text='VOICE GENERATOR PRO', 
            font_size='28sp', 
            bold=True, 
            size_hint=(1, 0.2),
            color=(0.1, 0.6, 0.9, 1)
        )
        
        # English Input
        self.txt_input = TextInput(
            hint_text='Type English text here...', 
            multiline=True, 
            size_hint=(1, 0.4),
            font_size='18sp'
        )
        
        # Action Button
        self.speak_btn = Button(
            text='GENERATE & SAVE', 
            background_normal='',
            background_color=(0.05, 0.3, 0.5, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
            bold=True
        )
        self.speak_btn.bind(on_press=self.generate_voice)
        
        self.status_label = Label(text='Status: Ready', color=(0.8, 0.8, 0.8, 1))

        self.layout.add_widget(self.header)
        self.layout.add_widget(self.txt_input)
        self.layout.add_widget(self.speak_btn)
        self.layout.add_widget(self.status_label)
        
        return self.layout

    def generate_voice(self, instance):
        text = self.txt_input.text
        if text.strip():
            try:
                self.status_label.text = "Generating..."
                
                # App ke internal folder mein save karna (Sabse safe rasta)
                # Isse permission ka error nahi aayega
                filename = "my_voice.mp3"
                tts = gTTS(text=text, lang='en')
                tts.save(filename)
                
                self.status_label.text = "Success! File Saved."
                self.status_label.color = (0, 1, 0, 1)
            except Exception as e:
                self.status_label.text = "Check Internet Connection"
                self.status_label.color = (1, 0, 0, 1)
