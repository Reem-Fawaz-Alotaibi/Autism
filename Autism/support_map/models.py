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
            'x_min': 47,
            'x_max': 62,
            'y_min': 42,
            'y_max': 71,
        },

        'eastern': {
            'x_min': 63,
            'x_max': 75,
            'y_min': 39,
            'y_max': 75,
        },

        'makkah': {
            'x_min': 22,
            'x_max': 40,
            'y_min': 57,
            'y_max': 65,
        },

        'madinah': {
            'x_min': 21,
            'x_max': 33,
            'y_min': 43,
            'y_max': 56,
        },

        'asir': {
            'x_min': 35,
            'x_max': 43,
            'y_min': 70,
            'y_max': 78,
        },

        'jazan': {
            'x_min': 37,
            'x_max': 41,
            'y_min': 80,
            'y_max': 86,
        },

        'najran': {
            'x_min': 44,
            'x_max': 60,
            'y_min': 73,
            'y_max': 82,
        },

        'qassim': {
            'x_min': 34,
            'x_max': 44,
            'y_min': 39,
            'y_max': 43,
        },

        'hail': {
            'x_min': 27,
            'x_max': 43,
            'y_min': 28,
            'y_max': 38,
        },

        'tabuk': {
            'x_min': 8,
            'x_max': 12,
            'y_min': 30,
            'y_max': 35,
        },

        'jouf': {
            'x_min': 15,
            'x_max': 30,
            'y_min': 17,
            'y_max': 26,
        },

        'northern_borders': {
            'x_min': 40,
            'x_max': 50,
            'y_min': 25,
            'y_max': 28,
        },

        'bahah': {
            'x_min': 30,
            'x_max': 34,
            'y_min': 69,
            'y_max': 72,
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