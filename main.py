from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from gtts import gTTS
import os

class VoiceBotPro(App):
    def build(self):
        # Main Layout with Professional Dark Theme
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        
        # App Header
        self.header = Label(
            text='VOICE GENERATOR PRO', 
            font_size='30sp', 
            bold=True, 
            size_hint=(1, 0.2),
            color=(0.1, 0.6, 0.9, 1) # Professional Blue
        )
        
        # English Text Input
        self.txt_input = TextInput(
            hint_text='Type your message here...', 
            multiline=True, 
            size_hint=(1, 0.4),
            font_size='20sp',
            padding=[10, 10]
        )
        
        # Action Buttons Layout
        self.btn_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 0.4))
        
        # Generate & Play Button
        self.speak_btn = Button(
            text='GENERATE VOICE', 
            background_normal='',
            background_color=(0.05, 0.3, 0.5, 1), # Dark Blue
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        self.speak_btn.bind(on_press=self.generate_voice)
        
        # Status Label
        self.status_label = Label(text='Status: Ready', color=(0.7, 0.7, 0.7, 1))

        self.layout.add_widget(self.header)
        self.layout.add_widget(self.txt_input)
        self.layout.add_widget(self.speak_btn)
        self.layout.add_widget(self.status_label)
        
        return self.layout

def generate_voice(self, instance):
        text = self.txt_input.text
        if text.strip():
            try:
                self.status_label.text = "Status: Generating..."
                # App ke andar hi file save karein taake crash na ho
                filename = "VoiceGenerated.mp3" 
                tts = gTTS(text=text, lang='en')
                tts.save(filename)
                
                self.status_label.text = "Status: Created Successfully!"
                self.status_label.color = (0, 1, 0, 1)
            except Exception as e:
                self.status_label.text = "Status: Storage Error"
                self.status_label.color = (1, 0, 0, 1)
                print(f"Error: {e}")
