from django.db import models

from patient.models import Patient

# Create your models here.


class DentalScreening(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='screenings')

    caregiver_treatment = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    income = models.CharField(max_length=20)
    sugar_meals = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    sugar_snacks = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    sugar_beverages = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    sa_citizen = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    special_needs = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    plaque = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    dry_mouth = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    enamel_defects = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    appliance = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    fluoride_water = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    fluoride_toothpaste = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    topical_fluoride = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    regular_checkups = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    sealed_pits = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    restorative_procedures = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    enamel_change = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    dentin_discoloration = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    white_spot_lesions = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    cavitated_lesions = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    multiple_restorations = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    missing_teeth = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    
    teeth_data = models.JSONField()  #stores all tooth values as a dict

    created_at = models.DateTimeField(auto_now_add=True)

class DietaryScreening(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dietary_screenings')

    # Section 1: Sweet/Sugary Foods
    sweet_sugary_foods = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    sweet_sugary_foods_daily = models.CharField(max_length=20, blank=True, null=True)
    sweet_sugary_foods_weekly = models.CharField(max_length=20, blank=True, null=True)
    sweet_sugary_foods_timing = models.CharField(max_length=20, blank=True, null=True)
    sweet_sugary_foods_bedtime = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True)

    # Section 2: Take-aways and Processed Foods
    takeaways_processed_foods = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    takeaways_processed_foods_daily = models.CharField(max_length=20, blank=True, null=True)
    takeaways_processed_foods_weekly = models.CharField(max_length=20, blank=True, null=True)

    # Section 3: Fresh Fruit
    fresh_fruit = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    fresh_fruit_daily = models.CharField(max_length=20, blank=True, null=True)
    fresh_fruit_weekly = models.CharField(max_length=20, blank=True, null=True)
    fresh_fruit_timing = models.CharField(max_length=20, blank=True, null=True)
    fresh_fruit_bedtime = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True)

    # Section 4: Cold Drinks, Juices and Flavoured Water and Milk
    cold_drinks_juices = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    cold_drinks_juices_daily = models.CharField(max_length=20, blank=True, null=True)
    cold_drinks_juices_weekly = models.CharField(max_length=20, blank=True, null=True)
    cold_drinks_juices_timing = models.CharField(max_length=20, blank=True, null=True)
    cold_drinks_juices_bedtime = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True)

    # Section 5: Processed Fruit
    processed_fruit = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    processed_fruit_daily = models.CharField(max_length=20, blank=True, null=True)
    processed_fruit_weekly = models.CharField(max_length=20, blank=True, null=True)
    processed_fruit_timing = models.CharField(max_length=20, blank=True, null=True)
    processed_fruit_bedtime = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True)

    # Section 6: Spreads
    spreads = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    spreads_daily = models.CharField(max_length=20, blank=True, null=True)
    spreads_weekly = models.CharField(max_length=20, blank=True, null=True)
    spreads_timing = models.CharField(max_length=20, blank=True, null=True)
    spreads_bedtime = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True)

    # Section 7: Added Sugars
    added_sugars = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    added_sugars_daily = models.CharField(max_length=20, blank=True, null=True)
    added_sugars_weekly = models.CharField(max_length=20, blank=True, null=True)
    added_sugars_timing = models.CharField(max_length=20, blank=True, null=True)
    added_sugars_bedtime = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True)

    # Section 8: Salty Snacks
    salty_snacks = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    salty_snacks_daily = models.CharField(max_length=20, blank=True, null=True)
    salty_snacks_weekly = models.CharField(max_length=20, blank=True, null=True)
    salty_snacks_timing = models.CharField(max_length=20, blank=True, null=True)

    # Section 9: Dairy Products
    dairy_products = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    dairy_products_daily = models.CharField(max_length=20, blank=True, null=True)
    dairy_products_weekly = models.CharField(max_length=20, blank=True, null=True)

    # Section 10: Vegetables
    vegetables = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    vegetables_daily = models.CharField(max_length=20, blank=True, null=True)
    vegetables_weekly = models.CharField(max_length=20, blank=True, null=True)

    # Section 11: Water
    water = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    water_timing = models.CharField(max_length=50, blank=True, null=True)
    water_glasses = models.CharField(max_length=20, blank=True, null=True)

    # Section 12: Xylitol-containing Products
    xylitol_products = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    xylitol_products_daily = models.CharField(max_length=20, blank=True, null=True)
    xylitol_products_weekly = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)