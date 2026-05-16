from django.db import models
from django.contrib.auth.models import User

class Child(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="children")
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    communication_type = models.CharField(max_length=20, blank=True)
    sensory_sensitivities = models.CharField(max_length=20, blank=True)
    goals = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name