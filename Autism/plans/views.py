from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpRequest, HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.staticfiles import finders
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from children.models import Child
from plans.models import SupportPlan,PlanActivity
from ai_analysis.models import VideoAnalysis,Activity,ResourceVideo
from openai import OpenAI
from assessment.models import AssessmentSession,AssessmentAnswer
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import json
import os
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse
from django.conf import settings
import matplotlib.pyplot as plt
import io
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

def ar(text):
    return get_display(reshape(str(text)))


def support_plan_redirect(request):
    plan = SupportPlan.objects.filter(user=request.user).first()

    if not plan:
        return redirect(f"{reverse('main:home_page_view')}#start")

    return redirect('plans:main_plan_view')

# ==========================================
# صفحة الأنشطة المقترحة
# ==========================================

@login_required(login_url='accounts:signin')
def support_plan_view(request: HttpRequest):

    plan = SupportPlan.objects.filter(user=request.user).first()

    if not plan:
        categories         = request.session.get('result_categories', [])
        activity_ids       = request.session.get('result_activities', [])
        ai_summary         = request.session.get('ai_summary', '')
        daily_routine_data = request.session.get('daily_routine', {})

        if not categories:
            return redirect('assessment:questionnaire')

        session = AssessmentSession.objects.filter(
            user=request.user,
            status='completed'
        ).first()

        if not session:
            return redirect('assessment:questionnaire')

        # جلب الأنشطة
        activities = list(Activity.objects.filter(id__in=activity_ids))

        # الخطة الأسبوعية — أنشطة موزعة على الأيام
        days = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
        weekly_activities = []
        for i, day in enumerate(days):
            activity = activities[i % len(activities)] if activities else None
            weekly_activities.append({
                'day':         day,
                'activity':    activity.title if activity else '',
                'description': activity.description if activity else '',
                'category':    activity.category if activity else '',
                'duration':    activity.duration_minutes if activity else 15,
                'activity_id': activity.id if activity else None,
            })

        # نحفظ الروتين من AI + الأنشطة الأسبوعية معاً
        weekly_plan = {
            'routine':         daily_routine_data.get('routine', []),
            'calm_tip':        daily_routine_data.get('calm_tip', ''),
            'behavioral_tip':  daily_routine_data.get('behavioral_tip', ''),
            'activities':      weekly_activities,
        }

        plan = SupportPlan.objects.create(
            session=session,
            child=session.child,
            user=request.user,
            categories=categories,
            ai_summary=ai_summary,
            weekly_plan=weekly_plan,
        )

        for item in weekly_activities:
            PlanActivity.objects.create(
                plan=plan,
                day=item['day'],
                title=item['activity'],
                description=item['description'],
                category=item['category'],
                duration_minutes=item['duration'],
                activity_id=item['activity_id'],
            )

        for key in ['result_categories', 'result_activities', 'result_videos', 'ai_summary', 'daily_routine']:
            request.session.pop(key, None)

    # جلب الأنشطة
    plan_activities  = PlanActivity.objects.filter(plan=plan)
    current_activity = plan_activities.first()
    next_activity    = plan_activities[1] if plan_activities.count() > 1 else None

    # جلب الفيديوهات حسب التصنيف وعمر الطفل
    child_age = (date.today() - plan.child.birth_date).days // 365
    videos = ResourceVideo.objects.filter(
        category__in=plan.categories,
        age_min__lte=child_age,
        age_max__gte=child_age,
        is_active=True
    ).order_by('order')[:4]

    start_date = plan.created_at
    end_date   = start_date + timezone.timedelta(days=6)

    return render(request, 'plans/support_plan.html', {
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
    })


# ==========================================
# الخطة الرئيسية — الروتين اليومي من AI
# ==========================================

