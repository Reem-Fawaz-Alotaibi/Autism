from django.db import models
import random
from django.contrib.auth.models import User

# Create your models here.

class AutismSupportPlace(models.Model):

    PLACE_TYPES = [
        ('government', 'حكومي'),
        ('private', 'خاص'),
        ('community', 'مجتمعي'),
    ]

    REGIONS = [
        ('riyadh', 'منطقة الرياض'),
        ('eastern', 'المنطقة الشرقية'),
        ('makkah', 'منطقة مكة المكرمة'),
        ('madinah', 'منطقة المدينة المنورة'),
        ('asir', 'منطقة عسير'),
        ('jazan', 'جازان'),
        ('najran', 'نجران'),
        ('qassim', 'القصيم'),
        ('hail', 'حائل'),
        ('tabuk', 'تبوك'),
        ('jouf', 'الجوف'),
        ('northern_borders', 'الحدود الشمالية'),
        ('bahah', 'الباحة'),
    ]

    REGION_POSITIONS = {

        'riyadh': {
            'x_min': 20,
            'x_max': 60,
            'y_min': 65,
            'y_max': 75,
        },

        'eastern': {
            'x_min': 68,
            'x_max': 82,
            'y_min': 45,
            'y_max': 62,
        },

        'makkah': {
            'x_min': 28,
            'x_max': 42,
            'y_min': 58,
            'y_max': 78,
        },

        'madinah': {
            'x_min': 30,
            'x_max': 42,
            'y_min': 42,
            'y_max': 58,
        },

        'asir': {
            'x_min': 35,
            'x_max': 48,
            'y_min': 78,
            'y_max': 92,
        },

        'jazan': {
            'x_min': 28,
            'x_max': 38,
            'y_min': 88,
            'y_max': 98,
        },

        'najran': {
            'x_min': 50,
            'x_max': 62,
            'y_min': 82,
            'y_max': 95,
        },

        'qassim': {
            'x_min': 42,
            'x_max': 54,
            'y_min': 40,
            'y_max': 52,
        },

        'hail': {
            'x_min': 38,
            'x_max': 50,
            'y_min': 28,
            'y_max': 42,
        },

        'tabuk': {
            'x_min': 20,
            'x_max': 35,
            'y_min': 15,
            'y_max': 32,
        },

        'jouf': {
            'x_min': 10,
            'x_max': 26,
            'y_min': 17,
            'y_max': 26,
        },

        'northern_borders': {
            'x_min': 50,
            'x_max': 68,
            'y_min': 10,
            'y_max': 28,
        },

        'bahah': {
            'x_min': 34,
            'x_max': 44,
            'y_min': 72,
            'y_max': 82,
        },
    }


    name = models.CharField(max_length=200)
    description = models.TextField()
    region = models.CharField(max_length=50,choices=REGIONS)
    address = models.TextField()
    phone_number = models.CharField(max_length=10)
    website = models.URLField(blank=True, null=True)
    place_type = models.CharField(max_length=20,choices=PLACE_TYPES)
    x_position = models.FloatField(blank=True, null=True)
    y_position = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):

        if not self.x_position and not self.y_position:
            if self.region in self.REGION_POSITIONS:
                region_data = self.REGION_POSITIONS[self.region]
                self.x_position = random.uniform(
                    region_data['x_min'],
                    region_data['x_max']
                )

                self.y_position = random.uniform(
                    region_data['y_min'],
                    region_data['y_max']
                )

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


class PlaceLike(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    place = models.ForeignKey(AutismSupportPlace,on_delete=models.CASCADE,related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'place']