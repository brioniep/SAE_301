import paho.mqtt.client as mqtt

class MQTT():
    def __init__(self, broker= "broker.hivemq.com" , topic = "IUT/SAE3.01/prise"):
        self.__broker = broker
        self.__topics = topic
        self.__client = None
    
# fonction pour subcribe au topic MQTT
    def __on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.__topics)

# fonction pour lire les messages
    def __on_message(self, client, userdata, msg):
        message = msg.payload.decode() # récupere les messages
        print(f"Topic: {self.__topics}\nMessage: {message}\n")

        return message #pour l'utiliser dans d'autre fonction

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

# fonction pour initialiser la connection et creer le client MQTT 
    def connection(self):
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.connect(self.__broker, 1883, 60)
        self.__client.loop_forever()  # utiliser loop_forever() pour démarrer la boucle de réception


#test
if __name__ == "__main__":
    envoyeur = MQTT()
    envoyeur.connection()