from django.db import models

class Activity(models.Model):

    CATEGORY_CHOICES = [
        ('visual',   'بصري'),
        ('sensory',  'حسي'),
        ('motor',    'حركي'),
        ('language', 'لغوي'),
    ]

    LEVEL_CHOICES = [
        ('easy',   'سهل'),
        ('medium', 'متوسط'),
        ('hard',   'صعب'),
    ]

    title       = models.CharField(max_length=200)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    emoji       = models.CharField(max_length=10)
    level       = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='easy')
    html_file   = models.CharField(max_length=100)  # مثال: color_match.html
    tag         = models.CharField(max_length=50, blank=True)  # مثال: "بصري + حركي"
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
