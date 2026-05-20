from django.urls import path
from . import views

app_name="plans"

urlpatterns=[
    path('main_plan/', views.main_plan_view, name='main_plan_view'),
<<<<<<< HEAD
    path('support_plan/', views.support_plan_view, name='support_plan_view'),
    # path('<int:report_id>/',views.report_detail,name='report_detail'),
    # path('download/<int:report_id>/', views.download_report, name='download_report')
    path('download-report/<int:child_id>/',views.download_report,name='download_report'),
]
=======
    path('support/plan/', views.support_plan_view, name='support_plan_view'),
    path('video/plan/', views.video_plan_view, name='video_plan_view'),
    path('support/strategies/plan/', views.support_strategies_view, name='support_strategies_view')

]
>>>>>>> b21ece247883f99f30ea46b301ad5c3ed4bd9485
