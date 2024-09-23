from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class MyApp(App):
    def build(self):
        # Création du layout principal (BoxLayout)
        layout = BoxLayout(orientation='vertical')

        # Création d'un label
        self.label = Label(text="Bienvenue dans Kivy !")
        layout.add_widget(self.label)

        # Création d'un bouton
        button = Button(text="Cliquez-moi")
        button.bind(on_press=self.on_button_click)  # Liaison du bouton à la méthode on_button_click
        layout.add_widget(button)

        return layout

    def on_button_click(self, instance):
        # Action effectuée lors du clic sur le bouton
        self.label.text = "Bouton cliqué !"

# Lancement de l'application
if __name__ == '__main__':
    MyApp().run()
