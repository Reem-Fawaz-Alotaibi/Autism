from django.db import models
from django.conf import settings
from children.models import Child

class SkillCategory(models.TextChoices):
    FOCUS         = 'focus',         'التركيز والانتباه'
    EYE_CONTACT   = 'eye_contact',   'التواصل البصري'
    SOCIAL        = 'social',        'التفاعل الاجتماعي'
    COMMUNICATION = 'communication', 'التواصل اللغوي'
    MOTOR         = 'motor',         'المهارات الحركية'
    BEHAVIOR      = 'behavior',      'السلوك والتصرفات'



class Activity(models.Model):

    LEVEL_CHOICES = [
        ('easy',   'سهل'),
        ('medium', 'متوسط'),
        ('hard',   'صعب'),
    ]

    CATEGORY_CHOICES = [
         ('visual',   'بصري'),
         ('sensory',  'حسي'),
         ('motor',    'حركي'),
         ('language', 'لغوي'),
     ]

    title       = models.CharField(max_length=200, verbose_name="اسم النشاط")
    description = models.TextField(verbose_name="وصف النشاط")
    category    = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="التصنيف")
    level       = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='easy', verbose_name="المستوى")
    age_min     = models.PositiveIntegerField(default=2, verbose_name="العمر الأدنى")
    age_max     = models.PositiveIntegerField(default=12, verbose_name="العمر الأقصى")
    emoji       = models.CharField(max_length=10, blank=True, verbose_name="إيموجي")
    activity_file = models.CharField(max_length=100, default='null')  # مثال: color_match.html
    is_active   = models.BooleanField(default=True, verbose_name="مفعّل")
    order       = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    created_at  = models.DateTimeField(auto_now_add=True)
    tag         = models.CharField(max_length=50, blank=True)  # مثال: "بصري + حركي"

    class Meta:
        ordering = ['order']
        verbose_name = "نشاط"
        verbose_name_plural = "الأنشطة"

    def __str__(self):
        return f"{self.title} — {self.get_category_display()}"


class ResourceVideo(models.Model):

    title       = models.CharField(max_length=200, verbose_name="عنوان الفيديو")
    description = models.TextField(blank=True, verbose_name="وصف الفيديو")
    video_file  = models.FileField(upload_to='resource_videos/', verbose_name="ملف الفيديو")
    thumbnail   = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True, verbose_name="صورة مصغرة")
    category    = models.CharField(max_length=50, choices=SkillCategory.choices, verbose_name="التصنيف")
    age_min     = models.PositiveIntegerField(default=2, verbose_name="العمر الأدنى")
    age_max     = models.PositiveIntegerField(default=12, verbose_name="العمر الأقصى")
    is_active   = models.BooleanField(default=True, verbose_name="مفعّل")
    order       = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "فيديو تعليمي"
        verbose_name_plural = "الفيديوهات التعليمية"

    def __str__(self):
        return f"{self.title} — {self.get_category_display()}"
    

##################################################################
class VideoAnalysis(models.Model):

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="video_analyses"
    )

    video = models.FileField(upload_to="videos/")

    ai_summary = models.TextField()

    eye_contact_score = models.IntegerField()

    attention_score = models.IntegerField()

    repetitive_behavior_score = models.IntegerField()

    interaction_level_score = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.child.name} - Video Analysis"