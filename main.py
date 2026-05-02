from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
import threading
from gtts import gTTS
import os

class ProVoiceApp(App):
    def build(self):
        self.sound_path = None
        self.is_playing = False
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.txt = TextInput(hint_text="Enter English text...", size_hint=(1, 0.4), font_size='18sp')
        self.bar = ProgressBar(max=100, value=0, size_hint=(1, 0.1), opacity=0)
        self.status = Label(text="Ready to Generate", size_hint=(1, 0.1), color=(0, 1, 0, 1))
        
        # Action Buttons
        self.gen_btn = Button(text="GENERATE & SAVE VOICE", size_hint=(1, 0.2), bold=True, background_color=(0, 0.5, 0.8, 1))
        self.gen_btn.bind(on_press=self.start_thread)
        
        layout.add_widget(self.txt)
        layout.add_widget(self.bar)
        layout.add_widget(self.status)
        layout.add_widget(self.gen_btn)
        return layout

    def start_thread(self, instance):
        if self.txt.text.strip():
            self.gen_btn.disabled = True
            self.bar.opacity = 1
            self.status.text = "Processing... Please Wait"
            threading.Thread(target=self.generate_audio).start()

    def generate_audio(self):
        try:
            # Save path - Downloads folder for easy access
            save_folder = "/sdcard/Download"
            if not os.path.exists(save_folder):
                save_folder = os.getcwd()
                
            self.sound_path = os.path.join(save_folder, "my_voice_ai.mp3")
            
            tts = gTTS(text=self.txt.text, lang='en')
            tts.save(self.sound_path)
            
            Clock.schedule_once(lambda dt: self.finish_up())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error())

    def finish_up(self):
        self.bar.value = 100
        self.status.text = f"Saved in Downloads!\nPath: {self.sound_path}"
        self.gen_btn.disabled = False
        # Play using Android's internal system (No Crash)
        os.system(f"am start -a android.intent.action.VIEW -d file://{self.sound_path} -t audio/mp3")

    def show_error(self):
        self.status.text = "Error: Check Internet or Storage"
        self.gen_btn.disabled = False

if __name__ == '__main__':
    ProVoiceApp().run()
