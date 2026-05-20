from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.staticfiles import finders

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from children.models import Child
from ai_analysis.models import VideoAnalysis

from arabic_reshaper import reshape
from bidi.algorithm import get_display

import os
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


def main_plan_view(request: HttpRequest):
    return render(request, 'plans/main_plan.html')


def support_plan_view(request: HttpRequest):
    return render(request, 'plans/support_plan.html')

<<<<<<< HEAD

@login_required
def download_report(request, child_id):

    child = get_object_or_404(
        Child,
        id=child_id,
        user=request.user
    )

    analysis = VideoAnalysis.objects.filter(child=child).last()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{child.name}_report.pdf"'

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

    # =========================
    # الرسم البياني
    # =========================
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

    # =========================
    # PDF START
    # =========================

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # =========================
    # 🔵 BACKGROUND (خفيف)
    # =========================
    p.setFillColor(colors.whitesmoke)
    p.rect(0, 0, width, height, fill=1)

    # =========================
    # 🔷 HEADER BAR
    # =========================
    p.setFillColor(colors.HexColor("#4F46E5"))
    p.rect(0, height - 70, width, 70, fill=1)

    p.setFillColor(colors.white)
    p.setFont("Arabic", 18)
    p.drawRightString(width - 30, height - 45, ar("تقرير تحليل الطفل"))

    # =========================
    # 🧾 CARD BOX
    # =========================
    p.setFillColor(colors.white)
    p.setStrokeColor(colors.lightgrey)
    p.roundRect(30, 120, width - 60, height - 220, 15, fill=1, stroke=1)

    # =========================
    # 👶 بيانات الطفل
    # =========================
    y = height - 140
    p.setFillColor(colors.black)
    p.setFont("Arabic", 13)

    p.drawRightString(width - 50, y, ar(f"اسم الطفل: {child.name}")); y -= 25

    gender = "ذكر" if child.gender == "male" else "أنثى"
    p.drawRightString(width - 50, y, ar(f"الجنس: {gender}")); y -= 25

    communication = "لفظي" if child.communication_type == "verbal" else "غير لفظي"
    p.drawRightString(width - 50, y, ar(f"التواصل: {communication}")); y -= 25

    sensory_map = {
        "sound": "الصوت",
        "touch": "اللمس",
        "light": "الضوء",
        "none": "لا توجد"
    }

    sensory = sensory_map.get(child.sensory_sensitivities, "غير محدد")
    p.drawRightString(width - 50, y, ar(f"الحساسية: {sensory}"))

    # =========================
    # 📊 Chart
    # =========================
    if analysis and chart_image:
        p.drawImage(
            chart_image,
            50,
            220,
            width=250,
            height=150
        )

    # =========================
    # 📈 SCORES
    # =========================
    if analysis:
        p.setFont("Arabic", 12)

        p.drawRightString(width - 50, 250, ar(f"التواصل البصري: {analysis.eye_contact_score}"))
        p.drawRightString(width - 50, 230, ar(f"الانتباه: {analysis.attention_score}"))
        p.drawRightString(width - 50, 210, ar(f"التكرار: {analysis.repetitive_behavior_score}"))
        p.drawRightString(width - 50, 190, ar(f"التفاعل: {analysis.interaction_level_score}"))

    # =========================
    # 📝 SUMMARY BOX
    # =========================
    if analysis:
        p.setFont("Arabic", 14)
        p.drawRightString(width - 50, 150, ar("ملخص التحليل"))

        text = p.beginText(width - 50, 130)
        text.setFont("Arabic", 11)

        for line in (analysis.ai_summary or "").splitlines():
            text.textLine(ar(line))

        p.drawText(text)

    p.showPage()
    p.save()

    return response
=======
def video_plan_view(request:HttpRequest):

    return render(request, 'plans/video_plan.html')

def support_strategies_view(request:HttpRequest):

    return render(request, 'plans/support_strategies.html')

>>>>>>> b21ece247883f99f30ea46b301ad5c3ed4bd9485
