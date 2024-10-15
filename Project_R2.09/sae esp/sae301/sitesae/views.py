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
from twilio.rest import Client


# Tmpérature : IUT/température 

# Leds : IUT/on/off/led_1    ( ou _2)

# États des LEDs : IUT/etat/led_1    ( ou _2)

prise_states = {}
# Initialiser les clients MQTT
mqtt_client_temperature = MQTT(topic="IUT/temperature")  # Capteur de température
mqtt_client_led_1 = MQTT(topic="IUT/on/off/led_1")  # LED 1 on/off
mqtt_client_led_2 = MQTT(topic="IUT/on/off/led_2")  # LED 2 on/off
mqtt_client_led_1_état = MQTT(topic="IUT/etat/led_1")  # LED 1 etat
mqtt_client_led_2_état = MQTT(topic="IUT/etat/led_2")  # LED 2 etat
mqtt_client_temperature.connection()
mqtt_client_led_1.connection()
mqtt_client_led_2.connection()
mqtt_client_led_1_état.connection()
mqtt_client_led_2_état.connection()

TWILIO_SID = ('AC0c11fe84fa3f524ec942de5b2babc2e4')
TWILIO_AUTH_TOKEN = ('75bacabdb073bf974ee3dc45cb28bbd1')
TWILIO_PHONE_NUMBER = ('+13344024583')


def send_sms(to_phone, body):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        print(f"SMS envoyé avec succès à {to_phone}")
    except Exception as e:
        print(f"Erreur lors de l'envoi du SMS : {e}")

def index(request):
    if 'user' not in request.session:
        return redirect('sitesae/login')

    # Récupérer tous les plannings
    schedules = Schedule.objects.all()

    # Récupérer les états des LEDs depuis le client MQTT
    led_1_state = mqtt_client_led_1_état.get_messages()  # Récupérer l'état de la LED 1
    led_2_state = mqtt_client_led_2_état.get_messages()  # Récupérer l'état de la LED 2

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
        mqtt_client_led_1_état.envoi("led_1_on")
    elif prise_id == 2:
        mqtt_client_led_2.envoi("led_2_on")
        mqtt_client_led_2_état.envoi("led_2_on")
    return redirect('sitesae/index')

def turn_off(request, prise_id):
    # Envoyer un message MQTT pour éteindre une prise
    if prise_id == 1:
        mqtt_client_led_1.envoi("led_1_off")
        mqtt_client_led_1_état.envoi("led_1_off")
    elif prise_id == 2:
        mqtt_client_led_2.envoi("led_2_off")
        mqtt_client_led_2_état.envoi("led_2_off")
    return redirect('sitesae/index')

def turn_on_all(request):
    # Envoyer un message MQTT pour allumer les deux prises
    mqtt_client_led_1.envoi("led_1_on")
    mqtt_client_led_2.envoi("led_2_on")
    mqtt_client_led_1_état.envoi("led_1_on")
    mqtt_client_led_2_état.envoi("led_2_on")
    return redirect('sitesae/index')

