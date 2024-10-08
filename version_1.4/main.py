from datetime import datetime, time as dt_time
import threading    
import time  # Assure-toi d'importer ce module pour utiliser sleep

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock
#mqtt
from MQTT import *


gris = [0.5, 0.5, 0.5, 1]
rouge = [1, 0, 0, 1]
vert = [0, 1, 0, 1]

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

    # Fonction pour lancer le thread séparé
    def start_updating_temperature(self):
        # Créer un thread pour écouter les messages MQTT sans bloquer l'interface
        threading.Thread(target=self.listen_for_temperature, daemon=True).start()

    # Fonction qui tourne en continu dans un thread séparé
    def listen_for_temperature(self):
        client = MQTT(topic="IUT/temperature")
        client.connection()

        while True:
            try:
                # Récupérer la température
                temperature = client.get_messages()

                # Mettre à jour l'UI de manière sûre en utilisant Clock.schedule_once
                Clock.schedule_once(lambda dt: self.update_temperature_ui(temperature))
                time.sleep(1)
                # Afficher la température dans le terminal pour le débogage
                print("Température reçue : ", temperature)

            except Exception as e:
                # Afficher un message d'erreur en cas de problème de connexion
                print(f"Erreur de connexion MQTT : {str(e)}")
                Clock.schedule_once(lambda dt: self.update_temperature_ui("Erreur de connexion"))

    # Fonction pour mettre à jour l'UI
    def update_temperature_ui(self, temperature):
        # Mettre à jour le texte du label de température
        self.ids.temperature_2.text = f"{temperature}"
















    def update_led_3(self):
        # Créer un thread pour écouter les messages MQTT sans bloquer l'interface
        threading.Thread(target=self.listen_for_led_state, daemon=True).start()


    def listen_for_led_state(self):
        client_1 = MQTT(topic="IUT/led_1")
        client_2 = MQTT(topic="IUT/led_2")

        client_1.connection()
        client_2.connection()

        while True:
            try:
                # Récupérer les messages des deux LEDs
                etat_led_1_get = client_1.get_messages()
                etat_led_2_get = client_2.get_messages()

                print(f"LED 1: {etat_led_1_get}, LED 2: {etat_led_2_get}")  # Debugging

                # Mettre à jour l'UI de manière sûre
                Clock.schedule_once(lambda dt: self.update_led_ui(etat_led_1_get, etat_led_2_get))
                
                # Pause de 1 seconde avant la prochaine vérification
                time.sleep(1)

            except Exception as e:
                print(f"Erreur de connexion MQTT : {str(e)}")
                Clock.schedule_once(lambda dt: self.update_led_ui("Erreur de connexion", "Erreur de connexion"))



    def update_led_ui(self, etat_led_1_get, etat_led_2_get):
        # Mise à jour de l'état de la LED 1
        if etat_led_1_get == "led_1_on":
            self.ids.button_on_1.background_color = vert
            self.ids.button_off_1.background_color = gris
        elif etat_led_1_get == "led_1_off":
            self.ids.button_off_1.background_color = rouge
            self.ids.button_on_1.background_color = gris

        # Mise à jour de l'état de la LED 2
        if etat_led_2_get == "led_2_on":
            self.ids.button_on_2.background_color = vert
            self.ids.button_off_2.background_color = gris
        elif etat_led_2_get == "led_2_off":
            self.ids.button_off_2.background_color = rouge
            self.ids.button_on_2.background_color = gris

        # Mise à jour de l'état de la LED 3 en fonction des états de la LED 1 et de la LED 2
        if etat_led_1_get == "led_1_on" and etat_led_2_get == "led_2_on":
            # Si les deux LEDs sont ON, allume la LED 3
            self.ids.button_on_3.background_color = vert
            self.ids.button_off_3.background_color = gris
        elif etat_led_1_get == "led_1_off" and etat_led_2_get == "led_2_off":
            # Si les deux LEDs sont OFF, éteins la LED 3
            self.ids.button_off_3.background_color = rouge
            self.ids.button_on_3.background_color = gris
        else:
            # Si une seule des deux LEDs est ON, éteins la LED 3
            self.ids.button_on_3.background_color = gris
            self.ids.button_off_3.background_color = gris








    def toggle_on_1(self):
        client = MQTT(topic="IUT/led_1")
        client.connection()
        self.ids.button_on_1.background_color = vert
        self.ids.button_off_1.background_color = gris
        self.ids.good_message.text = "Led 1 activée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_1_on")
        
        # Mettre à jour l'état de la LED 3
        self.update_led_3()


    def toggle_off_1(self):
        client = MQTT(topic="IUT/led_1")
        client.connection()
        self.ids.button_off_1.background_color = rouge
        self.ids.button_on_1.background_color = gris
        self.ids.bad_message.text = "Led 1 désactivée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_1_off")

        # Mettre à jour l'état de la LED 3
        self.update_led_3()


    def toggle_on_2(self):
        client = MQTT(topic="IUT/led_2")
        client.connection()
        self.ids.button_on_2.background_color = vert
        self.ids.button_off_2.background_color = gris
        self.ids.good_message.text = "Led 2 activée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_2_on")

        # Mettre à jour l'état de la LED 3
        self.update_led_3()


    def toggle_off_2(self):
        client = MQTT(topic="IUT/led_2")
        client.connection()
        self.ids.button_off_2.background_color = rouge
        self.ids.button_on_2.background_color = gris
        self.ids.bad_message.text = "Led 2 désactivée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_2_off")

        # Mettre à jour l'état de la LED 3
        self.update_led_3()


    def toggle_on_3(self):
        # Allumer les deux premières LEDs
        self.toggle_on_1()  # Assure-toi de bien allumer la LED 1
        self.toggle_on_2()  # Assure-toi de bien allumer la LED 2

        # Mettre à jour la LED 3
        self.ids.button_on_3.background_color = vert
        self.ids.button_off_3.background_color = gris
        self.ids.good_message.text = "Toutes les LEDs activées !"
        Clock.schedule_once(self.clear_message, 1)


    def toggle_off_3(self):
        # Éteindre les deux premières LEDs
        self.toggle_off_1()  # Assure-toi de bien éteindre la LED 1
        self.toggle_off_2()  # Assure-toi de bien éteindre la LED 2

        # Mettre à jour la LED 3
        self.ids.button_off_3.background_color = rouge
        self.ids.button_on_3.background_color = gris
        self.ids.bad_message.text = "Toutes les LEDs désactivées !"
        Clock.schedule_once(self.clear_message, 1)











    def save_time_schedule(self):

        client = MQTT(client = "horaires")



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
