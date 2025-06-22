from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from userprofile.models import Profile
from django.db import transaction

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .tokens import account_activation_token
from .decorators import user_not_authenticated
from django.contrib.sites.shortcuts import get_current_site

from .forms import CustomSetPasswordForm, CustomPasswordResetForm
from django.contrib.auth.tokens import default_token_generator

# Create your views here.

#For login and logout
@user_not_authenticated
def login_user(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:

            print("Login succesful")
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')

            if next_url:

                return redirect(next_url)
            
            return redirect('create_patient') #redirects to patient page
        else:
            print("Login unsuccessful")

            return render(
                request,
                'authentication/login.html',
                {
                    'error': 'Invalid username or password'
                }
            )
    else:
        return render(request, 'authentication/login.html', {})
    
@login_required
def logout_user(request: HttpRequest)->HttpResponse:

    if request.method == "POST":

        try:
            logout(request)
            messages.success(request, 'You have been successfully logged out.')
            print('logout successful')

        except Exception as e:
            print(f'Logout error: {e}')
            messages.error(request, 'An error occurred during logout. Please try again.')

        return redirect('login')
    
    else:

        print('logout unsuccessful')
        messages.success(request, 'Log out was unsuccessful.')
        return redirect('login')

def activate(request, uidb64, token):

    User = get_user_model()
    try:

        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has successfully been activated!")
        return redirect('create_patient')
    
    else:

        messages.success(request, "Activation link is invalid!")
        return redirect('login')

def activateEmail(request, user, to_email):

    mail_subject = 'Activate Your OralSmart Account'
    message = render_to_string('authentication/activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[to_email])

    if email.send():

        messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on \
                        received activation link to confirm and complete the registration process.')
        
    else:
        messages.error(request, f'There was a problem sending the email to {to_email},  check to see if the email you entered was correct.')

@user_not_authenticated
def register_user(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            try:
                with transaction.atomic(): #this will avoid partial save if something fails 
                    user = form.save(commit=False)
                    user.is_active=False

                    user.first_name = request.POST.get('name', '')
                    user.last_name = request.POST.get('surname', '')
                    user.email = request.POST.get('email', '')
                    user.save()
                    activateEmail(request, user, request.POST.get('email'))

                    profession = request.POST.get('profession', '')
                    health_professional_body = request.POST.get('health_professional_body', '')
                    reg_num = request.POST.get('reg_num', '')

                    Profile.objects.create(
                        user=user, 
                        profession=profession, 
                        health_professional_body=health_professional_body, 
                        reg_num=reg_num,
                        email=user.email
                    )
                return redirect('create_patient') #logs user in and redirects the user to the create patient page.
            
            except  Exception as e:
                print(f"Registration error {e}") #prints on the terminal

        else:
            messages.error(request, "There are some errors.")

    else:

        form = UserCreationForm()

    return render(request, 'authentication/register_user.html', {
        'form': form,
    })

@login_required
def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = CustomPasswordResetForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully updated!")
            return redirect('login')
        else:
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, str(error))
    else:
        form = CustomSetPasswordForm(user)
    return render(request, 'authentication/reset_password_confirm.html', {
        'form': form,
        'show_navbar': True,
        })

@user_not_authenticated
def req_password_reset(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='authentication/template_reset_password.html'
            )
            messages.success(request, "Password reset email sent.")
            return redirect('login')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'authentication/reset_password.html', {'form': form})

def confirm_password_reset(request, uidb64, token):
    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may log in now.")
                return redirect('login')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'authentication/reset_password_confirm.html', {'form': form})
    else:
        messages.error(request, "The password reset link is invalid, possibly because it has already been used. Please request a new password reset.")
        return redirect('reset_password')