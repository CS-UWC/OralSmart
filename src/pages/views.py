from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

############################MAIN PAGES##############################

def home_view(request, *args, **kwargs): # *args **kwargs

    print(request)
    print("The current user is :", request.user)

    #return HttpResponse("<h1>Hello World</h1>") #String of HTML Code

    return render(request, "home.html", {})

def login_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "login.html", {})

def registration_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "registration.html", {})

def patient_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "patient.html", {})

def report_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "report.html", {})

def hospital_booking_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "hospital.html", {})

def confirmation_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "confirmation.html", {})

#####################SCREENING PAGES#######################

def dental_screening_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "dental.html", {})

def dietary_screening_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "nutritional.html", {})

#######################SIDE PAGES#########################

def my_referrals_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "my_referrals.html", {})

def history_view(request, *args, **kwargs): # *args **kwargs

    return render(request, "history.html", {})