@login_required(login_url='accounts:signin')
def main_plan_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()

    today     = date.today()
    day_names = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']

    week_days = []
    for i in range(5):
        d = today + timedelta(days=i - 2)
        week_days.append({
            'name':     day_names[d.weekday()],
            'date':     d.strftime('%d %B'),
            'is_today': d == today,
        })

    other_days = [d for d in week_days if not d['is_today']][2:]

    daily_routine    = []
    calm_tip         = ''
    behavioral_tip   = ''
    current_activity = None
    next_activity    = None
    today_activities = []

    if plan:
        day_map = {
            'الاثنين': 'monday', 'الثلاثاء': 'tuesday',
            'الأربعاء': 'wednesday', 'الخميس': 'thursday',
            'الجمعة': 'friday', 'السبت': 'saturday', 'الأحد': 'sunday'
        }
        today_key        = day_map.get(day_names[today.weekday()], '')
        today_activities = PlanActivity.objects.filter(plan=plan, day=today_key)
        current_activity = today_activities.first()
        next_activity    = today_activities[1] if today_activities.count() > 1 else None

        stored = plan.weekly_plan
        if isinstance(stored, dict):
            daily_routine  = stored.get('routine', [])
            calm_tip       = stored.get('calm_tip', '')
            behavioral_tip = stored.get('behavioral_tip', '')

    return render(request, 'plans/main_plan.html', {
        'plan':             plan,
        'week_days':        week_days,
        'other_days':       other_days,
        'today_activities': today_activities,
        'current_activity': current_activity,
        'next_activity':    next_activity,
        'today_display':    f"{day_names[today.weekday()]} {today.strftime('%d %B')}",
        'daily_routine':    daily_routine,
        'calm_tip':         calm_tip,
        'behavioral_tip':   behavioral_tip,
    })


# ==========================================
# الفيديوهات التعليمية — حسب عمر الطفل
# ==========================================

@login_required(login_url='accounts:signin')
def video_plan_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()
    if not plan:
        return redirect(f"{reverse('main:home_page_view')}#start")

    videos = []
    if plan:
        child_age = (date.today() - plan.child.birth_date).days // 365
        videos = ResourceVideo.objects.filter(
            category__in=plan.categories,
            age_min__lte=child_age,
            age_max__gte=child_age,
            is_active=True
        ).order_by('order')[:6]

    return render(request, 'plans/video_plan.html', {
        'videos': videos,
        'plan':   plan,
    })


# ==========================================
# استراتيجيات الدعم
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
            strategies = strategies[:3]
    return render(request, 'plans/support_strategies.html', {
        'strategies': strategies,
        'plan':       plan,
    })


# ==========================================
# Feedback ولي الأمر — يحدث الخطة بـ AI
# ==========================================

@login_required(login_url='accounts:signin')
def update_plan_feedback(request):
    if request.method != "POST":
        return JsonResponse({'success': False})

    try:
        data     = json.loads(request.body)
        feedback = data.get('feedback', '').strip()
        plan     = SupportPlan.objects.filter(user=request.user).first()

        if not plan or not feedback:
            return JsonResponse({'success': False, 'error': 'بيانات غير كاملة'})

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""
        أنت متخصص في دعم أطفال طيف التوحد.
        ولي الأمر أرسل هذه الملاحظة عن طفله بعد تجربة الخطة:

        "{feedback}"

        معلومات الطفل:
        - التصنيفات الحالية: {', '.join(plan.categories)}
        - ملخص الخطة: {plan.ai_summary}

        بناءً على هذه الملاحظة:
        1. حدد المشكلة الرئيسية التي يواجهها الطفل
        2. اقترح تعديلاً محدداً على الخطة أو نشاطاً بديلاً مناسباً
        3. أعطِ نصيحة عملية لولي الأمر يطبقها مباشرة

        الرد يكون:
        - باللغة العربية
        - موجز وواضح وعملي
        - بدون ترقيم أو عناوين
        - لا يتجاوز 3 جمل
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        suggestion = response.choices[0].message.content.strip()

        return JsonResponse({'success': True, 'suggestion': suggestion})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
   



import os
import io
import matplotlib.pyplot as plt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ملاحظة: تأكد من استيراد الدوال ونماذج قواعد البيانات الخاصة بك هنا
# from .models import Child, VideoAnalysis
# from .utils import ar 

