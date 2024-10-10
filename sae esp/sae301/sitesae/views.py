from django.shortcuts import render, redirect
from django.http import JsonResponse
from envoi_MQTT import MQTT  # Importer la classe MQTT
from django.contrib import messages
from datetime import datetime, time
from .forms import ScheduleForm 
from .models import Schedule
from django.utils.timezone import make_aware
import threading
from django.shortcuts import get_object_or_404
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

prise_states = {}
# Initialiser les clients MQTT
mqtt_client_temperature = MQTT(topic="IUT/temperature")  # Capteur de température
mqtt_client_led_1 = MQTT(topic="IUT/led_1")  # LED 1
mqtt_client_led_2 = MQTT(topic="IUT/led_2")  # LED 2
mqtt_client_temperature.connection()
mqtt_client_led_1.connection()
mqtt_client_led_2.connection()

def index(request):
    if 'user' not in request.session:
        return redirect('sitesae/login')

    # Récupérer tous les plannings
    schedules = Schedule.objects.all()

    # Récupérer les états des LEDs depuis le client MQTT
    led_1_state = mqtt_client_led_1.get_messages()  # Récupérer l'état de la LED 1
    led_2_state = mqtt_client_led_2.get_messages()  # Récupérer l'état de la LED 2

    # Passer les états des LEDs au template
    context = {
        'schedules': schedules,
        'led_1_state': led_1_state or 'off',  # Si pas de message, afficher "off" par défaut
        'led_2_state': led_2_state or 'off'
    }

    return render(request, 'sitesae/index.html', context)



def is_within_schedule(start, end):
    now = datetime.now().time()  # Obtenir l'heure actuelle
    return start <= now <= end

def get_temperature(request):
    # Plage horaire autorisée (exemple : entre 8h00 et 20h00)
    start_time = time(8, 0)  # 08:00 AM
    end_time = time(20, 0)   # 08:00 PM

    # Vérifier si l'heure actuelle est dans la plage
    if is_within_schedule(start_time, end_time):
        temperature = mqtt_client_temperature.get_messages()  # Récupérer la température
        print("Température reçue :", temperature)  # Debug
        return JsonResponse({'temperature': temperature})
    else:
        return JsonResponse({'temperature': '--', 'error': 'Temperature display is disabled outside of working hours'})

def turn_on(request, prise_id):
    # Envoyer un message MQTT pour allumer une prise
    if prise_id == 1:
        mqtt_client_led_1.envoi("led_1_on")
    elif prise_id == 2:
        mqtt_client_led_2.envoi("led_2_on")
    return redirect('sitesae/index')

def turn_off(request, prise_id):
    # Envoyer un message MQTT pour éteindre une prise
    if prise_id == 1:
        mqtt_client_led_1.envoi("led_1_off")
    elif prise_id == 2:
        mqtt_client_led_2.envoi("led_2_off")
    return redirect('sitesae/index')

def turn_on_all(request):
    # Envoyer un message MQTT pour allumer les deux prises
    mqtt_client_led_1.envoi("led_1_on")
    mqtt_client_led_2.envoi("led_2_on")
    return redirect('sitesae/index')

def turn_off_all(request):
    # Envoyer un message MQTT pour éteindre les deux prises
    mqtt_client_led_1.envoi("led_1_off")
    mqtt_client_led_2.envoi("led_2_off")
    return redirect('sitesae/index')


