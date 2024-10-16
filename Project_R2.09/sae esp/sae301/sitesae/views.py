from django.shortcuts import render, redirect
from django.http import JsonResponse
from envoi_MQTT import MQTT  # la classe est dans le fichier envoi_MQTT.py
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


prise_states = {} # état actuel des prises dans la fonction check_schedule
mqtt_client_temperature = MQTT(topic="IUT/temperature")  # capteur de température
mqtt_client_led_1 = MQTT(topic="IUT/on/off/led_1")  # led 1 on/off
mqtt_client_led_2 = MQTT(topic="IUT/on/off/led_2")  # led 2 on/off
mqtt_client_led_1_état = MQTT(topic="IUT/etat/led_1")  # led 1 etat
mqtt_client_led_2_état = MQTT(topic="IUT/etat/led_2")  # led 2 etat
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

    schedules = Schedule.objects.all()
    led_1_state = mqtt_client_led_1_état.get_messages()  
    led_2_state = mqtt_client_led_2_état.get_messages()  

    # passer les états des LEDs au template
    context = {
        'schedules': schedules,
        'led_1_state': led_1_state or 'off',  # si pas de message, afficher "off" par défaut
        'led_2_state': led_2_state or 'off'
    }

    return render(request, 'sitesae/index.html', context)


# verifier si l'heure actuelle est dans la plage horaire
def is_within_schedule(start, end):
    now = datetime.now().time()  # obtenir l'heure actuelle
    return start <= now <= end

#  recupérer la température
def get_temperature(request):
    start_time = time(8, 0) # heure de début de la plage horaire par défaut  
    end_time = time(20, 0)   

    # Vérifier si l'heure actuelle est dans la plage
    if is_within_schedule(start_time, end_time):
        temperature = mqtt_client_temperature.get_messages()  # recup la température
        print("Température reçue :", temperature)  # Debug
        return JsonResponse({'temperature': temperature})
    else:
        return JsonResponse({'temperature': '--', 'error': 'Temperature display is disabled outside of working hours'}) # en json pour l'affichage (le traitement est fait en js)


# envois des messages de base pour allumer et éteindre les prises
def turn_on(request, prise_id):
    if prise_id == 1:
        mqtt_client_led_1.envoi("led_1_on")
        mqtt_client_led_1_état.envoi("led_1_on")
    elif prise_id == 2:
        mqtt_client_led_2.envoi("led_2_on")
        mqtt_client_led_2_état.envoi("led_2_on")
    return redirect('sitesae/index')

def turn_off(request, prise_id):
    if prise_id == 1:
        mqtt_client_led_1.envoi("led_1_off")
        mqtt_client_led_1_état.envoi("led_1_off")
    elif prise_id == 2:
        mqtt_client_led_2.envoi("led_2_off")
        mqtt_client_led_2_état.envoi("led_2_off")
    return redirect('sitesae/index')

def turn_on_all(request):
    mqtt_client_led_1.envoi("led_1_on")
    mqtt_client_led_2.envoi("led_2_on")
    mqtt_client_led_1_état.envoi("led_1_on")
    mqtt_client_led_2_état.envoi("led_2_on")
    return redirect('sitesae/index')

def turn_off_all(request):
    mqtt_client_led_1.envoi("led_1_off")
    mqtt_client_led_2.envoi("led_2_off")
    mqtt_client_led_1_état.envoi("led_1_off")
    mqtt_client_led_2_état.envoi("led_2_off")
    return redirect('sitesae/index')

# afficher les plages horaires
def schedule(request):
    if request.method == 'POST':
        pass # envoyer les données au formulaire
    return render(request, 'schedule.html')

# connexion de l'utilisateur
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

# deconnexion de l'utilisateur
def logout_view(request):
    request.session.flush()  # supprime toutes les données de session
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('sitesae/login')

# vérifier les plannings en arrière-plan et controle les prises
def check_schedule():
    import time
    while True:
        current_time = datetime.now().time()
        schedules = Schedule.objects.all()

        for schedule in schedules:
            # vérifier si l'heure actuelle est dans une plage horaire pour la prise donnée
            if schedule.start_time <= current_time <= schedule.end_time:
                desired_state = 'on'
            else:
                desired_state = 'off'
            
            # l'état actuel de la prise 
            current_state = prise_states.get(schedule.prise_id, 'off')
            
            # vérifier si l'état actuel est différent de l'état souhaité
            if schedule.prise_id == 1:
                if desired_state == 'on':
                    mqtt_client_led_1.envoi(f"led_{schedule.prise_id}_on")  
                else:
                    mqtt_client_led_1.envoi(f"led_{schedule.prise_id}_off")  
            elif schedule.prise_id == 2:
                if desired_state == 'on':
                    mqtt_client_led_2.envoi(f"led_{schedule.prise_id}_on")  
                else:
                    mqtt_client_led_2.envoi(f"led_{schedule.prise_id}_off")  
                
                prise_states[schedule.prise_id] = desired_state # mettre à jour l'état de la prise

        time.sleep(5)

