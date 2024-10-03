from django.db import models

class Schedule(models.Model):
    start_time = models.TimeField()  # Heure de début
    end_time = models.TimeField()  # Heure de fin
    prise_id = models.IntegerField()  # ID de la prise

    def __str__(self):
        return f"Prise {self.prise_id} de {self.start_time} à {self.end_time}"
