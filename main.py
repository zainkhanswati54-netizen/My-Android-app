from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Welcome message
        hello_label = Label(
            text='Salam Dost! App Chal Gayi!', 
            font_size='30sp',
            color=(0, 1, 0, 1)  # Green color
        )
        
        # Simple Button
        btn = Button(
            text='Mubarak Ho!', 
            size_hint=(.8, .2), 
            pos_hint={'center_x': .5}
        )
        
        layout.add_widget(hello_label)
        layout.add_widget(btn)
        
        return layout

if __name__ == '__main__':
    TestApp().run()
