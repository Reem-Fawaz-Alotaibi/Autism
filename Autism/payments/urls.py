from django.urls import path
from .views import create_payment, payment_success

urlpatterns = [
    path('pay/', create_payment, name='pay'),
    path('success/', payment_success, name='payment_success'),
]