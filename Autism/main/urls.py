from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('home/', views.home_page_view, name="home_page_view"),
    path("about-us/", views.about_us_view, name="about_us"),
    path("contact-us/", views.contact_us_view, name="contact_us"),
    path("how-it-works/", views.how_it_works_view, name="how_it_works"),
    path("privacy-policy/", views.privacy_policy_view, name="privacy_policy"),
    path("terms-of-service/", views.terms_of_service_view, name="terms_of_service"),
    path("questions/", views.questions_view, name="questions"),
    path('theme/<str:theme>/', views.set_theme, name='set_theme'),
    path("dashbord/admin/", views.dashboard_view, name="dashboard_view"),
    path("404", views.test_view, name="dashboard_view"),
]