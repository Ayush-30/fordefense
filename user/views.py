from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, auth
from django.contrib.auth.views import login_required
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login

from Forum.models import QuestionPost
from .form import Userupdateform, Userprofileupdate
from .models import Profile
from GeekHubFinal import settings
from .tokens import account_activation_token


# Create your views here.


# Dashboard
def base(request):
    if request.user.is_authenticated:
        user_name = request.user
        p = Profile.objects.get(user=user_name)
        if p.email_confirmed:
            user = request.user
            user_sem = Profile.objects.get(user=user)
            questions = QuestionPost.objects.filter(question_author_semester=user_sem.semester)
            context = {'questions': questions}
            return render(request, 'forum/dashboard.html', context)
        else:
            return render(request, 'user/email_not_verified.html')
    else:
        return render(request, 'user/open_page.html')


# Login Page
def loginpage(request):
    if request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['psw']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('forum')
        else:
            messages.info(request, 'Invalid Username or Password. Please Try Again.')
            return redirect('login')

    else:
        return render(request, 'user/login.html')


# Register
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        profile_form = Userprofileupdate(request.POST)
        # special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'user already taken')
                return redirect('register')
            elif username == password1:
                messages.info(request, '++++++.[[[[[.....')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'email taken ......')
                return redirect('register')
            elif len(password1) < 6:
                messages.info(request, 'length must be greater than 6......')
                return redirect('register')
            elif not any(char.isdigit() for char in password1):
                messages.info(request, 'password too weak,use letter too ......')
                return redirect('register')
            elif not any(char.isalpha() for char in password1):
                messages.info(request, 'password too weak,use digit too .....')
                return redirect('register')
            # elif not any(char in special_characters for char in password1):
            #     messages.info(request, 'use a special character ......')
            #     return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                if profile_form.is_valid():
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    current_site = get_current_site(request)
                    message = render_to_string('user/account_activation_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
                        'token': account_activation_token.make_token(user),
                    })
                    subject = 'Activate your GeekHub account.'
                    from_email = settings.EMAIL_HOST_USER
                    to_email = email
                    send_mail(
                        subject,
                        message,
                        from_email,
                        [to_email],
                        fail_silently=False,
                    )
                    # messages.success(request, ('Please Confirm your email to complete registration.'))
                    return render(request, 'user/email_check_request.html')
        else:
            messages.info(request, 'Passwords did not match...')
            return redirect('register')
    else:
        profile_form = Userprofileupdate()
        args = {'profile_form': profile_form}
        return render(request, 'user/register.html', args)

# def register(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password1 = request.POST['password1']
#         password2 = request.POST['password2']
#         profile_form = Userprofileupdate(request.POST)
#         # special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
#         if password1 == password2:
#             if User.objects.filter(username=username).exists():
#                 messages.info(request, 'user already taken')
#                 return redirect('register')
#             elif username == password1:
#                 messages.info(request, '++++++.[[[[[.....')
#                 return redirect('register')
#             elif User.objects.filter(email=email).exists():
#                 messages.info(request, 'email taken ......')
#                 return redirect('register')
#             elif len(password1) < 6:
#                 messages.info(request, 'length must be greater than 6......')
#                 return redirect('register')
#             elif not any(char.isdigit() for char in password1):
#                 messages.info(request, 'password too weak,use letter too ......')
#                 return redirect('register')
#             elif not any(char.isalpha() for char in password1):
#                 messages.info(request, 'password too weak,use digit too .....')
#                 return redirect('register')
#             # elif not any(char in special_characters for char in password1):
#             #     messages.info(request, 'use a special character ......')
#             #     return redirect('register')
#             else:
#                 user = User.objects.create_user(username=username, email=email, password=password1)
#                 user.save()
#                 if profile_form.is_valid():
#                     profile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.save()
#                     current_site = get_current_site(request)
#                     message = render_to_string('user/account_activation_email.html', {
#                         'user': user,
#                         'domain': current_site.domain,
#                         'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
#                         'token': account_activation_token.make_token(user),
#                     })
#                     subject = 'Activate your GeekHub account.'
#                     from_email = settings.EMAIL_HOST_USER
#                     to_email = email
#                     send_mail(
#                         subject,
#                         message,
#                         from_email,
#                         [to_email],
#                         fail_silently=False,
#                     )
#                     # messages.success(request, ('Please Confirm your email to complete registration.'))
#                     return render(request, 'user/email_check_request.html')
#         else:
#             messages.info(request, 'Passwords did not match...')
#             return redirect('register')
#     else:
#         profile_form = Userprofileupdate()
#         return render(request, 'user/register.html', {'profile_form': profile_form})
#

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        u = request.user
        p = Profile.objects.get(user=u)
        p.email_confirmed = True
        p.save()
        messages.success(request, 'Thank you for your email confirmation.')
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid!')


def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def editprofile(request):
    if request.method == 'POST':
        u_form = Userupdateform(request.POST, instance=request.user)
        p_form = Userprofileupdate(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'your profile is updated')
            return redirect('profile')
    else:
        u_form = Userupdateform(instance=request.user)
        p_form = Userprofileupdate(instance=request.user.profile)

    content = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'user/editprofile.html', content)


@login_required
def profile(request):
    u_form = Userupdateform(instance=request.user)

    content = {
        'u_form': u_form,
    }
    return render(request, 'user/profile.html', content)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('forum')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/password_change.html', {
        'form': form
    })
