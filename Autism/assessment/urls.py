from django.urls import path
from . import views

app_name = "assessment"

urlpatterns = [
    # مسار أ — فيديو + تقييم
    path('step1/', views.upload_video, name="upload_video"),
    path('step2/', views.questionnaire_video, name="questionnaire_video"),

    # مسار ب — تقييم فقط
    path('questionnaire/', views.questionnaire, name="questionnaire"),

    # المعالجة — مشترك بين المسارين
    path('processing/', views.processing_view, name="processing"),
]