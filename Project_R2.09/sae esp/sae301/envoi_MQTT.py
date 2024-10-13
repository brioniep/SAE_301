import paho.mqtt.client as mqtt
import time

class MQTT():
    def __init__(self, broker="broker.hivemq.com", topic="IUT/on/off/led_1"):
        self.__broker = broker
        self.__topics = topic
        self.__client = None
        self.__message = None
    
    # Fonction pour s'abonner au topic MQTT
    def __on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.__topics)

    # Fonction pour lire les messages
    def __on_message(self, client, userdata, msg):
        message = msg.payload.decode()  # Récupère les messages
        self.__message = message

    # Fonction d'envoi de message via MQTT
    def envoi(self, message):
        if self.__client:
            try:
                self.__client.publish(self.__topics, message)  # Envoi du message
                print("Message envoyé")
            except:
                print("Erreur : message non envoyé")
        else:
            print("Client non connecté")

    # Fonction pour retourner les messages reçus
    def get_messages(self):
        if self.__message is not None:
            return self.__message

    # Fonction pour initialiser la connexion et créer le client MQTT 
    def connection(self):
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.connect(self.__broker, 1883, 60)
        self.__client.loop_start()  # Utiliser loop_start() pour démarrer la boucle de réception dans un thread séparé

if __name__ == "__main__":
    led_1_envois = MQTT()
    led_2_envois = MQTT(broker="broker.hivemq.com", topic="IUT/on/off/led_2")
    led_1_etat = MQTT(broker="broker.hivemq.com", topic="IUT/etat/led_1")
    led_2_etat = MQTT(broker="broker.hivemq.com", topic="IUT/etat/led_2")
    temperature = MQTT(broker="broker.hivemq.com", topic="IUT/temperature")
    led_1_envois.connection()
    led_2_envois.connection()
    led_1_etat.connection()
    led_2_etat.connection()
    temperature.connection()


    while True:
        
        print("message reçu (topic 1 led envoi): ", led_1_envois.get_messages())
        print("message reçu (topic 2 led envoi) : ", led_2_envois.get_messages())
        print("message reçu (topic 1 led etat) : ", led_1_etat.get_messages())
        print("message reçu (topic 2 led etat) : ", led_2_etat.get_messages())
        print("message reçu (topic temperature) : ", temperature.get_messages())
        time.sleep(1)