def turn_off_all(request):
    # Envoyer un message MQTT pour éteindre les deux prises
    mqtt_client_led_1.envoi("led_1_off")
    mqtt_client_led_2.envoi("led_2_off")
    mqtt_client_led_1_état.envoi("led_1_off")
    mqtt_client_led_2_état.envoi("led_2_off")
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
        user_phone = None
        temperature_threshold = 0

        for schedule in schedules:
            if schedule.start_time <= current_time <= schedule.end_time:
                is_within_schedule = True
                user_email = schedule.email
                user_phone = schedule.phone
                temperature_threshold = schedule.temperature_threshold  
                break

        current_state = prise_states.get(prise_id, 'off')

        
        current_temperature = float(mqtt_client_temperature.get_messages()) 

        
        if current_temperature > temperature_threshold:
            subject = f"Alerte : Température dépassée pour la prise {prise_id}"
            body = f"La température actuelle est de {current_temperature}°C, dépassant le seuil de {temperature_threshold}°C."
            send_email(user_email, subject, body, to_phone=user_phone)

        # Logique d'allumage/éteignage des prises
        if is_within_schedule and current_state == 'off':
            mqtt_client_led_1.envoi(f"led_{prise_id}_on")
            mqtt_client_led_2.envoi(f"led_{prise_id}_on")
            prise_states[prise_id] = 'on'
        elif not is_within_schedule and current_state == 'on':
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
            email = form.cleaned_data['email']  # Email de l'utilisateur
            phone = form.cleaned_data.get('phone')  # Téléphone de l'utilisateur, s'il est présent
            schedule.save()

            
            subject = "Nouveau planning créé"
            body = f"Un nouveau planning a été créé pour la prise {schedule.prise_id}, de {schedule.start_time} à {schedule.end_time}."
            send_email(email, subject, body, to_phone=phone)  # Envoi d'email et SMS si le téléphone est fourni

            messages.success(request, 'Plage horaire ajoutée avec succès !')
            return redirect('sitesae/index')
    else:
        form = ScheduleForm()

    return render(request, 'sitesae/add_schedule.html', {'form': form})



def delete_schedule(request, schedule_id):
    if request.method == 'POST':
        # Récupérer le planning à supprimer
        schedule = get_object_or_404(Schedule, id=schedule_id)
        email = schedule.email  # Email associé au planning
        phone = schedule.phone  # Numéro de téléphone associé, s'il existe
        schedule.delete()

        # Envoyer la notification après suppression
        subject = "Planning supprimé"
        body = f"Le planning pour la prise {schedule.prise_id} a été supprimé."
        send_email(email, subject, body, to_phone=phone)

        messages.success(request, "Planning supprimé avec succès !")
    return redirect('sitesae/index')


def delete_all_schedules(request):
    if request.method == 'POST':
        # Supprimer tous les plannings
        Schedule.objects.all().delete()
        messages.success(request, "Tous les plannings ont été supprimés avec succès !")
    return redirect('sitesae/index')


def get_led_status(request):
    # Récupérer les états des LEDs depuis le client MQTT
    led_1_state = mqtt_client_led_1_état.get_messages()  # Récupérer l'état de la LED 1
    led_2_state = mqtt_client_led_2_état.get_messages()  # Récupérer l'état de la LED 2
    

    # Retourner les états des LEDs sous forme de JSON
    return JsonResponse({
        'led_1_state': led_1_state or 'off',
        'led_2_state': led_2_state or 'off'
    })


# def send_email(to_email, subject, body, to_phone=None):
#     from_email = "l.petit02400@gmail.com"
#     from_password = "dfyh xbiv nxft sqdv"
    
#     # Configuration du serveur SMTP de Gmail
#     server = smtplib.SMTP('smtp.gmail.com', 587) #587 for TLS
#     server.starttls()
    
#     try:
#         # Connexion au compte Gmail
#         server.login(from_email, from_password)

#         # Création du message
#         msg = MIMEMultipart()
#         msg['From'] = from_email
#         msg['To'] = to_email
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'plain'))

#         # Envoi de l'email
#         server.sendmail(from_email, to_email, msg.as_string())
#         print(f"Email envoyé avec succès à {to_email}")
#         if to_phone:
#             send_sms(to_phone, body)
#     except Exception as e:
#         print(f"Erreur lors de l'envoi de l'email: {e}")
#     finally:
#         server.quit()
def send_email(to_email, subject, body, to_phone=None):
    from_email = "l.petit02400@gmail.com"
    from_password = "dfyh xbiv nxft sqdv"
    
    # Configuration du serveur SMTP de Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)  # Port 587 pour TLS
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

        # Envoi d'un SMS si le numéro de téléphone est fourni
        if to_phone:
            send_sms(to_phone, body)
    
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
    
    finally:
        server.quit()
