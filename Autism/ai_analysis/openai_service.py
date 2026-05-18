from openai import OpenAI
from django.conf import settings
from .models import Activity, ResourceVideo, SkillCategory

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_recommendations(video_analysis: str, questionnaire_answers: dict, child_age: int):
    """
    تاخذ نتيجة تحليل الفيديو + إجابات الأسئلة
    وترجع أنشطة وفيديوهات مناسبة للطفل
    """

    # 1️⃣ نبني الـ prompt لـ OpenAI
    prompt = f"""
    أنت متخصص في تقييم أطفال التوحد.
    بناءً على المعلومات التالية، حدد التصنيفات التي يحتاج الطفل للتحسين فيها.

    ** عمر الطفل:** {child_age} سنوات

    ** نتيجة تحليل الفيديو:**
    {video_analysis}

    ** إجابات تقييم الأسئلة:**
    {questionnaire_answers}

    ** التصنيفات المتاحة:**
    - focus: التركيز والانتباه
    - eye_contact: التواصل البصري
    - social: التفاعل الاجتماعي
    - communication: التواصل اللغوي
    - motor: المهارات الحركية
    - behavior: السلوك والتصرفات

    رجّع فقط قائمة JSON بالتصنيفات الأكثر أهمية للطفل مرتبة من الأعلى أولوية.
    مثال: ["focus", "eye_contact", "communication"]
    لا تضيف أي نص خارج الـ JSON.
    """

    # 2️⃣ نرسل لـ OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    # 3️⃣ نحلل الرد
    import json
    raw = response.choices[0].message.content.strip()
    categories = json.loads(raw)

    # 4️⃣ نتأكد إن التصنيفات صحيحة
    valid_categories = [c for c in categories if c in SkillCategory.values]

    # 5️⃣ نجيب الأنشطة والفيديوهات من DB
    activities = Activity.objects.filter(
        category__in=valid_categories,
        age_min__lte=child_age,
        age_max__gte=child_age,
        is_active=True
    )[:6]  # أقصى 6 أنشطة

    videos = ResourceVideo.objects.filter(
        category__in=valid_categories,
        age_min__lte=child_age,
        age_max__gte=child_age,
        is_active=True
    )[:4]  # أقصى 4 فيديوهات

    return {
        "categories": valid_categories,
        "activities": activities,
        "videos": videos
    }