def schedule(request):
    if request.method == 'POST':
        # Logique pour enregistrer les plages horaires
        pass
    return render(request, 'schedule.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'toto' and password == 'toto':
            request.session['user'] = username
            return redirect('sitesae/index')
        else:
            messages.error(request, "Identifiants incorrects. Veuillez réessayer.")
    
    return render(request, 'sitesae/login.html')

def logout_view(request):
    request.session.flush()  # Supprime toutes les données de session
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('sitesae/login')

def check_schedule():
    import time
    while True:
        current_time = datetime.now().time()
        schedules = Schedule.objects.all()

        for schedule in schedules:
            # Détermine si la prise doit être allumée ou éteinte
            if schedule.start_time <= current_time <= schedule.end_time:
                desired_state = 'on'
            else:
                desired_state = 'off'
            
            # Récupère l'état actuel de la prise (par défaut 'off')
            current_state = prise_states.get(schedule.prise_id, 'off')

            # Si l'état désiré est différent de l'état actuel, envoyer un message MQTT
            if schedule.prise_id == 1:
                if desired_state == 'on':
                    mqtt_client_led_1.envoi(f"led_{schedule.prise_id}_on")  # Envoyer le message correct pour allumer
                else:
                    mqtt_client_led_1.envoi(f"led_{schedule.prise_id}_off")  # Envoyer le message correct pour éteindre
            elif schedule.prise_id == 2:
                if desired_state == 'on':
                    mqtt_client_led_2.envoi(f"led_{schedule.prise_id}_on")  # Envoyer le message correct pour allumer
                else:
                    mqtt_client_led_2.envoi(f"led_{schedule.prise_id}_off")  # Envoyer le message correct pour éteindre
                
                # Mettre à jour l'état actuel de la prise
                prise_states[schedule.prise_id] = desired_state

        # Attendre 5 secondes avant de vérifier à nouveau
        time.sleep(5)

# Créer et démarrer un thread qui exécute la vérification en continu
def start_schedule_checker():
    thread = threading.Thread(target=check_schedule, daemon=True)
    thread.start()

# Appeler cette fonction au démarrage de l'application
start_schedule_checker()

def check_schedule_for_prise(prise_id):
    current_time = make_aware(datetime.now()).time()

    # Vérifier si l'heure actuelle est dans une plage horaire pour la prise donnée
    schedules = Schedule.objects.filter(prise_id=prise_id)
    for schedule in schedules:
        if schedule.start_time <= current_time <= schedule.end_time:
            return True  # Prise doit être allumée

    return False  # En dehors des plages, prise doit être éteinte

def check_schedules_and_control_prises():
    current_time = make_aware(datetime.now()).time()

    for prise_id in [1, 2]:
        schedules = Schedule.objects.filter(prise_id=prise_id)
        is_within_schedule = False
        user_email = None

        for schedule in schedules:
            if schedule.start_time <= current_time <= schedule.end_time:
                is_within_schedule = True
                user_email = schedule.email  # Récupérer l'email associé au planning
                break

        current_state = prise_states.get(prise_id, 'off')  # Récupère l'état actuel de la prise (par défaut 'off')

        # Envoi d'email quand on entre ou sort de la plage horaire
        if is_within_schedule and current_state == 'off':
            send_email(user_email, "Entrée dans la plage horaire", f"La prise {prise_id} est maintenant active.")
        elif not is_within_schedule and current_state == 'on':
            send_email(user_email, "Sortie de la plage horaire", f"La prise {prise_id} est maintenant inactive.")

        # Mise à jour de l'état des prises
        if is_within_schedule:
            mqtt_client_led_1.envoi(f"led_{prise_id}_on")
            mqtt_client_led_2.envoi(f"led_{prise_id}_on")
            prise_states[prise_id] = 'on'
        else:
            mqtt_client_led_1.envoi(f"led_{prise_id}_off")
            mqtt_client_led_2.envoi(f"led_{prise_id}_off")
            prise_states[prise_id] = 'off'



def schedule_view(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new schedule
            return redirect('sitesae/index')
    else:
        form = ScheduleForm()

    schedules = Schedule.objects.all()  # Retrieve all existing schedules
    return render(request, 'sitesae/index.html', {'form': form, 'schedules': schedules})

def enforce_schedules(request):
    check_schedules_and_control_prises()
    return redirect('sitesae/index')

def add_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            email = form.cleaned_data['email']
            schedule.save()

            # Envoi d'un email après création
            subject = "Nouveau planning créé"
            body = f"Un nouveau planning a été créé : \nPrise: {schedule.prise_id}\nDébut: {schedule.start_time}\nFin: {schedule.end_time}"
            send_email(email, subject, body)  # Envoie un email après la création du planning

            messages.success(request, 'Plage horaire ajoutée avec succès !')
            return redirect('sitesae/index')
    else:
        form = ScheduleForm()

    return render(request, 'sitesae/add_schedule.html', {'form': form})

class MQTT():
    def __init__(self, broker="broker.hivemq.com", topic="IUT/led_1"):
        self.__broker = broker
        self.__topics = topic
        self.__client = None
        self.__message = None
    
    # fonction pour subcribe au topic MQTT
    def __on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.__topics)

    # fonction pour lire les messages
    def __on_message(self, client, userdata, msg):
        message = msg.payload.decode()  # récupère les messages
        self.__message = message

    # fonction d'envoi de message via MQTT
    def envoi(self, message):
        if self.__client:
            try:
                self.__client.publish(self.__topics, message)  # envoi du message
                print("Message envoyé")
            except Exception as e:
                print(f"Erreur : message non envoyé, {e}")
        else:
            print("Client non connecté")

    # fonction pour retourner les messages reçus
    def get_messages(self):
        return self.__message  # Simplifier la logique ici

    # fonction pour initialiser la connection et créer le client MQTT 
    def connection(self):
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.connect(self.__broker, 1883, 60)
        self.__client.loop_start()  # utiliser loop_start() pour démarrer la boucle de réception dans un thread séparé

def delete_schedule(request, schedule_id):
    if request.method == 'POST':
        # Récupérer le planning à supprimer
        schedule = get_object_or_404(Schedule, id=schedule_id)
        email = schedule.email  # Récupérer l'email associé au planning
        schedule.delete()

        # Envoi d'un email après suppression
        subject = "Planning supprimé"
        body = f"Le planning pour la prise {schedule.prise_id} a été supprimé."
        send_email(email, subject, body)

        messages.success(request, "Planning supprimé avec succès !")
    return redirect('sitesae/index')

def delete_all_schedules(request):
    if request.method == 'POST':
        # Supprimer tous les plannings
        Schedule.objects.all().delete()
        messages.success(request, "Tous les plannings ont été supprimés avec succès !")
    return redirect('sitesae/index')


def get_led_status(request):
    led_1_state = mqtt_client_led_1.get_messages()  # Récupérer l'état de la LED 1
    led_2_state = mqtt_client_led_2.get_messages()  # Récupérer l'état de la LED 2

    # Retourner les états des LEDs sous forme de JSON
    return JsonResponse({
        'led_1_state': led_1_state or 'off',
        'led_2_state': led_2_state or 'off'
    })


def send_email(to_email, subject, body):
    from_email = "l.petit02400@gmail.com"
    from_password = "dfyh xbiv nxft sqdv"

    # Configuration du serveur SMTP de Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    try:
        # Connexion au compte Gmail
        server.login(from_email, from_password)

        # Création du message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Envoi de l'email
        server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email envoyé avec succès à {to_email}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
    finally:
        server.quit()

