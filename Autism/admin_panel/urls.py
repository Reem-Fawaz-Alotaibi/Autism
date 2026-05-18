from django.urls import path
from . import views

app_name="admin_panel"

urlpatterns=[
    path('dashboard/', views.dashboard_view,name='dashboard_view'),
    path('reports/<int:id>/',views.report_detail,name='report_detail'),
    path('reports/delete/<int:id>/',views.delete_report,name='delete_report'),
    path(
    'users/block/<int:id>/',
    views.block_user,
    name='block_user'
),

path(
    'users/unblock/<int:id>/',
    views.unblock_user,
    name='unblock_user'
),

path(
    'users/delete/<int:id>/',
    views.delete_user,
    name='delete_user'
),

]