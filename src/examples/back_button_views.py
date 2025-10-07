"""
Example views demonstrating how to use the back button mixins.
These are just examples - you can apply these patterns to your existing views.
"""
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from oralsmart.mixins import BackUrlMixin, NavigationHistoryMixin
from patient.models import Patient


class ExamplePatientDetailView(LoginRequiredMixin, BackUrlMixin, DetailView):
    """
    Example of using BackUrlMixin with a DetailView.
    This will provide a back_url that goes to the patient list by default.
    """
    model = Patient
    template_name = 'patient/detail.html'
    context_object_name = 'patient'
    default_back_url = 'patient_list'  # Fallback to patient list


class ExamplePatientListView(LoginRequiredMixin, NavigationHistoryMixin, ListView):
    """
    Example of using NavigationHistoryMixin with a ListView.
    This tracks navigation history for better back button behavior.
    """
    model = Patient
    template_name = 'patient/list.html'
    context_object_name = 'patients'
    paginate_by = 10


class ExampleDashboardView(LoginRequiredMixin, NavigationHistoryMixin, TemplateView):
    """
    Example of using NavigationHistoryMixin with a TemplateView.
    """
    template_name = 'dashboard.html'


# Example of how to modify an existing function-based view
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from oralsmart.context_processors import get_safe_home_url
from urllib.parse import urlparse


@login_required
def example_function_view(request, patient_id):
    """
    Example function-based view that manually handles back URL.
    Use this pattern if you need custom back URL logic in function views.
    """
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get back URL (similar to what the context processor does)
    referer = request.META.get('HTTP_REFERER')
    back_url = None
    
    if referer:
        try:
            referer_parsed = urlparse(referer)
            request_parsed = urlparse(request.build_absolute_uri())
            
            if referer_parsed.netloc == request_parsed.netloc:
                back_url = referer
        except Exception:
            pass
    
    if not back_url:
        back_url = get_safe_home_url()
    
    context = {
        'patient': patient,
        'back_url': back_url,  # This would be automatic with context processor
        'show_navbar': True,
    }
    
    return render(request, 'patient/detail.html', context)


@login_required
def enhanced_create_patient(request):
    """
    Enhanced version of your create_patient view with better back button handling.
    """
    if request.method == 'POST':
        # Your existing POST logic here...
        # Example: create patient and redirect
        try:
            # Process form data here
            messages.success(request, 'Patient created successfully!')
            return redirect('patient_list')  # or wherever you want to redirect
        except Exception as e:
            messages.error(request, f'Error creating patient: {e}')
            # Fall through to render the form again
    
    # For GET requests or when POST fails, show the form
    context = {
        'show_navbar': True,
        # back_url is automatically available from context processor
    }
    return render(request, 'patient/create_patient.html', context)