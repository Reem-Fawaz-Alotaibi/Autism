from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.utils import timezone

from assessment.models import AssessmentSession, AssessmentResult
from ai_analysis.models import Activity, ResourceVideo
from .models import SupportPlan, PlanActivity


# ==========================================
# صفحة الخطة الرئيسية
# ==========================================

@login_required(login_url='accounts:signin')
def support_plan_view(request: HttpRequest):

    # جلب آخر خطة للمستخدم
    plan = SupportPlan.objects.filter(user=request.user).first()

    if not plan:
        # لو ما في خطة، نبنيها من السيشن
        categories    = request.session.get('result_categories', [])
        activity_ids  = request.session.get('result_activities', [])
        video_ids     = request.session.get('result_videos', [])
        ai_summary    = request.session.get('ai_summary', '')

        if not categories:
            return redirect('assessment:questionnaire')

        # جلب آخر جلسة مكتملة
        session = AssessmentSession.objects.filter(
            user=request.user,
            status='completed'
        ).first()

        if not session:
            return redirect('assessment:questionnaire')

        # جلب الأنشطة والفيديوهات
        activities = list(Activity.objects.filter(id__in=activity_ids))
        videos     = list(ResourceVideo.objects.filter(id__in=video_ids))

        # بناء الخطة الأسبوعية
        days = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
        weekly_plan = []
        for i, day in enumerate(days):
            activity = activities[i % len(activities)] if activities else None
            weekly_plan.append({
                'day': day,
                'activity': activity.title if activity else '',
                'description': activity.description if activity else '',
                'category': activity.category if activity else '',
                'duration': activity.duration_minutes if activity else 15,
                'activity_id': activity.id if activity else None,
            })

        # حفظ الخطة في DB
        plan = SupportPlan.objects.create(
            session=session,
            child=session.child,
            user=request.user,
            categories=categories,
            ai_summary=ai_summary,
            weekly_plan=weekly_plan,
        )

        # حفظ أنشطة الخطة
        for item in weekly_plan:
            PlanActivity.objects.create(
                plan=plan,
                day=item['day'],
                title=item['activity'],
                description=item['description'],
                category=item['category'],
                duration_minutes=item['duration'],
                activity_id=item['activity_id'],
            )

        # مسح السيشن
        for key in ['result_categories', 'result_activities', 'result_videos', 'ai_summary']:
            request.session.pop(key, None)

    # جلب الأنشطة من DB
    plan_activities = PlanActivity.objects.filter(plan=plan)
    current_activity = plan_activities.first()
    next_activity    = plan_activities[1] if plan_activities.count() > 1 else None

    # جلب الفيديوهات
    videos = ResourceVideo.objects.filter(
        category__in=plan.categories,
        is_active=True
    )[:4]

    # تاريخ الخطة
    start_date = plan.created_at
    end_date   = start_date + timezone.timedelta(days=6)

    context = {
        'plan':             plan,
        'current_activity': current_activity,
        'next_activity':    next_activity,
        'plan_activities':  plan_activities,
        'videos':           videos,
        'categories':       plan.categories,
        'ai_summary':       plan.ai_summary,
        'start_date':       start_date.strftime('%d %B'),
        'end_date':         end_date.strftime('%d %B'),
        'child':            plan.child,
    }

    return render(request, 'plans/support_plan.html', context)


# ==========================================
# صفحة الخطة الرئيسية (اختيار المسار)
# ==========================================

from datetime import date, timedelta

@login_required(login_url='accounts:signin')
def main_plan_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()

    # أيام الأسبوع
    today = date.today()
    day_names = ['الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت','الأحد']
    week_days = []
    for i in range(5):
        d = today + timedelta(days=i-2)
        week_days.append({
            'name': day_names[d.weekday()],
            'date': d.strftime('%d %B'),
            'is_today': d == today,
        })

    other_days = [d for d in week_days if not d['is_today']][2:]

    # أنشطة اليوم
    today_activities = []
    current_activity = None
    next_activity = None

    if plan:
        today_name = day_names[today.weekday()].lower()
        day_map = {
            'الاثنين': 'monday', 'الثلاثاء': 'tuesday',
            'الأربعاء': 'wednesday', 'الخميس': 'thursday',
            'الجمعة': 'friday', 'السبت': 'saturday', 'الأحد': 'sunday'
        }
        today_key = day_map.get(day_names[today.weekday()], '')
        today_activities = PlanActivity.objects.filter(plan=plan, day=today_key)
        current_activity = today_activities.first()
        next_activity = today_activities[1] if today_activities.count() > 1 else None

    return render(request, 'plans/main_plan.html', {
        'plan': plan,
        'week_days': week_days,
        'other_days': other_days,
        'today_activities': today_activities,
        'current_activity': current_activity,
        'next_activity': next_activity,
        'today_display': f"{day_names[today.weekday()]} {today.strftime('%d %B')}",
    })


# ==========================================
# صفحة الفيديوهات التعليمية
# ==========================================

@login_required(login_url='accounts:signin')
def video_plan_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()

    videos = []
    if plan:
        videos = ResourceVideo.objects.filter(
            category__in=plan.categories,
            is_active=True
        )[:6]

    return render(request, 'plans/video_plan.html', {'videos': videos, 'plan': plan})


# ==========================================
# صفحة استراتيجيات الدعم
# ==========================================

@login_required(login_url='accounts:signin')
def support_strategies_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()

    strategies = []
    if plan:
        category_strategies = {
            'visual': [
                'استخدم بطاقات مصورة ملونة أثناء الحديث مع طفلك',
                'قلل من المشتتات البصرية في غرفة الدراسة',
                'استخدم الإشارات البصرية بدلاً من التعليمات اللفظية فقط',
            ],
            'sensory': [
                'وفر بيئة هادئة وخالية من الضوضاء قدر الإمكان',
                'استخدم سماعات عند وجود أصوات مزعجة',
                'جرب الأقمشة الناعمة في ملابس طفلك',
            ],
            'motor': [
                'خصص وقتاً يومياً للعب الحر والحركة',
                'استخدم أدوات مساعدة للكتابة إذا لزم',
                'جرب تمارين التوازن البسيطة مع طفلك',
            ],
            'language': [
                'تحدث مع طفلك ببطء ووضوح',
                'كرر الكلمات الجديدة في سياقات مختلفة',
                'استخدم الغناء والأناشيد لتطوير اللغة',
            ],
        }

        for cat in plan.categories:
            if cat in category_strategies:
                strategies.extend(category_strategies[cat])

    return render(request, 'plans/support_strategies.html', {
        'strategies': strategies,
        'plan': plan
    })