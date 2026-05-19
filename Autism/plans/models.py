from django.db import models
from django.conf import settings
from children.models import Child
from assessment.models import AssessmentSession


class SupportPlan(models.Model):

    session  = models.OneToOneField(AssessmentSession, on_delete=models.CASCADE, related_name='plan')
    child    = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='plans')
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categories   = models.JSONField(verbose_name="التصنيفات")
    ai_summary   = models.TextField(verbose_name="ملخص AI عن الطفل")
    weekly_plan  = models.JSONField(verbose_name="الخطة الأسبوعية")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "خطة دعم"
        verbose_name_plural = "خطط الدعم"

    def __str__(self):
        return f"خطة {self.child.name} — {self.created_at.strftime('%Y-%m-%d')}"


class PlanActivity(models.Model):

    DAY_CHOICES = [
        ('saturday',  'السبت'),
        ('sunday',    'الأحد'),
        ('monday',    'الاثنين'),
        ('tuesday',   'الثلاثاء'),
        ('wednesday', 'الأربعاء'),
        ('thursday',  'الخميس'),
        ('friday',    'الجمعة'),
    ]

    plan             = models.ForeignKey(SupportPlan, on_delete=models.CASCADE, related_name='plan_activities')
    day              = models.CharField(max_length=20, choices=DAY_CHOICES)
    title            = models.CharField(max_length=200)
    description      = models.TextField()
    category         = models.CharField(max_length=50)
    duration_minutes = models.PositiveIntegerField(default=15)
    activity_id      = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['day']
        verbose_name = "نشاط في الخطة"
        verbose_name_plural = "أنشطة الخطة"

    def __str__(self):
        return f"{self.get_day_display()} — {self.title}"