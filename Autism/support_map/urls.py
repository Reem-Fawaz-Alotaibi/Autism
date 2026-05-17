from django.urls import path
from . import views

app_name="map"

urlpatterns=[
    path('support/map/' , views.support_map_view,  name='support_map_view'),
    path('create/place', views.create_place_view, name='create_place_view'),
    path('edit/<int:place_id>/',views.edit_place_view,name='edit'),
    path('delete/<int:place_id>/',views.delete_place_view,name='delete'),
    path('like/<int:place_id>/',views.toggle_like_view,name='like'),
]