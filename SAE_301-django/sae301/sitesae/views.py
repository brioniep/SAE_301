from django.shortcuts import render, redirect
from django.http import JsonResponse
from envoi_MQTT import MQTT  # Importer la classe MQTT que vous avez définie
from django.contrib import messages

# Initialiser le client MQTT
mqtt_client = MQTT()
mqtt_client.connection()

def index(request):
    return render(request, 'index.html')

def get_temperature(request):
    # Récupérer les messages (température) depuis MQTT
    temperature = mqtt_client.get_messages()
    return JsonResponse({'temperature': temperature})

def turn_on(request, prise_id):
    # Envoyer un message MQTT pour allumer une prise
    mqtt_client.envoi(f"turn_on_{prise_id}")
    return redirect('index')

def turn_off(request, prise_id):
    # Envoyer un message MQTT pour éteindre une prise
    mqtt_client.envoi(f"turn_off_{prise_id}")
    return redirect('index')

def turn_on_all(request):
    # Envoyer un message MQTT pour allumer les deux prises
    mqtt_client.envoi("turn_on_all")
    return redirect('index')

def turn_off_all(request):
    # Envoyer un message MQTT pour éteindre les deux prises
    mqtt_client.envoi("turn_off_all")
    return redirect('index')

def schedule(request):
    if request.method == 'POST':
        # Logique pour enregistrer les plages horaires
        pass
    return render(request, 'schedule.html')


# def turn_on(request, prise_id):
#     mqtt_client.envoi(f"turn_on_{prise_id}")
#     messages.success(request, f"Prise {prise_id} allumée")
#     return redirect('index')

# def turn_off(request, prise_id):
#     mqtt_client.envoi(f"turn_off_{prise_id}")
#     messages.success(request, f"Prise {prise_id} éteinte")
#     return redirect('index')

# def turn_on_all(request):
#     mqtt_client.envoi("turn_on_all")
#     messages.success(request, "Les deux prises sont allumées")
#     return redirect('index')

# def turn_off_all(request):
#     mqtt_client.envoi("turn_off_all")
#     messages.success(request, "Les deux prises sont éteintes")
#     return redirect('index')
