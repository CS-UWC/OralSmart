from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from userprofile.models import Profile

# Create your views here.


#For login and logout
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

        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        print('logout successful')

        return redirect('login')
    else:

        print('logout unsuccessful')
        messages.success(request, 'Log out was unsuccessful.')

        return redirect('login')


def register_user(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()
            user.first_name = request.POST.get('name', '')
            user.last_name = request.POST.get('surname', '')
            user.email = request.POST.get('email', '')
            user.save()
            id_number = request.POST.get('id_number', '')
            profession = request.POST.get('profession', '')
            Profile.objects.create(user=user, id_number=id_number, profession=profession)
            login(request, user)

            return redirect('create_patient')
    else:
        form = UserCreationForm()

    return render(request, 'authentication/register_user.html', {
        'form': form,
    })