from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from gtts import gTTS
import os

class VoiceApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Text Input jahan user likhega
        self.txt_input = TextInput(
            text='Yahan kuch likhein...', 
            multiline=False, 
            size_hint=(1, 0.2)
        )
        
        # Bolne wala button
        speak_btn = Button(
            text='Awaz Suniye!', 
            size_hint=(1, 0.2),
            background_color=(0, 0.7, 0.9, 1)
        )
        speak_btn.bind(on_press=self.generate_voice)
        
        layout.add_widget(self.txt_input)
        layout.add_widget(speak_btn)
        return layout

    def generate_voice(self, instance):
        text = self.txt_input.text
        if text.strip():
            tts = gTTS(text=text, lang='hi') # Urdu/Hindi ke liye 'hi' ya 'ur'
            tts.save("speech.mp3")
            # Note: Mobile par play karne ke liye humein baad mein 
            # ek 'audio player' library bhi chahiye hogi, abhi ye sirf file banayega.
            print("Awaz tayyar hai!")

if __name__ == '__main__':
    VoiceApp().run()
