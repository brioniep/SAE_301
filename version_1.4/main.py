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
            success_screen.start_update_led()  # Démarrer la mise à jour continue des LEDs
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




















    def __init__(self, **kwargs):
        super(SuccessScreen, self).__init__(**kwargs)
        # Ajout des variables d'état pour LED 1 et LED 2
        self.led_1_state = "off"  # Etat initial de la LED 1
        self.led_2_state = "off"  # Etat initial de la LED 2



    def start_update_led(self):
        # Créer un thread pour écouter les messages MQTT sans bloquer l'interface
        threading.Thread(target=self.listen_for_led, daemon=True).start()

    # Fonction qui tourne en continu dans un thread séparé
    def listen_for_led(self):

        client_1 = MQTT(topic="IUT/led_1")
        client_1.connection()

        client_2 = MQTT(topic="IUT/led_2")
        client_2.connection()   

        while True:
            try:
      
                # Mettre à jour l'UI de manière sûre en utilisant Clock.schedule_once
                
                msg_1 = client_1.get_messages()
                msg_2 = client_2.get_messages()
                led_1_state = "none"
                led_2_state = "none"

                if msg_1 == "led_1_on":
                    self.ids.button_on_1.background_color = vert
                    self.ids.button_off_1.background_color = gris              
                
                elif msg_1 == "led_1_off":
                    self.ids.button_off_1.background_color = rouge
                    self.ids.button_on_1.background_color = gris
                if msg_2 == "led_2_on":     
                    self.ids.button_on_2.background_color = vert
                    self.ids.button_off_2.background_color = gris
                elif msg_2 == "led_2_off":
                    self.ids.button_off_2.background_color = rouge
                    self.ids.button_on_2.background_color = gris

                if msg_1 == "led_1_on" and msg_2 == "led_2_on":
                    self.ids.button_on_3.background_color = vert
                    self.ids.button_off_3.background_color = gris
                elif msg_1 == "led_1_off" and msg_2 == "led_2_off":
                    self.ids.button_off_3.background_color = rouge
                    self.ids.button_on_3.background_color = gris
                else:
                    self.ids.button_on_3.background_color = gris
                    self.ids.button_off_3.background_color = gris


        
                
                time.sleep(1)
                # Afficher la température dans le terminal pour le débogage
                print("led reçue : ", msg_1, msg_2)

            except Exception as e:
                # Afficher un message d'erreur en cas de problème de connexion
                print(f"Erreur de connexion MQTT : {str(e)}")
                Clock.schedule_once(lambda dt: self.update_temperature_ui("Erreur de connexion"))




    # Fonction pour vérifier les états des LEDs 1 et 2 en fonction des messages MQTT
    def update_led_3(self):

        # Vérifie si les deux LEDs sont activées
        if self.led_1_state == "on" and self.led_2_state == "on":
            # Allume la LED 3
            self.ids.button_on_3.background_color = vert
            self.ids.button_off_3.background_color = gris
            self.ids.good_message.text = "Toutes les LEDs activées !"
        # Vérifie si les deux LEDs sont désactivées
        elif self.led_1_state == "off" and self.led_2_state == "off":
            # Éteint la LED 3
            self.ids.button_off_3.background_color = rouge
            self.ids.button_on_3.background_color = gris
            self.ids.bad_message.text = "Toutes les LEDs désactivées !"
        else:
            # Si l'une des deux LEDs est activée et l'autre éteinte, état intermédiaire pour LED 3
            self.ids.button_on_3.background_color = gris
            self.ids.button_off_3.background_color = gris

        Clock.schedule_once(self.clear_message, 1)





    # Fonction toggle pour LED 1 (On)
    def toggle_on_1(self):
        client = MQTT(topic="IUT/led_1")
        client.connection()
        self.ids.button_on_1.background_color = vert
        self.ids.button_off_1.background_color = gris
        self.ids.good_message.text = "Led 1 activée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_1_on")

        # Met à jour l'état de la LED 1
        self.led_1_state = "on"
        
        # Mettre à jour l'état de la LED 3
        self.update_led_3()

    # Fonction toggle pour LED 1 (Off)
    def toggle_off_1(self):
        client = MQTT(topic="IUT/led_1")
        client.connection()
        self.ids.button_off_1.background_color = rouge
        self.ids.button_on_1.background_color = gris
        self.ids.bad_message.text = "Led 1 désactivée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_1_off")

        # Met à jour l'état de la LED 1
        self.led_1_state = "off"
        
        # Mettre à jour l'état de la LED 3
        self.update_led_3()

    # Fonction toggle pour LED 2 (On)
    def toggle_on_2(self):
        client = MQTT(topic="IUT/led_2")
        client.connection()
        self.ids.button_on_2.background_color = vert
        self.ids.button_off_2.background_color = gris
        self.ids.good_message.text = "Led 2 activée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_2_on")

        # Met à jour l'état de la LED 2
        self.led_2_state = "on"
        
        # Mettre à jour l'état de la LED 3
        self.update_led_3()

    # Fonction toggle pour LED 2 (Off)
    def toggle_off_2(self):
        client = MQTT(topic="IUT/led_2")
        client.connection()
        self.ids.button_off_2.background_color = rouge
        self.ids.button_on_2.background_color = gris
        self.ids.bad_message.text = "Led 2 désactivée !"
        Clock.schedule_once(self.clear_message, 1)
        client.envoi(message="led_2_off")

        # Met à jour l'état de la LED 2
        self.led_2_state = "off"
        
        # Mettre à jour l'état de la LED 3
        self.update_led_3()

    # Fonction toggle pour LED 3 (On)
    def toggle_on_3(self):
        # Si l'utilisateur veut allumer la LED 3 manuellement, on allume les deux premières LEDs
        self.toggle_on_1()
        self.toggle_on_2()

    # Fonction toggle pour LED 3 (Off)
    def toggle_off_3(self):
        # Si l'utilisateur veut éteindre la LED 3 manuellement, on éteint les deux premières LEDs
        self.toggle_off_1()
        self.toggle_off_2()






























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
