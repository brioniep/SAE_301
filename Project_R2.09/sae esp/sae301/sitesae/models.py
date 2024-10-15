from django.db import models
from datetime import datetime

class Schedule(models.Model):
    prise_id = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    email = models.EmailField(default="")
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=False)
    temperature_threshold = models.FloatField(null=True, blank=True)
    

    def is_active(self):
        """Returns True if the current time is within the schedule range."""
        now = datetime.now().time()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"Prise {self.prise_id} de {self.start_time} à {self.end_time}"


