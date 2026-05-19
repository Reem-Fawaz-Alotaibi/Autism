from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.urls import reverse
import os
from datetime import date

from ai_analysis.openai_service import get_recommendations, build_daily_routine
from ai_analysis.gemini_service import analyze_video
from children.models import Child
from ai_analysis.models import VideoAnalysis
from .models import AssessmentSession, AssessmentQuestion, AssessmentAnswer, AssessmentResult
from cloudinary.uploader import upload


# ==========================================
# مسار أ — الخطوة 1: رفع الفيديو
# ==========================================

@login_required(login_url='accounts:signin')
def upload_video(request):
    children = Child.objects.filter(user=request.user)

    if request.method == "POST":
        child_id   = request.POST.get("child")
        video_file = request.FILES.get("video")

        try:
            child = Child.objects.get(id=child_id, user=request.user)
        except Child.DoesNotExist:
            return redirect("assessment:upload_video")

        # تحليل الفيديو بـ Gemini
        if hasattr(video_file, 'temporary_file_path'):
            video_path    = video_file.temporary_file_path()
            is_temp_saved = False
        else:
            temp_file_name = default_storage.save(f"temp_{video_file.name}", ContentFile(video_file.read()))
            video_path     = default_storage.path(temp_file_name)
            is_temp_saved  = True

        try:
            analysis_result = analyze_video(video_path)
        finally:
            if is_temp_saved and os.path.exists(video_path):
                os.remove(video_path)

        # رفع الفيديو لـ Cloudinary
        uploaded_video = upload(video_file, resource_type="video")

        # حفظ تحليل الفيديو
        video_analysis = VideoAnalysis.objects.create(
            child=child,
            video=uploaded_video["secure_url"],
            ai_summary=analysis_result,
            eye_contact_score=0,
            attention_score=0,
            repetitive_behavior_score=0,
            interaction_level_score=0
        )

        # إنشاء جلسة تقييم جديدة
        session = AssessmentSession.objects.create(
            child=child,
            user=request.user,
            path='video',
            status='pending'
        )

        request.session['assessment_session_id'] = session.id
        request.session['video_analysis_id']     = video_analysis.id

        return redirect("assessment:questionnaire_video")

    return render(request, "assessment/upload_video.html", {"children": children})


# ==========================================
# مسار أ — الخطوة 2: أسئلة مسار الفيديو
# ==========================================

@login_required(login_url='accounts:signin')
def questionnaire_video(request):
    session_id = request.session.get('assessment_session_id')
    if not session_id:
        return redirect("assessment:upload_video")

    session   = get_object_or_404(AssessmentSession, id=session_id, user=request.user)
    questions = list(AssessmentQuestion.objects.filter(path='video', is_active=True))
    total     = len(questions)

    if request.method == "POST":
        question_id  = request.POST.get("question_id")
        answer_value = request.POST.get("answer")
        direction    = request.POST.get("direction")
        current_index = int(request.POST.get("current_index", 1))

        if answer_value and question_id:
            question = get_object_or_404(AssessmentQuestion, id=question_id)
            AssessmentAnswer.objects.update_or_create(
                session=session,
                question=question,
                defaults={'answer': answer_value}
            )

        if direction == "prev":
            next_index = max(1, current_index - 1)
        elif direction == "finish":
            return redirect("assessment:processing")
        else:
            next_index = min(total, current_index + 1)

        return redirect(f"{request.path}?q={next_index}")

    current_index = int(request.GET.get("q", 1))
    current_index = max(1, min(current_index, total))
    question      = questions[current_index - 1]
    progress      = round((current_index / total) * 100)

    saved_answer = None
    existing = AssessmentAnswer.objects.filter(session=session, question=question).first()
    if existing:
        saved_answer = existing.answer

    return render(request, "assessment/questionnaire-video.html", {
        "question":      question,
        "current_index": current_index,
        "total":         total,
        "progress":      progress,
        "saved_answer":  saved_answer,
    })


# ==========================================
# مسار ب — تقييم فقط
# ==========================================