# demarer un processus en arrière-plan pour vérifier les plannings
def start_schedule_checker():
    thread = threading.Thread(target=check_schedule, daemon=True)
    thread.start()

# appeler cette fonction au démarrage de l'application
start_schedule_checker()

# vérifier si une prise doit être allumée ou éteinte
def check_schedule_for_prise(prise_id):
    current_time = make_aware(datetime.now()).time()

    # vérifier si l'heure actuelle est dans une plage horaire pour la prise donnée
    schedules = Schedule.objects.filter(prise_id=prise_id)
    for schedule in schedules:
        if schedule.start_time <= current_time <= schedule.end_time:
            return True  # la prise doit être allumée

    return False  # en dehors des plages la prise doit être éteinte

# logique de vérification des plannings et contrôle des prises, envoi de notifications si nécessaire
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

    # seuil de température + envoi mail et sms quand dépassé
        if current_temperature > temperature_threshold:
            subject = f"Alerte : Température dépassée pour la prise {prise_id}"
            body = f"La température actuelle est de {current_temperature}°C, dépassant le seuil de {temperature_threshold}°C."
            send_email(user_email, subject, body, to_phone=user_phone)

        # logique dallumage/éteignage des prises
        if is_within_schedule and current_state == 'off':
            mqtt_client_led_1.envoi(f"led_{prise_id}_on")
            mqtt_client_led_2.envoi(f"led_{prise_id}_on")
            prise_states[prise_id] = 'on'
        elif not is_within_schedule and current_state == 'on':
            mqtt_client_led_1.envoi(f"led_{prise_id}_off")
            mqtt_client_led_2.envoi(f"led_{prise_id}_off")
            prise_states[prise_id] = 'off'



# pour afficher les plannings
def schedule_view(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('sitesae/index')
    else:
        form = ScheduleForm() # pour afficher le formulaire vide

    schedules = Schedule.objects.all()  
    return render(request, 'sitesae/index.html', {'form': form, 'schedules': schedules})

# La fonction est plus utilisée mais j'avais la flemme de re changer
def enforce_schedules(request):
    check_schedules_and_control_prises()
    
    return redirect('sitesae/index')


# ajout de planning et envoi de notification
def add_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            email = form.cleaned_data['email']  
            phone = form.cleaned_data.get('phone')  
            schedule.save()

            
            subject = "Nouveau planning créé"
            body = f"Un nouveau planning a été créé pour la prise {schedule.prise_id}, de {schedule.start_time} à {schedule.end_time}."
            send_email(email, subject, body, to_phone=phone)  

            messages.success(request, 'Plage horaire ajoutée avec succès !')
            return redirect('sitesae/index')
    else:
        form = ScheduleForm()

    return render(request, 'sitesae/add_schedule.html', {'form': form})



def delete_schedule(request, schedule_id):
    if request.method == 'POST':
        # Récupérer le planning à supprimer
        schedule = get_object_or_404(Schedule, id=schedule_id)
        email = schedule.email  
        phone = schedule.phone  
        schedule.delete()

        # envoyer la notification après suppression
        subject = "Planning supprimé"
        body = f"Le planning pour la prise {schedule.prise_id} a été supprimé."
        send_email(email, subject, body, to_phone=phone) # envoi d'email et SMS si numéro fourni

        messages.success(request, "Planning supprimé avec succès !")
    return redirect('sitesae/index')


def delete_all_schedules(request):
    if request.method == 'POST':
        # supprimer tous les plannings
        Schedule.objects.all().delete()
        messages.success(request, "Tous les plannings ont été supprimés avec succès !") 
    return redirect('sitesae/index')


def get_led_status(request):
    led_1_state = mqtt_client_led_1_état.get_messages()  
    led_2_state = mqtt_client_led_2_état.get_messages()  

    # Retourner les états des LEDs sous forme de JSON pour l'affichage
    return JsonResponse({
        'led_1_state': led_1_state or 'off',
        'led_2_state': led_2_state or 'off'
    })

def send_email(to_email, subject, body, to_phone=None):
    from_email = "l.petit02400@gmail.com"
    from_password = "dfyh xbiv nxft sqdv"
    
    server = smtplib.SMTP('smtp.gmail.com', 587)  
    server.starttls()
    
    try:
        # Connexion
        server.login(from_email, from_password)

        # Création 
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Envoi 
        server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email envoyé avec succès à {to_email}")

        # Envoi d'un SMS si numéro fourni
        if to_phone:
            send_sms(to_phone, body)
    
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
    
    finally:
        server.quit()
