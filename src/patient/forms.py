from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):

    class Meta:

        model = Patient
        fields = [
            'name',
            'surname',
            'age',
            'parent_id',
            'parent_contact',
        ]