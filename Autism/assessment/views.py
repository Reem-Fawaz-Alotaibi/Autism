from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from ai_analysis.openai_service import get_recommendations
# استيراد الموديلات (تأكدي من مطابقة أسماء التطبيقات والموديلات لديكِ)
from children.models import Child
from ai_analysis.models import VideoAnalysis

# استيراد مكتبة Cloudinary للرفع
from cloudinary.uploader import upload

# استيراد الدالة التي أنشأناها في الخطوة السابقة
from ai_analysis.gemini_service import analyze_video

@login_required(login_url='accounts:signin')
def upload_video(request):
    # جلب الأطفال التابعين للمستخدم الحالي لتضمينهم في القائمة المنسدلة (Dropdown)
    children = Child.objects.filter(user=request.user)

    if request.method == "POST":
        child_id = request.POST.get("child")
        video_file = request.FILES.get("video")

        try:
            child = Child.objects.get(id=child_id, user=request.user)
        except Child.DoesNotExist:
            return redirect("assessment:upload_video")

        # --- تأمين مسار الفيديو لـ Gemini ---
        # إذا كان دجانغو خزن الفيديو في مسار مؤقت (لأنه كبير) نأخذه مباشرة
        if hasattr(video_file, 'temporary_file_path'):
            video_path = video_file.temporary_file_path()
            is_temp_saved = False
        else:
            # إذا كان الفيديو صغيراً وخزن في الذاكرة، نحفظه مؤقتاً على القرص لنحصل على مسار حقيقي
            temp_file_name = default_storage.save(f"temp_{video_file.name}", ContentFile(video_file.read()))
            video_path = default_storage.path(temp_file_name)
            is_temp_saved = True

        try:
            # إرسال مسار الفيديو إلى دالة Gemini وجلب التحليل
            analysis_result = analyze_video(video_path)
        finally:
            # تنظيف السيرفر: حذف الملف المؤقت (إذا أنشأناه) لكي لا يملأ مساحة جهازك
            if is_temp_saved and os.path.exists(video_path):
                os.remove(video_path)
        # -------------------------------------

        # رفع الفيديو إلى حسابك في Cloudinary للحفظ الدائم
        uploaded_video = upload(
            video_file,
            resource_type="video"
        )

        # حفظ سجل التحليل الكامل في قاعدة البيانات
        VideoAnalysis.objects.create(
            child=child,
            video=uploaded_video["secure_url"], # رابط الفيديو من Cloudinary
            ai_summary=analysis_result,         # نص التحليل القادم من Gemini
            eye_contact_score=0,                # قيم افتراضية يمكنك تعديلها لاحقاً
            attention_score=0,
            repetitive_behavior_score=0,
            interaction_level_score=0
        )

        # إعادة توجيه المستخدم لنفس الصفحة بعد النجاح لإفراغ الفورم
        return redirect("assessment:upload_video")

    context = {
        "children": children
    }
    return render(request, "assessment/upload_video.html", context)


def questionnaire(request: HttpRequest):
    return render(request, 'assessment/questionnaire.html')

def questionnaire_video(request: HttpRequest):
    return render(request, 'assessment/questionnaire-video.html')


def processing_view(request: HttpRequest):
    return render(request, 'assessment/processing.html')