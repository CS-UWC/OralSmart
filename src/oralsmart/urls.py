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
from pages.views import home_view, patient_view
from products.views import product_detail_view, product_create_view, dynamic_product_view
from patient.views import create_patient_view, patient_detail_view, create_patient
from userauth.views import login_user, logout_user,register_user
from userprofile.views import profile_view

urlpatterns = [
    path('admin/', admin.site.urls),

    path('home/', home_view, name='home'),

    #for product
    path('product/', product_detail_view),
    path('create_product/', product_create_view),
    path('product/<int:id>/', dynamic_product_view, name='product'),

    #for patient
    #path('create_patient/', create_patient_view),
    path('patient_detail/', patient_detail_view),
    path('patient/', patient_view, name='patient'),
    path('create_patient/', create_patient, name='create_patient'),
    

    #for userauth
    path('login_user/', login_user, name='login'),
    path('logout_user/', logout_user, name='logout'),
    path('register_user/', register_user, name='register_user'),

    #for profile
    path('profile_view/', profile_view, name='profile')

]
