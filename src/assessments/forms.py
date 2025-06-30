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
            # Sweet/Sugary Foods
            'sweet_sugary_foods', 'sweet_sugary_foods_daily', 'sweet_sugary_foods_weekly',
            'sweet_sugary_foods_timing', 'sweet_sugary_foods_bedtime',
            
            # Take-aways and Processed Foods
            'takeaways_processed_foods', 'takeaways_processed_foods_daily', 'takeaways_processed_foods_weekly',
            
            # Fresh Fruit
            'fresh_fruit', 'fresh_fruit_daily', 'fresh_fruit_weekly',
            'fresh_fruit_timing', 'fresh_fruit_bedtime',
            
            # Cold Drinks, Juices and Flavoured Water and Milk
            'cold_drinks_juices', 'cold_drinks_juices_daily', 'cold_drinks_juices_weekly',
            'cold_drinks_juices_timing', 'cold_drinks_juices_bedtime',
            
            # Processed Fruit
            'processed_fruit', 'processed_fruit_daily', 'processed_fruit_weekly',
            'processed_fruit_timing', 'processed_fruit_bedtime',
            
            # Spreads
            'spreads', 'spreads_daily', 'spreads_weekly',
            'spreads_timing', 'spreads_bedtime',
            
            # Added Sugars
            'added_sugars', 'added_sugars_daily', 'added_sugars_weekly',
            'added_sugars_timing', 'added_sugars_bedtime',
            
            # Salty Snacks
            'salty_snacks', 'salty_snacks_daily', 'salty_snacks_weekly',
            'salty_snacks_timing',
            
            # Dairy Products
            'dairy_products', 'dairy_products_daily', 'dairy_products_weekly',
            
            # Vegetables
            'vegetables', 'vegetables_daily', 'vegetables_weekly',
            
            # Water
            'water', 'water_timing', 'water_glasses',
            
            # Xylitol Products
            'xylitol_products', 'xylitol_products_daily', 'xylitol_products_weekly'
        ]
        widgets = {
            'sweet_sugary_foods': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'takeaways_processed_foods': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'fresh_fruit': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'cold_drinks_juices': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'processed_fruit': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'spreads': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'added_sugars': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'salty_snacks': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'dairy_products': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'vegetables': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'water': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
            'xylitol_products': forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
        }