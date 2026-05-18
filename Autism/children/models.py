from django.db import models
from django.contrib.auth.models import User


class Child(models.Model):

    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    class CommunicationChoices(models.TextChoices):
        VERBAL = "verbal", "Verbal"
        NONVERBAL = "nonverbal", "Nonverbal"

    class SensoryChoices(models.TextChoices):
        SOUND = "sound", "Sound"
        TOUCH = "touch", "Touch"
        LIGHT = "light", "Light"
        NONE = "none", "None"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="children"
    )

    name = models.CharField(max_length=100)

    birth_date = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices
    )

    communication_type = models.CharField(
        max_length=20,
        choices=CommunicationChoices.choices
    )

    sensory_sensitivities = models.CharField(
        max_length=20,
        choices=SensoryChoices.choices
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name