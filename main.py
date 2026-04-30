from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

class TestApp(MDApp):
    def build(self):
        screen = MDScreen()
        self.label = MDLabel(
            text="Salam! Ye meri pehli App hai",
            halign="center",
            pos_hint={"center_y": 0.6}
        )
        btn = MDRaisedButton(
            text="Click Karein!",
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            on_release=self.button_pressed
        )
        screen.add_widget(self.label)
        screen.add_widget(btn)
        return screen

    def button_pressed(self, instance):
        self.label.text = "Zabardast! Button kaam kar raha hai."

TestApp().run()

