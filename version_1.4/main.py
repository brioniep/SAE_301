from datetime import time
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock
import time
from kivy.uix.screenmanager import Screen, SlideTransition
from datetime import datetime, time



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
    def save_time_schedule(self):
        # Plage Horaire 1
        start_hour1 = int(self.ids.start_hour.text)
        start_minute1 = int(self.ids.start_minute.text)
        end_hour1 = int(self.ids.end_hour.text)
        end_minute1 = int(self.ids.end_minute.text)

        # Plage Horaire 2
        start_hour2 = int(self.ids.start_hour2.text)
        start_minute2 = int(self.ids.start_minute2.text)
        end_hour2 = int(self.ids.end_hour2.text)
        end_minute2 = int(self.ids.end_minute2.text)

        current_date = datetime.now().date()

        # Création des objets datetime pour les deux plages horaires
        start_time1 = datetime.combine(current_date, time(start_hour1, start_minute1))
        end_time1 = datetime.combine(current_date, time(end_hour1, end_minute1))

        start_time2 = datetime.combine(current_date, time(start_hour2, start_minute2))
        end_time2 = datetime.combine(current_date, time(end_hour2, end_minute2))

        # Conversion en timestamp
        start_timestamp1 = int(start_time1.timestamp())
        end_timestamp1 = int(end_time1.timestamp())

        start_timestamp2 = int(start_time2.timestamp())
        end_timestamp2 = int(end_time2.timestamp())

        # Vérification de la validité des deux plages horaires
        if start_timestamp1 >= end_timestamp1:
            self.ids.bad_message.text = "Plage 1 : Erreur dans la configuration"
            Clock.schedule_once(self.clear_message, 3)

        elif start_timestamp2 >= end_timestamp2:
            self.ids.bad_message.text = "Plage 2 : Erreur dans la configuration"
            Clock.schedule_once(self.clear_message, 3)

        else:
            self.ids.good_message.text = "Plages horraires enregistrées ! "
            Clock.schedule_once(self.clear_message, 3)

        print(f"Plage horaire 1 : début {start_timestamp1}, fin {end_timestamp1}")
        print(f"Plage horaire 2 : début {start_timestamp2}, fin {end_timestamp2}")
    
    def clear_message(self, dt):
        self.ids.good_message.text = ""
        self.ids.bad_message.text = ""






    def clear_message(self, dt):
        self.ids.good_message.text = ""
        self.ids.bad_message.text = ""



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
