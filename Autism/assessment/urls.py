from django.urls import path
from . import views

app_name="assessment"

urlpatterns=[
    path('step1/', views.upload_video, name="upload_video"),
    path('step2/', views.questionnaire_video, name="questionnaire_video"),
    path('step3/', views.processing_view, name="processing_view"),
    path('questionnaire/', views.questionnaire, name="questionnaire"),
]