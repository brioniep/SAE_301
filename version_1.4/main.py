from datetime import datetime, time
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock

class LoginScreen(Screen):
    def on_login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if username == "" and password == "":            
            self.resetForm()
            self.resetLabel()
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = 'success'
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_on = False

    def on_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'login'

    def toggle_on(self):
        self.ids.button_on.background_color = [0, 1, 0, 1]
        self.ids.button_off.background_color = [1, 0.5, 0.5, 1]
        self.is_on = True
        self.ids.good_message.text = "Leds activées !"
        Clock.schedule_once(self.clear_message, 1)

    def toggle_off(self):
        self.ids.button_off.background_color = [1, 0, 0, 1]
        self.ids.button_on.background_color = [0.5, 1, 0.5, 1]
        self.is_on = False
        self.ids.bad_message.text = "Leds désactivées !"
        Clock.schedule_once(self.clear_message, 1)

    def save_time_schedule(self):
        start_hour1 = int(self.ids.start_hour.text)
        start_minute1 = int(self.ids.start_minute.text)
        end_hour1 = int(self.ids.end_hour.text)
        end_minute1 = int(self.ids.end_minute.text)

        start_hour2 = int(self.ids.start_hour2.text)
        start_minute2 = int(self.ids.start_minute2.text)
        end_hour2 = int(self.ids.end_hour2.text)
        end_minute2 = int(self.ids.end_minute2.text)

        current_date = datetime.now().date()

        start_time1 = datetime.combine(current_date, time(start_hour1, start_minute1))
        end_time1 = datetime.combine(current_date, time(end_hour1, end_minute1))
        start_time2 = datetime.combine(current_date, time(start_hour2, start_minute2))
        end_time2 = datetime.combine(current_date, time(end_hour2, end_minute2))

        start_timestamp1 = int(start_time1.timestamp())
        end_timestamp1 = int(end_time1.timestamp())
        start_timestamp2 = int(start_time2.timestamp())
        end_timestamp2 = int(end_time2.timestamp())

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
