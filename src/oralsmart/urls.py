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
from django.urls import path
from pages.views import home_view, login_view, registration_view, patient_view, report_view, hospital_booking_view, confirmation_view, dental_screening_view, dietary_screening_view, my_referrals_view, history_view


urlpatterns = [
    path('admin/', admin.site.urls),

    path('home/', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', registration_view),
    path('patient/', patient_view, name='patient'),
    path('report/', report_view, name='report'),
    path('hospital/', hospital_booking_view, name='hospital'),
    path('confirmation/', confirmation_view, name='confirmation'),
    path('dental_screen/', dental_screening_view, name='dental'),
    path('dietary_screen/', dietary_screening_view, name='nutritional'),
    path('my_referrals/', my_referrals_view, name='my_referrals'),
    path('history/', history_view, name='history'),

]
