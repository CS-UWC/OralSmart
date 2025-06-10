from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from userprofile.models import Profile

# Create your views here.

@login_required
def profile_view(request):

    user = request.user #gets user instance that is currently logged in and their details
    profile, created = Profile.objects.get_or_create(user=user) #gets extra user profile data for profile viewing

    #gives the profile.html template context data it can use to populate itself
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': profile.email,
        'phone': profile.tel,
        'address': profile.address,
        'profession': profile.profession,
        'show_navbar': False
    }
    
    return render(request, 'userprofile/profile.html', context)