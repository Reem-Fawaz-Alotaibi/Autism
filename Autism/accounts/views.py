from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from community.models import Like, CommentLike

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

        if user is not None:

            login(request, user)

            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)

            return redirect('main:home_page_view')

        else:
            messages.error(request, 'بيانات الدخول خاطئة')

    return render(request, 'accounts/signin.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:signin")

def reset_view(request):
    return render(request, 'accounts/reset-password.html')

def guest_login(request):
    request.session['is_guest'] = True
    return redirect('main:home_page_view')

@login_required
def profile(request):
    total_liked_posts = Like.objects.filter(user=request.user).count()
    total_liked_comments = CommentLike.objects.filter(user=request.user).count()
    total_likes_count = total_liked_posts + total_liked_comments

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    return render(request, "accounts/profile.html", {
        "profile": profile,
        'total_likes_count': total_likes_count,
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
    return render(request, 'accounts/saved_centers.html')


