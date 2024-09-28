from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition

class NotConnected(Screen):
    def disconnect(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'login'
        self.manager.get_screen('login').resetForm()