from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout,update_session_auth_hash
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from community.models import Like, CommentLike,Post
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from support_map.models import PlaceLike

def signup_view(request):
    form = SignUpForm(request.POST or None)

    if request.method == 'POST':
        print(form.errors)

        if form.is_valid():

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'اسم المستخدم مستخدم مسبقًا')
                return render(request, 'accounts/signup.html', {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'البريد الإلكتروني مستخدم مسبقًا')
                return render(request, 'accounts/signup.html', {'form': form})

            User.objects.create_user(
                username=username,
                email=email,
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            messages.success(request, 'تم إنشاء الحساب بنجاح')
            return redirect('accounts:signin')

    return render(request, 'accounts/signup.html', {'form': form})


def signin_view(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'يرجى تعبئة جميع الحقول')
            return render(request, 'accounts/signin.html')

        user = authenticate(
            request,
            username=username,
            password=password
        )
        print("user:", user)

        if user is not None:
            login(request, user)
            request.session.pop('is_guest', None)
            request.session.pop('guest_name', None)
            if request.POST.get('remember_me'):
                request.session.set_expiry(None) 
            else:
                request.session.set_expiry(0)

            return redirect('main:home_page_view')

        else:
            messages.error(request, 'بيانات الدخول خاطئة')
            return render(request, 'accounts/signin.html')



    return render(request, 'accounts/signin.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:signin")

def reset_view(request):
    return render(request, 'accounts/reset-password.html')

def guest_login(request):
    request.session['is_guest'] = True
    request.session['guest_name'] = "زائر"
    return redirect('main:home_page_view')

@login_required
def profile(request):
    total_liked_posts = Like.objects.filter(user=request.user).count()
    total_liked_comments = CommentLike.objects.filter(user=request.user).count()
    total_likes_count = total_liked_posts + total_liked_comments
    posts_count = Post.objects.filter(user=request.user).count()

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    return render(request, "accounts/profile.html", {
        "profile": profile,
        'total_likes_count': total_likes_count,
        'posts_count': posts_count,
    })

@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        user = request.user
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        profile.phone = request.POST.get("phone")
        profile.city = request.POST.get("city")
        profile.save()

        messages.success(request, "تم حفظ التعديلات بنجاح")

        return redirect("accounts:profile")

    return render(request, "accounts/edit-profile.html", {
        "profile": profile
    })


def settings_view(request):
    return render(request, 'accounts/settings.html')


def saved_centers_view(request):
    saved_centers = PlaceLike.objects.filter(user=request.user).select_related('place')

    return render(request, 'accounts/saved_centers.html',{
        'saved_centers': saved_centers
    })


@login_required
def update_email(request):

    if request.method == "POST":

        new_email = request.POST.get("email", "").strip()

        user = request.user

        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "البريد الإلكتروني مستخدم مسبقًا")
            return redirect("accounts:settings")

        old_email = user.email

        user.email = new_email
        user.save()

        send_mail(
            subject='تم تغيير البريد الإلكتروني',
            message=f'''
                مرحبًا {user.username}

                تم تحديث البريد الإلكتروني لحسابك بنجاح.

                البريد الجديد:
                {new_email}

                إذا لم تقم بهذا التغيير يرجى التواصل معنا فورًا.
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
            fail_silently=False,
        )

        messages.success(request, "تم تحديث البريد الإلكتروني بنجاح")

        return redirect("accounts:settings")

    return redirect("accounts:settings")


@login_required
def update_password(request):
    if request.method == "POST":
        user = request.user

        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not user.check_password(old_password):
            messages.error(request, "كلمة المرور الحالية غير صحيحة")
            return redirect("accounts:settings")

        if new_password != confirm_password:
            messages.error(request, "كلمات المرور غير متطابقة")
            return redirect("accounts:settings")

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        messages.success(request, "تم تغيير كلمة المرور بنجاح")
        return redirect("accounts:settings")

    return redirect("accounts:settings")


@login_required
def logout_all_devices(request):

    sessions = Session.objects.filter(
        expire_date__gte=timezone.now()
    )

    for session in sessions:

        data = session.get_decoded()

        if data.get('_auth_user_id') == str(request.user.id):
            session.delete()

    logout(request)

    messages.success(
        request,
        "تم تسجيل الخروج من جميع الأجهزة"
    )

    return redirect("accounts:signin")



@login_required
def delete_account(request):

    if request.method == "POST":

        user = request.user

        logout(request)

        user.delete()

        messages.success(
            request,
            "تم حذف الحساب نهائيًا"
        )

        return redirect("main:home_page_view")

    return redirect("accounts:settings")