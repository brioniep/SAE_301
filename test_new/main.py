from datetime import time
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock
import time
from kivy.uix.screenmanager import Screen, SlideTransition



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
            self.resetForm()
            self.ids.message_label.text = "Nom d'utilisateur ou mdp incorrect"
            Clock.schedule_once(self.clear_message, 2.5)  # Effacer le message après 2 secondes

    def resetForm(self):
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
    
    def resetLabel(self):
        self.ids.message_label.text = ""

    def clear_message(self, dt):
        self.ids.message_label.text = ""




class SuccessScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_back(self):
        self.manager.transition = SlideTransition(direction="right")  # Glisse vers la droite
        self.manager.current = 'login'  # Revenir à l'écran de connexion

    def clear_messages(self, dt):
        self.ids.bad_format1.text = ""
        self.ids.bad_format2.text = ""

    def on_save(self):
        champ1 = self.ids.horaires_1.text
        champ2 = self.ids.horaires_2.text
        champ3 = self.ids.horaires_3.text
        champ4 = self.ids.horaires_4.text

        def is_valid_time_format(time_str):
            if not time_str:
                return False  # Considérer les champs vides comme invalides
            try:
                time.strptime(time_str, '%H:%M')
                return True
            except ValueError:
                return False

        # Vérification des paires 1 et 2
        pair1_valid = is_valid_time_format(champ1) and is_valid_time_format(champ2)
        pair1_empty = not champ1 and not champ2

        # Vérification des paires 3 et 4
        pair2_valid = is_valid_time_format(champ3) and is_valid_time_format(champ4)
        pair2_empty = not champ3 and not champ4

        if pair1_empty and pair2_empty:
            self.ids.bad_format1.text = ""
            self.ids.bad_format2.text = ""
        elif pair1_valid and pair2_valid:
            self.ids.bad_format1.text = "Bon format"
            self.ids.bad_format1.color = (0, 1, 0, 1)  # Vert
            self.ids.bad_format2.text = "Bon format"
            self.ids.bad_format2.color = (0, 1, 0, 1)  # Vert
        elif pair1_valid and pair2_empty:
            self.ids.bad_format1.text = "Bon format"
            self.ids.bad_format1.color = (0, 1, 0, 1)  # Vert
            self.ids.bad_format2.text = ""
        elif pair2_valid and pair1_empty:
            self.ids.bad_format2.text = "Bon format"
            self.ids.bad_format2.color = (0, 1, 0, 1)  # Vert
            self.ids.bad_format1.text = ""
        else:
            self.ids.bad_format1.text = "Mauvais format"
            self.ids.bad_format1.color = (1, 0, 0, 1)  # Rouge
            self.ids.bad_format2.text = "Mauvais format"
            self.ids.bad_format2.color = (1, 0, 0, 1)  # Rouge

            # Effacer le texte des champs incorrects
            if not is_valid_time_format(champ1):
                self.ids.horaires_1.text = ""
            if not is_valid_time_format(champ2):
                self.ids.horaires_2.text = ""
            if not is_valid_time_format(champ3):
                self.ids.horaires_3.text = ""
            if not is_valid_time_format(champ4):
                self.ids.horaires_4.text = ""

        Clock.schedule_once(self.clear_messages, 3)  # Effacer les messages après 3 secondes




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
