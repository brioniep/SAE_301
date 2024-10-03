from datetime import datetime, time as dt_time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock
#mqtt
from MQTT import *


class LoginScreen(Screen):
    def on_login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if username == "" and password == "":
            self.resetForm()
            self.resetLabel()
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = 'success'

            # Appel de la méthode start_updating_temperature
            success_screen = self.manager.get_screen('success')
            success_screen.start_updating_temperature()  # Démarrer la mise à jour continue
        else:
            self.resetForm()
            self.ids.message_label.text = "Nom d'utilisateur ou mdp incorrect"
            Clock.schedule_once(self.clear_message, 2.5)





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
        self.is_on = False

    def on_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'login'

   
    def update_temperature(self, dt=None):
        client = MQTT()
        client.connection()
        temperature = client.get_messages()
        self.ids.temperature_2.text = f"{temperature}  C° "
        print("message reçu : ", temperature)

    def start_updating_temperature(self):
        # Mettre à jour la température toutes les 5 secondes
        Clock.schedule_interval(self.update_temperature, 5)

    def stop_updating_temperature(self):
        # Arrêter la mise à jour de la température
        Clock.unschedule(self.update_temperature)







    def update_led_3(self):
        # Vérifier l'état des deux premières LEDs
        if (self.ids.button_on_1.background_color == [0, 1, 0, 1] and
            self.ids.button_on_2.background_color == [0, 1, 0, 1]):
            # Si les deux sont allumées, mettre la LED 3 sur ON
            self.ids.button_on_3.background_color = [0, 1, 0, 1]
            self.ids.button_off_3.background_color = [0.5, 0.5, 0.5, 1]
        else:
            # Sinon, mettre la LED 3 sur OFF
            self.ids.button_off_3.background_color = [1, 0, 0, 1]
            self.ids.button_on_3.background_color = [0.5, 0.5, 0.5, 1]

    def toggle_on_1(self):
        self.ids.button_on_1.background_color = [0, 1, 0, 1]
        self.ids.button_off_1.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.good_message.text = "Led 1 activée !"
        Clock.schedule_once(self.clear_message, 1)
        # Mettre à jour l'état de la troisième LED
        self.update_led_3()

    def toggle_off_1(self):
        self.ids.button_off_1.background_color = [1, 0, 0, 1]
        self.ids.button_on_1.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.bad_message.text = "Led 1 désactivée !"
        Clock.schedule_once(self.clear_message, 1)
        # Mettre à jour l'état de la troisième LED
        self.update_led_3()

    def toggle_on_2(self):
        self.ids.button_on_2.background_color = [0, 1, 0, 1]
        self.ids.button_off_2.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.good_message.text = "Led 2 activée !"
        Clock.schedule_once(self.clear_message, 1)
        # Mettre à jour l'état de la troisième LED
        self.update_led_3()

    def toggle_off_2(self):
        self.ids.button_off_2.background_color = [1, 0, 0, 1]
        self.ids.button_on_2.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.bad_message.text = "Led 2 désactivée !"
        Clock.schedule_once(self.clear_message, 1)
        # Mettre à jour l'état de la troisième LED
        self.update_led_3()

    def toggle_on_3(self):
        # Allumer les deux premières LEDs
        self.ids.button_on_1.background_color = [0, 1, 0, 1]
        self.ids.button_off_1.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.button_on_2.background_color = [0, 1, 0, 1]
        self.ids.button_off_2.background_color = [0.5, 0.5, 0.5, 1]

        # Mettre à jour la LED 3
        self.ids.button_on_3.background_color = [0, 1, 0, 1]
        self.ids.button_off_3.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.good_message.text = "Toutes les LEDs activées !"
        Clock.schedule_once(self.clear_message, 1)

    def toggle_off_3(self):
        # Éteindre les deux premières LEDs
        self.ids.button_off_1.background_color = [1, 0, 0, 1]
        self.ids.button_on_1.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.button_off_2.background_color = [1, 0, 0, 1]
        self.ids.button_on_2.background_color = [0.5, 0.5, 0.5, 1]

        # Mettre à jour la LED 3
        self.ids.button_off_3.background_color = [1, 0, 0, 1]
        self.ids.button_on_3.background_color = [0.5, 0.5, 0.5, 1]
        self.ids.bad_message.text = "Toutes les LEDs désactivées !"
        Clock.schedule_once(self.clear_message, 1)






    def save_time_schedule(self):
        # Définir current_date avant de l'utiliser
        current_date = datetime.now().date()

        # Extraire les valeurs des champs de saisie
        start_hour1 = int(self.ids.start_hour.text)
        start_minute1 = int(self.ids.start_minute.text)
        end_hour1 = int(self.ids.end_hour.text)
        end_minute1 = int(self.ids.end_minute.text)

        start_hour2 = int(self.ids.start_hour2.text)
        start_minute2 = int(self.ids.start_minute2.text)
        end_hour2 = int(self.ids.end_hour2.text)
        end_minute2 = int(self.ids.end_minute2.text)

        # Utiliser current_date avec dt_time
        start_time1 = datetime.combine(current_date, dt_time(start_hour1, start_minute1))
        end_time1 = datetime.combine(current_date, dt_time(end_hour1, end_minute1))
        start_time2 = datetime.combine(current_date, dt_time(start_hour2, start_minute2))
        end_time2 = datetime.combine(current_date, dt_time(end_hour2, end_minute2))

        # Convertir les temps en timestamps
        start_timestamp1 = int(start_time1.timestamp())
        end_timestamp1 = int(end_time1.timestamp())
        start_timestamp2 = int(start_time2.timestamp())
        end_timestamp2 = int(end_time2.timestamp())

        # Vérifier si les plages horaires sont configurées
        is_schedule1_configured = not (start_hour1 == 0 and start_minute1 == 0 and end_hour1 == 0 and end_minute1 == 0)
        is_schedule2_configured = not (start_hour2 == 0 and start_minute2 == 0 and end_hour2 == 0 and end_minute2 == 0)

        if is_schedule1_configured:
            if start_timestamp1 >= end_timestamp1:
                self.ids.bad_message.text = "Plage 1 : échec lors de l'enregistrement"
                Clock.schedule_once(self.clear_message, 3)
                return

        if is_schedule2_configured:
            if start_timestamp2 >= end_timestamp2:
                self.ids.bad_message.text = "Plage 2 : échec lors de l'enregistrement"
                Clock.schedule_once(self.clear_message, 3)
                return

        if not (is_schedule1_configured or is_schedule2_configured):
            self.ids.bad_message.text = "Aucune plage horaire configurée"
            Clock.schedule_once(self.clear_message, 3)
            return

        self.ids.good_message.text = "Enregistrement réussi !"
        Clock.schedule_once(self.clear_message, 3)


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
