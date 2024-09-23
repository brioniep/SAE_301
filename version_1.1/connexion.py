from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

class LoginScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [50, 100]  # Espacement autour
        self.spacing = 20  # Espace entre les widgets




        # Titre de la page "Login"
        self.add_widget(Label(text="Login", font_size=70, size_hint_y=None, height=30))

        # Champ de texte pour le nom d'utilisateur
        self.add_widget(Label(text="Nom d'utilisateur:"))
        self.username_input = TextInput(multiline=False)
        self.add_widget(self.username_input)

        # Champ de texte pour le mot de passe
        self.add_widget(Label(text="Mot de passe:"))
        self.password_input = TextInput(password=True, multiline=False)
        self.add_widget(self.password_input)

        # Bouton de connexion
        self.login_button = Button(text="Se connecter", size_hint_y=None, height=50)
        self.login_button.bind(on_press=self.verify_credentials)
        self.add_widget(self.login_button)

    def verify_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username == "admin" and password == "1234":
            self.show_popup("Succès", "Connexion réussie !")
        else:
            self.show_popup("Erreur", "Identifiants incorrects.")

    def show_popup(self, title, message):
        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(Label(text=message))
        close_button = Button(text="Fermer", size_hint_y=None, height=40)
        popup_content.add_widget(close_button)
        
        popup = Popup(title=title, content=popup_content, size_hint=(0.6, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()


class LoginApp(App):
    def build(self):
        return LoginScreen()


if __name__ == '__main__':
    LoginApp().run()
