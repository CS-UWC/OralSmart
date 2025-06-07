"""oralsmart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from pages.views import home_view, registration_view, patient_view, report_view, hospital_booking_view, confirmation_view, dental_screening_view, dietary_screening_view, my_referrals_view, history_view
from products.views import product_detail_view, product_create_view
from patient.views import create_patient_view, patient_detail_view
from userauth.views import login_user, logout_user

urlpatterns = [
    path('admin/', admin.site.urls),

    path('home/', home_view, name='Home'),
    path('register/', registration_view),
    path('patient/', patient_view, name='patient'),
    path('report/', report_view, name='report'),
    path('hospital/', hospital_booking_view, name='hospital'),
    path('confirmation/', confirmation_view, name='confirmation'),
    path('dental_screen/', dental_screening_view, name='dental'),
    path('dietary_screen/', dietary_screening_view, name='nutritional'),
    path('my_referrals/', my_referrals_view, name='my_referrals'),
    path('history/', history_view, name='history'),
    path('product/', product_detail_view),
    path('create_product/', product_create_view),
    path('create_patient/', create_patient_view),
    path('patient_detail/', patient_detail_view),

    #for userauth
    path('login_user/', login_user, name='Login'),
    path('logout_user/', logout_user, name="Logout"),  # type: ignore

]
