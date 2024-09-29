# MQTT Client Script

Ce script fournit une classe MQTT qui permet de se connecter à un serveur MQTT, de s'abonner à un topic et d'envoyer des messages.

## Importation

Pour utiliser ce script dans un autre script, vous devez l'importer en ajoutant la ligne suivante au début de votre script :

```python
from mqtt_client import MQTT
```

## Création d'un objet MQTT

Créez un objet MQTT en appelant le constructeur :

```python
envoyeur = MQTT()
```

## Méthodes

L'objet MQTT propose les méthodes suivantes :

* `connection()`: établit la connexion au serveur MQTT
* `envoi(message)`: envoie un message au topic abonné

## Exemple d'utilisation

```python
from mqtt_client import MQTT

envoyeur = MQTT()
envoyeur.connection()
envoyeur.envoi("Bonjour, ceci est un message de test")
```

## Paramètres

* `broker`: le nom du serveur MQTT (par défaut : `broker.hivemq.com`)
* `topics`: le nom du topic à abonner (par défaut : `IUT/SAE3.01/prise`)

## Remarques

* Assurez-vous d'avoir installé la bibliothèque Paho-MQTT pour utiliser ce script.
* Le script utilise la méthode `loop_forever()` pour démarrer la boucle de réception, ce qui signifie que le script va rester en attente de messages jusqu'à ce que vous l'arrêtiez manuellement.

![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)


