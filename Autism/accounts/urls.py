from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('accounts/guest/', views.guest_login, name='guest_login'),
    path('', views.signup_view,name='signup'),
    path('accounts/signin/', views.signin_view,name='signin'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/reset/password/', views.reset_view,name='reset'),
    path('accounts/profile/', views.profile,name='profile'),
    path('accounts/edit/profile/', views.edit_profile,name='edit_profile'),
    path('accounts/settings', views.settings_view,name='settings'),
    path('accounts/saved/centers/', views.saved_centers_view,name='saved_centers_view'),
]
