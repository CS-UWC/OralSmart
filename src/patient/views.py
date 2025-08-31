from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import PatientForm
from .models import Patient
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def create_patient(request):
    if request.method == 'POST':
        try:
            #get form data
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            parent_name = request.POST.get('parent_name')
            parent_surname = request.POST.get('parent_surname')
            parent_id = request.POST.get('parent_id')
            parent_contact = request.POST.get('parent_contact')
            screening_type = request.POST.get('screening_type')
            
            #validate required fields
            if not all([name, surname, gender, age, parent_name, parent_surname, parent_id, parent_contact]):
                messages.error(request, 'All fields are required.')
                return render(request, 'patient/create_patient.html', {'show_navbar': True})
            
            #create new patient
            patient = Patient.objects.create(
                name=name,
                surname=surname,
                gender=gender,
                age=age,
                parent_name=parent_name,
                parent_surname=parent_surname,
                parent_id=parent_id,
                parent_contact=parent_contact,
                created_by=request.user  # Associate with current user
            )
            
            messages.success(request, f'Patient {patient.name} {patient.surname} created successfully!')
            
            #check if screening was requested
            if screening_type:
                if screening_type == 'dental':
                    return redirect('dental_screening', patient_id=patient.id) #type: ignore
                elif screening_type == 'dietary':
                    return redirect('dietary_screening', patient_id=patient.id) #type: ignore
                elif screening_type == 'both':
                    #start with dietary screening, then proceed to dental
                    return redirect(f'/assessments/dietary_screening/{patient.id}/?perform_both=true') #type: ignore
            
            #if no screening, redirect to success page or patient list
            return redirect('create_patient')  # or wherever you want to redirect
            
        except Exception as e:
            messages.error(request, f'Error creating patient: {str(e)}')
            return render(request, 'patient/create_patient.html', {'show_navbar': True})
    
    #if GET request, render the form
    return render(request, 'patient/create_patient.html', {'show_navbar': True})

@login_required
def patient_list_view(request):
    """View to display all patients created by the current user with search functionality"""
    # Get search query from GET parameters
    search_query = request.GET.get('search', '').strip()
    
    # Base queryset - only show patients created by the current user
    patients = Patient.objects.filter(created_by=request.user)
    
    # Apply search filter if search query exists
    if search_query:
        patients = patients.filter(
            Q(name__icontains=search_query) |
            Q(surname__icontains=search_query) |
            Q(parent_id__icontains=search_query) |
            Q(parent_contact__icontains=search_query) #|
            # Q(parent_name__icontains=search_query) |
            # Q(parent_surname__icontains=search_query)
        )
    
    # Order by most recent
    patients = patients.order_by('-id')
    
    # Pagination - 10 patients per page
    paginator = Paginator(patients, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'patients': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'show_navbar': True,
        'total_patients': paginator.count,
    }
    
    return render(request, "patient/patient_list.html", context)