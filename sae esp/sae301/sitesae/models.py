from django.db import models
from datetime import datetime

class Schedule(models.Model):
    start_time = models.TimeField()  # Heure de début
    end_time = models.TimeField()  # Heure de fin
    prise_id = models.IntegerField()  # ID de la prise
    email = models.EmailField(default="")  # Adresse email
    phone = models.CharField(max_length=15, blank=True, default="")
    

    def is_active(self):
        """Returns True if the current time is within the schedule range."""
        now = datetime.now().time()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"Prise {self.prise_id} de {self.start_time} à {self.end_time}"