@login_required(login_url='accounts:signin')
def questionnaire(request):
    if 'assessment_session_id' not in request.session:
        child = Child.objects.filter(user=request.user).first()
        if not child:
            return redirect("children:add")

        session = AssessmentSession.objects.create(
            child=child,
            user=request.user,
            path='questionnaire',
            status='pending'
        )
        request.session['assessment_session_id'] = session.id

    session_id = request.session.get('assessment_session_id')
    session    = get_object_or_404(AssessmentSession, id=session_id, user=request.user)
    questions  = list(AssessmentQuestion.objects.filter(path='questionnaire', is_active=True))
    total      = len(questions)

    if request.method == "POST":
        question_id   = request.POST.get("question_id")
        answer_value  = request.POST.get("answer")
        direction     = request.POST.get("direction")
        current_index = int(request.POST.get("current_index", 1))

        if answer_value and question_id:
            question = get_object_or_404(AssessmentQuestion, id=question_id)
            AssessmentAnswer.objects.update_or_create(
                session=session,
                question=question,
                defaults={'answer': answer_value}
            )

        if direction == "prev":
            next_index = max(1, current_index - 1)
        elif direction == "finish":
            return redirect("assessment:processing")
        else:
            next_index = min(total, current_index + 1)

        return redirect(f"{request.path}?q={next_index}")

    current_index = int(request.GET.get("q", 1))
    current_index = max(1, min(current_index, total))
    question      = questions[current_index - 1]
    progress      = round((current_index / total) * 100)

    saved_answer = None
    existing = AssessmentAnswer.objects.filter(session=session, question=question).first()
    if existing:
        saved_answer = existing.answer

    return render(request, "assessment/questionnaire.html", {
        "question":      question,
        "current_index": current_index,
        "total":         total,
        "progress":      progress,
        "saved_answer":  saved_answer,
    })


# ==========================================
# صفحة المعالجة — تحليل AI
# ==========================================

@login_required(login_url='accounts:signin')
def processing_view(request):

    # GET — عرض الصفحة فقط مع تمرير المسار
    if request.method == "GET":
        session_id = request.session.get('assessment_session_id')
        path = 'questionnaire'
        if session_id:
            session = AssessmentSession.objects.filter(id=session_id, user=request.user).first()
            if session:
                path = session.path
        return render(request, 'assessment/processing.html', {'path': path})

    # POST — تنفيذ التحليل عبر AJAX
    session_id = request.session.get('assessment_session_id')
    if not session_id:
        return JsonResponse({'success': False, 'error': 'لا توجد جلسة'})

    try:
        session = get_object_or_404(AssessmentSession, id=session_id, user=request.user)

        # جلب الإجابات
        answers = AssessmentAnswer.objects.filter(session=session).select_related('question')
        questionnaire_answers = {
            a.question.text: a.get_answer_display()
            for a in answers
        }

        # جلب تحليل Gemini لو مسار أ
        gemini_summary = ""
        if session.path == 'video':
            video_analysis_id = request.session.get('video_analysis_id')
            if video_analysis_id:
                video_obj = VideoAnalysis.objects.filter(id=video_analysis_id).first()
                if video_obj:
                    gemini_summary = video_obj.ai_summary

        session.status = 'analyzing'
        session.save()

        # حساب العمر
        child     = session.child
        child_age = (date.today() - child.birth_date).days // 365

        # معلومات الطفل
        child_info = {
            'نوع التواصل':      child.get_communication_type_display(),
            'الحساسية الحسية':  child.get_sensory_sensitivities_display(),
            'الأهداف الحالية':  child.goals,
            'ملاحظات ولي الأمر': child.notes,
        }

        # إرسال لـ OpenAI — التصنيفات والأنشطة
        result = get_recommendations(
            video_analysis=gemini_summary,
            questionnaire_answers=questionnaire_answers,
            child_age=child_age,
            child_info=child_info
        )

        # بناء الروتين اليومي
        daily_routine = build_daily_routine(
            child_age=child_age,
            categories=result['categories'],
            child_info=child_info
        )

        # حفظ النتيجة في DB — مرة واحدة فقط
        AssessmentResult.objects.update_or_create(
            session=session,
            defaults={
                'categories':            result['categories'],
                'ai_summary':            daily_routine.get('behavioral_tip', ''),
                'gemini_video_analysis': gemini_summary,
            }
        )

        session.status       = 'completed'
        session.completed_at = timezone.now()
        session.save()

        # حفظ في السيشن للخطة
        request.session['result_categories'] = result['categories']
        request.session['result_activities'] = [a.id for a in result['activities']]
        request.session['result_videos']     = [v.id for v in result['videos']]
        request.session['daily_routine']     = daily_routine
        request.session['ai_summary']        = daily_routine.get('behavioral_tip', '')

        del request.session['assessment_session_id']

        return JsonResponse({
            'success':      True,
            'redirect_url': reverse('plans:support_plan_view')
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})