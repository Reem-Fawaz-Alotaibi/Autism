from django.urls import path
from . import views

app_name = 'children'

urlpatterns = [
    path('profile/<int:id>/', views.profile_view, name='profile'),
    path('edit/profile/<int:id>/', views.edit_child,name='edit_profile'),
    path('add/child/', views.add_child_view,name='add_child'),
]