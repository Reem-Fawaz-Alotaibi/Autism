from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from children.models import Child
from community.models import Post, Report
from support_map.models import AutismSupportPlace
from django.utils import timezone
from datetime import timedelta

# Create your views here.

def dashboard_view(request:HttpRequest):
    users_count = User.objects.filter(is_staff=False).count()
    children_count = Child.objects.count()
    post_count = Post.objects.count()
    reports_count = Report.objects.count()
    support_centers_count = AutismSupportPlace.objects.count()

    last_month = timezone.now() - timedelta(days=30)

    active_users_count = User.objects.filter(is_staff=False,last_login__gte=last_month).count()

    latest_reports = Report.objects.select_related('user','post').order_by('-created_at')[:5]

    latest_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]

    return render(request, 'admin_panel/dashboard.html',{
        'users_count': users_count,
        'children_count': children_count,
        'post_count':post_count,
        'reports_count': reports_count,
        'active_users_count': active_users_count,
        'latest_reports': latest_reports,
        'latest_users': latest_users,
        'support_centers_count': support_centers_count,
    })



def report_detail(request:HttpRequest, id):

    report = get_object_or_404(Report, id=id)

    return render(request,'admin_panel/report_detail.html',{'report': report})


def delete_report(request: HttpRequest, id):

    report = get_object_or_404(Report, id=id)

    if report.post:
        report.post.delete()

        report.post = None

    report.status = 'solved'
    report.save()

    return redirect('admin_panel:dashboard_view')

def solve_report(request: HttpRequest, id):

    report = get_object_or_404(Report, id=id)

    report.status = 'solved'
    report.save()

    return redirect('admin_panel:report_detail', id=report.id)


def block_user(request, id):

    user = get_object_or_404(User, id=id)

    user.is_active = False
    user.save()

    return redirect('admin_panel:dashboard_view')


def unblock_user(request, id):

    user = get_object_or_404(User, id=id)

    user.is_active = True
    user.save()

    return redirect('admin_panel:dashboard_view')


def delete_user(request, id):

    user = get_object_or_404(User, id=id)

    user.delete()

    return redirect('admin_panel:dashboard_view')