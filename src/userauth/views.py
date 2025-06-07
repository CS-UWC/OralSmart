from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def login_user(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            print("Login succesful")
            login(request, user)
            return redirect('patient/') #redirects to patient page
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
    

def logout_user(request):

    if request.method == "POST":

        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        print('logout successful')

        return redirect('Home')
    else:
        print('logout unsuccessful')