@login_required
def download_report(request, child_id):
    # =========================================================================
    # 1. جلب البيانات والتحقق من الصلاحيات (DATA FETCHING & AUTH)
    # =========================================================================
    child = get_object_or_404(
        Child,
        id=child_id,
        user=request.user
    )
    analysis = VideoAnalysis.objects.filter(child=child).last()

    # تجهيز استجابة الـ PDF وربطها بملف التحميل
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{child.name}_report.pdf"'

    # =========================================================================
    # 2. إعدادات الخطوط والمظهر (FONTS & ASSETS CONFIG)
    # =========================================================================
    font_path = os.path.join(
        settings.BASE_DIR,
        'Autism',
        'static',
        'fonts',
        'Tajawal',
        'Tajawal-Regular.ttf'
    )

    if not os.path.exists(font_path):
        raise Exception(f"❌ Font file not found: {font_path}")

    pdfmetrics.registerFont(TTFont("Arabic", font_path))

    # =========================================================================
    # 3. توليد الرسم البياني (CHART GENERATION)
    # =========================================================================
    chart_image = None

    if analysis:
        labels = ["Eye Contact", "Attention", "Repetitive", "Interaction"]
        values = [
            analysis.eye_contact_score,
            analysis.attention_score,
            analysis.repetitive_behavior_score,
            analysis.interaction_level_score
        ]

        plt.figure(figsize=(4, 2.5))
        plt.bar(labels, values)
        plt.title("AI Analysis Scores")
        plt.ylim(0, 100)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_image = ImageReader(buffer)
        plt.close()

    # =========================================================================
    # 4. إعداد صفحة الـ PDF والخلفية (PDF CANVAS & BACKGROUND)
    # =========================================================================
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # رسم الخلفية العامة (خفيف)
    p.setFillColor(colors.whitesmoke)
    p.rect(0, 0, width, height, fill=1)

    # رسم الهيدر العلوي (Header Bar)
    p.setFillColor(colors.HexColor("#4F46E5"))
    p.rect(0, height - 70, width, 70, fill=1)

    # عنوان التقرير داخل الهيدر
    p.setFillColor(colors.white)
    p.setFont("Arabic", 18)
    p.drawRightString(width - 30, height - 45, ar("تقرير تحليل الطفل"))

    # رسم الكارد الأبيض الرئيسي (Card Box) لترتيب المحتوى داخله
    p.setFillColor(colors.white)
    p.setStrokeColor(colors.lightgrey)
    p.roundRect(30, 40, width - 60, height - 130, 15, fill=1, stroke=1)

    # =========================================================================
    # 5. رسم وكتابة البيانات داخل الـ PDF (CONTENT RENDERING)
    # =========================================================================
    
    # --- [أ] بيانات الطفل الأساسية ---
    y_position = height - 120
    p.setFillColor(colors.black)
    p.setFont("Arabic", 13)

    p.drawRightString(width - 50, y_position, ar(f"اسم الطفل: {child.name}")); y_position -= 25

    gender = "ذكر" if child.gender == "male" else "أنثى"
    p.drawRightString(width - 50, y_position, ar(f"الجنس: {gender}")); y_position -= 25

    communication = "لفظي" if child.communication_type == "verbal" else "غير لفظي"
    p.drawRightString(width - 50, y_position, ar(f"التواصل: {communication}")); y_position -= 25

    sensory_map = {
        "sound": "الصوت",
        "touch": "اللمس",
        "light": "الضوء",
        "none": "لا توجد"
    }
    sensory = sensory_map.get(child.sensory_sensitivities, "غير محدد")
    p.drawRightString(width - 50, y_position, ar(f"الحساسية: {sensory}"))

    # --- [ب] الرسم البياني والدرجات الرقمية ---
    # نزلنا الـ Y عشان نضمن عدم تداخل الرسم البياني مع البيانات الأساسية فوقه
    chart_y = y_position - 180 
    
    if analysis and chart_image:
        p.drawImage(
            chart_image,
            50,
            chart_y,
            width=250,
            height=150
        )

    if analysis:
        p.setFont("Arabic", 12)
        # محاذاة النصوص رقمياً بجانب الرسم البياني
        p.drawRightString(width - 50, chart_y + 110, ar(f"التواصل البصري: {analysis.eye_contact_score}"))
        p.drawRightString(width - 50, chart_y + 85, ar(f"الانتباه: {analysis.attention_score}"))
        p.drawRightString(width - 50, chart_y + 60, ar(f"التكرار: {analysis.repetitive_behavior_score}"))
        p.drawRightString(width - 50, chart_y + 35, ar(f"التفاعل: {analysis.interaction_level_score}"))

    # --- [ج] صندوق الملخص النصي (Summary Box) ---
    if analysis:
        summary_y = chart_y - 40
        p.setFont("Arabic", 14)
        p.drawRightString(width - 50, summary_y, ar("ملخص التحليل"))

        text = p.beginText(width - 50, summary_y - 20)
        text.setFont("Arabic", 11)
        # تحديد المسافة بين السطور لضمان عدم تداخل النص العربي
        text.setLeading(16) 

        for line in (analysis.ai_summary or "").splitlines():
            text.textLine(ar(line))

        p.drawText(text)

    # =========================================================================
    # إنهاء وحفظ ملف الـ PDF
    # =========================================================================
    p.showPage()
    p.save()

    return response