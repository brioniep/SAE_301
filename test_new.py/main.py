from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen


class TestApp(Screen) :
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    
    def on_login(self,):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if username == "leonard" and password =="toto":
            self.ids.message_label.text = "Vous etes connecté ! "
        
        else:
            self.ids.message_label.text = "Nom d'utilisateur ou mdp incorrect"







class MyApp(App):
    def build(self):
        
        return TestApp()
    
if __name__ == '__main__':
    Window.size = (360,640)
    Builder.load_file("main.kv")
    MyApp().run()