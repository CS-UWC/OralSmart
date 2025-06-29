from django.shortcuts import render, redirect
from .forms import PatientForm
from .models import Patient
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def create_patient_view(request):

    form = PatientForm(request.POST or None)

    if form.is_valid():
        form.save()
        form = PatientForm()

    context = {
        'form': form,
        'show_navbar': True,
    }

    return render(request, "patient/create_patient.html", context)

def patient_detail_view(request):

    obj = Patient.objects.get(id=1) #contains the patient object and all it's variables

    context = {
        'object': obj,
        'show_navbar': True,
    }

    return render(request, "patient/patient_detail.html", context)


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
                parent_contact=parent_contact
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