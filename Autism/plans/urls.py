from django.urls import path
from . import views

app_name="plans"

urlpatterns=[
    path('main_plan/', views.main_plan_view, name='main_plan_view'),
    path('support/plan/', views.support_plan_view, name='support_plan_view'),
    path('video/plan/', views.video_plan_view, name='video_plan_view'),
    path('support/strategies/plan/', views.support_strategies_view, name='support_strategies_view')

]