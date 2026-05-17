# from django.urls import path
# from . import views

# app_name="activity"

# urlpatterns=[
#     path('activity_list/', views.activity_list, name="activity_list"),
#     path('activity_detail/', views.activity_detail, name="activity_detail"),
#     path('activity_result/', views.activity_result, name="activity_result"),
#     path('activity_play/', views.activity_play, name="activity_play"),
#     path('activity_eye/', views.activity_eye, name="activity_eye"),
#     path('activity_color/', views.activity_color_match, name="activity_color_match"),
#     path('activity_ball/', views.activity_balls_box, name="activity_balls_box"),
#     path('activity_shape/', views.activity_shape_match, name="activity_shape_match"),

# ]

from django.urls import path
from . import views

app_name = 'activity'

urlpatterns = [
    path('list/', views.activity_list, name='activity_list'),
    path('play/<int:activity_id>/', views.activity_play, name='activity_play'),
]