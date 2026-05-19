from django.db import models
from django.conf import settings
from children.models import Child


class AssessmentSession(models.Model):

    PATH_CHOICES = [
        ('video', 'فيديو + تقييم'),
        ('questionnaire', 'تقييم فقط'),
    ]

    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('analyzing', 'جاري التحليل'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
    ]

    child        = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='assessments')
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    path         = models.CharField(max_length=20, choices=PATH_CHOICES)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "جلسة تقييم"
        verbose_name_plural = "جلسات التقييم"

    def __str__(self):
        return f"{self.child.name} — {self.get_path_display()} — {self.get_status_display()}"


class AssessmentQuestion(models.Model):

    PATH_CHOICES = [
        ('video', 'مسار الفيديو'),
        ('questionnaire', 'مسار التقييم فقط'),
    ]

    CATEGORY_CHOICES = [
        ('visual',       'بصري'),
        ('sensory',      'حسي'),
        ('motor',        'حركي'),
        ('language',     'لغوي'),
    ]

    text      = models.TextField(verbose_name="نص السؤال")
    path      = models.CharField(max_length=20, choices=PATH_CHOICES, verbose_name="المسار")
    category  = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="التصنيف")
    source    = models.CharField(max_length=50, blank=True, verbose_name="المصدر العلمي")
    order     = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['path', 'order']
        verbose_name = "سؤال تقييم"
        verbose_name_plural = "أسئلة التقييم"

    def __str__(self):
        return f"[{self.get_path_display()}] {self.text[:60]}"


class AssessmentAnswer(models.Model):

    ANSWER_CHOICES = [
        ('always',    'دائماً'),
        ('sometimes', 'أحياناً'),
        ('rarely',    'نادراً'),
        ('never',     'أبداً'),
    ]

    ANSWER_SCORES = {
        'always':    0,
        'sometimes': 1,
        'rarely':    2,
        'never':     3,
    }

    session  = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    answer   = models.CharField(max_length=20, choices=ANSWER_CHOICES)

    class Meta:
        unique_together = ('session', 'question')
        verbose_name = "إجابة"
        verbose_name_plural = "الإجابات"

    @property
    def score(self):
        return self.ANSWER_SCORES.get(self.answer, 0)

    def __str__(self):
        return f"{self.question.text[:40]} → {self.get_answer_display()}"


class AssessmentResult(models.Model):

    session               = models.OneToOneField(AssessmentSession, on_delete=models.CASCADE, related_name='result')
    categories            = models.JSONField(verbose_name="التصنيفات المقترحة")
    ai_summary            = models.TextField(verbose_name="ملخص AI عن الطفل")
    gemini_video_analysis = models.TextField(blank=True, verbose_name="تحليل Gemini للفيديو")
    created_at            = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نتيجة تقييم"
        verbose_name_plural = "نتائج التقييم"

    def __str__(self):
        return f"نتيجة — {self.session}"