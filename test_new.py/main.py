from datetime import time
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition


class LoginScreen(Screen):
    def on_login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if username == "" and password == "":            
            self.resetForm()
            self.resetLabel()
            self.manager.transition = SlideTransition(direction="left")  # Glisse vers la gauche
            self.manager.current = 'success'  # Changer d'écran

        else:
            self.ids.message_label.text = "Nom d'utilisateur ou mdp incorrect"
            self.resetForm()

    def resetForm(self):
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
    
    def resetLabel(self):
        self.ids.message_label.text = ""







class SuccessScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_back(self):
        self.manager.transition = SlideTransition(direction="right")  # Glisse vers la droite
        self.manager.current = 'login'  # Revenir à l'écran de connexion


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SuccessScreen(name='success'))
        return sm


if __name__ == '__main__':
    Window.size = (360, 640)
    Builder.load_file("main.kv")
    MyApp().run()
