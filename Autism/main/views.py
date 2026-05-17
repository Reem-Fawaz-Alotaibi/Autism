from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def home_page_view(request: HttpRequest):
    return render(request, 'main/home.html')


def about_us_view(request: HttpRequest):
    return render(request, 'main/about_us.html')


def contact_us_view(request: HttpRequest):
    return render(request, 'main/contact_us.html')


def how_it_works_view(request: HttpRequest):
    return render(request, 'main/how_it_works.html')


def privacy_policy_view(request: HttpRequest):
    return render(request, 'main/privacy_policy.html')


def terms_of_service_view(request: HttpRequest):
    return render(request, 'main/terms_of_service.html')


def questions_view(request: HttpRequest):
    return render(request, 'main/questions.html')

def dashboard_view(request: HttpRequest):
    return render(request, 'main/dashbord_admin.html')

def test_view(request: HttpRequest):
    return render(request, 'main/404.html')
