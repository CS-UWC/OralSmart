from django import forms
from .models import DentalScreening, DietaryScreening

class DentalScreeningForm(forms.ModelForm):
    class Meta:
        model = DentalScreening
        fields = '__all__'

class DietaryScreeningForm(forms.ModelForm):
    class Meta:
        model = DietaryScreening
        fields = [
            'sweet_sugary_foods', 'sweet_sugary_foods_daily', 'sweet_sugary_foods_weekly',
            'cold_drinks_juices', 'cold_drinks_juices_daily', 'cold_drinks_juices_weekly',
            'takeaways_processed_foods', 'takeaways_processed_foods_daily', 'takeaways_processed_foods_weekly',
            'salty_snacks', 'salty_snacks_daily', 'salty_snacks_weekly',
            'spreads', 'spreads_daily', 'spreads_weekly'
        ]
        widgets = {
            'sweet_sugary_foods': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'cold_drinks_juices': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'takeaways_processed_foods': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'salty_snacks': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'spreads': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
        }