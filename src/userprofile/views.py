from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userprofile.models import Profile
from .forms import ProfilePictureForm
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.

@login_required
def profile_view(request):

    user = request.user #gets user instance that is currently logged in and their details
    profile, _ = Profile.objects.get_or_create(user=user) #gets extra user profile data for profile viewing

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating profile picture. Please try again.')
    else:
        form = ProfilePictureForm(instance=profile)

    #gives the profile.html template context data it can use to populate itself
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': profile.email,
        'phone': profile.tel,
        'address': profile.address,
        'profession': profile.profession,
        'show_navbar': False,
        'form': form
    }
    
    return render(request, 'userprofile/profile.html', context)

#view that serves professions for a given authority body
def get_professions(request):
    body = request.GET.get('body')
    professions = []
    if body == 'HPCSA':
        professions = [
            {'value': 'medical_doctor', 'text': 'Medical Doctor'},
            {'value': 'dentist', 'text': 'Dentist'},
            {'value': 'psychologist', 'text': 'Psychologist'},
            {'value': 'physiotherapist', 'text': 'Physiotherapist'},
            {'value': 'radiographer', 'text': 'Radiographer'},
            {'value': 'occupational_therapist', 'text': 'Occupational Therapist'},
            {'value': 'biokineticist', 'text': 'Biokineticist'},
            {'value': 'clinical_technologist', 'text': 'Clinical Technologist'},
            {'value': 'dietitian', 'text': 'Dietitian'},
            {'value': 'audiologist', 'text': 'Audiologist'},
            {'value': 'optometrist', 'text': 'Optometrist'},
            {'value': 'emergency_care_practitioner', 'text': 'Emergency Care Practitioner'},
        ]
    elif body == 'SANC':
        professions = [
            {'value': 'registered_nurse', 'text': 'Registered Nurse'},
            {'value': 'enrolled_nurse', 'text': 'Enrolled Nurse'},
            {'value': 'nursing_assistant', 'text': 'Nursing Assistant'},
            {'value': 'midwife', 'text': 'Midwife'},
        ]
    return JsonResponse({'professions': professions})