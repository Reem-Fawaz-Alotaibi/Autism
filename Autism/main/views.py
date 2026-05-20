from django.shortcuts import render,redirect
from django.http import HttpRequest
from chatbot.models import Conversation
from children.models import Child
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def home_page_view(request: HttpRequest):

    conv_id = None
    children = []  

    if request.user.is_authenticated:
        conv, _ = Conversation.objects.get_or_create(user=request.user)
        conv_id = conv.id
        children = Child.objects.filter(user=request.user)

    return render(request, 'main/home.html', {
        "conv_id": conv_id,
        "children": children
    })

def about_us_view(request: HttpRequest):
    return render(request, 'main/about_us.html')


def contact_us_view(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        topic = request.POST.get("topic")
        message = request.POST.get("message")

        full_message = f"""
الاسم: {name}

الإيميل: {email}

الموضوع: {topic}

الرسالة:
{message}
"""

        send_mail(
            subject=f"رسالة جديدة - {topic}",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["reemfawazalotaibi11@gmail.com"],
        )

        messages.success(request, "تم إرسال الرسالة بنجاح ✨")

        return redirect("main:contact_us")

    return render(request, "main/contact_us.html")


def how_it_works_view(request: HttpRequest):
    return render(request, 'main/how_it_works.html')


def privacy_policy_view(request: HttpRequest):
    return render(request, 'main/privacy_policy.html')


def terms_of_service_view(request: HttpRequest):
    return render(request, 'main/terms_of_service.html')


def questions_view(request: HttpRequest):
    return render(request, 'main/questions.html')


# 


def set_theme(request, theme):
    request.session['theme'] = theme  

    next_url = request.GET.get('next')

    if not next_url:
        next_url = request.META.get('HTTP_REFERER', '/')

    return redirect(next_url)


def theme_processor(request):
    return {
        'theme': request.session.get('theme', 'default')
    }
def dashboard_view(request: HttpRequest):
    return render(request, 'main/dashbord_admin.html')

def test_view(request: HttpRequest):
    return render(request, 'main/404.html')

    

