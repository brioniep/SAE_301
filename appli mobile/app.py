import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# La version minimale de Kivy requise
kivy.require('2.0.0')

class MyApp(App):
    def build(self):
        # Créer un layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Ajouter un champ de texte
        self.input = TextInput(hint_text="Entrez votre texte ici", multiline=False)
        layout.add_widget(self.input)

        # Ajouter un label
        self.label = Label(text="Appuyez sur le bouton pour voir le message")
        layout.add_widget(self.label)

        # Ajouter un bouton avec une action de clic
        btn = Button(text="Cliquez-moi")
        btn.bind(on_press=self.on_button_press)
        layout.add_widget(btn)

        return layout

    def on_button_press(self, instance):
        # Mettre à jour le label avec le texte du champ de saisie
        self.label.text = f"Bonjour, {self.input.text}!"

# Lancer l'application
if __name__ == '__main__':
    MyApp().run()
