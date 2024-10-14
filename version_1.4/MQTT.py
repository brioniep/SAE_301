import paho.mqtt.client as mqtt
import time

class MQTT():
    def __init__(self, broker="broker.hivemq.com", topic="IUT/SAE3.01/prise", username=None, password=None):
        self.__broker = broker
        self.__topics = topic
        self.__username = username
        self.__password = password
        self.__client = None
        self.__message = "None"
    
    # fonction pour subcribe au topic MQTT
    def __on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.__topics)

    # fonction pour lire les messages
    def __on_message(self, client, userdata, msg):
        message = msg.payload.decode() # récupere les messages
        self.__message = message

    # fonction d'envoi de message via MQTT
    def envoi(self, message):
        if self.__client:
            try:
                self.__client.publish(self.__topics, message) # envoi du message
                print("message envoyé")
            except:
                print("erreur : message non envoyé")
        else:
            print("Client non connecté")

    # fonction pour retourner les messages reçus
    def get_messages(self):
        if self.__message is not None:
            return self.__message
    
    # fonction pour initialiser la connection et creer le client MQTT 
    def connection(self):
        self.__client = mqtt.Client()
        if self.__username and self.__password:
            self.__client.username_pw_set(self.__username, self.__password)
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.connect(self.__broker, 1883, 60)
        self.__client.loop_start()  # utiliser loop_start() pour démarrer la boucle de réception dans un thread séparé

#test
if __name__ == "__main__":
    envoyeur = MQTT(broker="192.168.1.75",topic="test", username="toto", password="toto")
    envoyeur.connection()

    while True:
        print("message reçu : ", envoyeur.get_messages())
        envoyeur.envoi("Hello")
        time.sleep(1)