from django.urls import path
from . import views

app_name="plans"

urlpatterns=[
    path('main_plan/', views.main_plan_view, name='main_plan_view'),
    path('support_plan/', views.support_plan_view, name='support_plan_view'),
    # path('<int:report_id>/',views.report_detail,name='report_detail'),
    # path('download/<int:report_id>/', views.download_report, name='download_report')
    path('download-report/<int:child_id>/',views.download_report,name='download_report'),
]
