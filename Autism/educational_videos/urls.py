from django.urls import path
from . import views

app_name="edu_video"

urlpatterns=[
    path('all/videos', views.all_educational_videos_view, name='all_educational_videos_view'),
    path('videos/<int:id>/',views.video_details_view,name='video_details'),
]