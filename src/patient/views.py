from django.shortcuts import render

from .forms import PatientForm

from .models import Patient

# Create your views here.

def create_patient_view(request):

    form = PatientForm(request.POST or None)

    if form.is_valid():
        form.save()
        form = PatientForm()

    context = {
        'form': form
    }

    return render(request, "patient/create_patient.html", context)

def patient_detail_view(request):

    obj = Patient.objects.get(id=1) #has the object with all it's attributes/variables

    context = {
        'object': obj
    }

    return render(request, "patient/patient_detail.html", context)