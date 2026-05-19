from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.

def main_plan_view (request:HttpRequest):

    return render(request, 'plans/main_plan.html')

def support_plan_view(request:HttpRequest):

    return render(request, 'plans/support_plan.html')

def video_plan_view(request:HttpRequest):

    return render(request, 'plans/video_plan.html')

def support_strategies_view(request:HttpRequest):

    return render(request, 'plans/support_strategies.html')

