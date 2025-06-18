from django import forms
from .models import DentalScreening

class DentalScreeningForm(forms.ModelForm):
    class Meta:
        model = DentalScreening
        fields = '__all__'