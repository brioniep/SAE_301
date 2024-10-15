import paho.mqtt.client as mqtt
import time

class MQTT():
    def __init__(self, broker="192.168.179.24", topic="test", username="toto", password="toto"):
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


#Version sans le broker privé :
#import paho.mqtt.client as mqtt
# import time

# class MQTT():
#     def __init__(self, broker="broker.hivemq.com", topic="IUT/led_1"):
#         self.__broker = broker
#         self.__topics = topic
#         self.__client = None
#         self.__message = None
    
#     # Fonction pour s'abonner au topic MQTT
#     def __on_connect(self, client, userdata, flags, rc):
#         print(f"Connected with result code {rc}")
#         client.subscribe(self.__topics)

#     # Fonction pour lire les messages
#     def __on_message(self, client, userdata, msg):
#         message = msg.payload.decode()  # Récupère les messages
#         self.__message = message

#     # Fonction d'envoi de message via MQTT
#     def envoi(self, message):
#         if self.__client:
#             try:
#                 self.__client.publish(self.__topics, message)  # Envoi du message
#                 print("Message envoyé")
#             except:
#                 print("Erreur : message non envoyé")
#         else:
#             print("Client non connecté")

#     # Fonction pour retourner les messages reçus
#     def get_messages(self):
#         if self.__message is not None:
#             return self.__message

#     # Fonction pour initialiser la connexion et créer le client MQTT 
#     def connection(self):
#         self.__client = mqtt.Client()
#         self.__client.on_connect = self.__on_connect
#         self.__client.on_message = self.__on_message
#         self.__client.connect(self.__broker, 1883, 60)
#         self.__client.loop_start()  # Utiliser loop_start() pour démarrer la boucle de réception dans un thread séparé

# if __name__ == "__main__":
#     envoyeur = MQTT()
#     envoyeur1 = MQTT(broker="broker.hivemq.com", topic="IUT/led_2")
#     enovyeur2 = MQTT(broker="broker.hivemq.com", topic="IUT/temperature")
#     envoyeur.connection()
#     envoyeur1.connection()
#     enovyeur2.connection()

#     while True:
        
#         print("message reçu (topic 1 led): ", envoyeur.get_messages())
#         print("message reçu (topic 2 led) : ", envoyeur1.get_messages())
#         print("message reçu (topic temperature) : ", enovyeur2.get_messages())
#         time.sleep(1)
        

