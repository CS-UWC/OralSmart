from django.shortcuts import render, redirect
from django.contrib import messages
from patient.models import Patient
from .models import DentalScreening, DietaryScreening

# Create your views here.

def dental_screening(request, patient_id):

    patient = Patient.objects.get(pk=patient_id)
    
    #check if this comes from dietary screening
    from_dietary = request.GET.get('from_dietary', 'false') == 'true'

    permanent_upper = ["18", "17", "16", "15", "14", "13", "12", "11", "21", "22", "23", "24", "25", "26", "27", "28"]
    permanent_lower = ["48", "47", "46", "45", "44", "43", "42", "41", "31", "32", "33", "34", "35", "36", "37", "38"]
    primary_upper = ["55", "54", "53", "52", "51", "61", "62", "63", "64", "65"]
    primary_lower = ["85", "84", "83", "82", "81", "71", "72", "73", "74", "75"]

    required_fields = [
        'caregiver_treatment', 'income', 'sugar_meals', 'sugar_snacks', 'sugar_beverages',
        'sa_citizen', 'special_needs', 'plaque', 'dry_mouth', 'enamel_defects', 'appliance',
        'fluoride_water', 'fluoride_toothpaste', 'topical_fluoride', 'regular_checkups',
        'sealed_pits', 'restorative_procedures', 'enamel_change', 'dentin_discoloration',
        'white_spot_lesions', 'cavitated_lesions', 'multiple_restorations', 'missing_teeth'
    ]
    
    if request.method == 'POST':

        try:

            missing = [field for field in required_fields if not request.POST.get(field)]
            if missing:
                #show error and re-render form
                messages.error(request, f"Please answer all required questions: {', '.join(missing)}")
                return render(request, 'assessments/dental_screening.html', {
                    'permanent_upper': permanent_upper,
                    'permanent_lower': permanent_lower,
                    'primary_upper': primary_upper,
                    'primary_lower': primary_lower,
                    'from_dietary': from_dietary,
                })

            teeth_fields = {}

            for tooth in permanent_upper + permanent_lower + primary_upper + primary_lower:

                key = f"tooth_{tooth}"
                teeth_fields[key] = request.POST.get(key, "")

            #collect other fields

            screening, created = DentalScreening.objects.get_or_create(
                patient=patient,
                defaults={
                'caregiver_treatment': request.POST.get('caregiver_treatment', ''),
                'income': request.POST.get('income', ''),
                'sugar_meals': request.POST.get('sugar_meals', ''),
                'sugar_snacks': request.POST.get('sugar_snacks', ''),
                'sugar_beverages': request.POST.get('sugar_beverages', ''),
                'sa_citizen': request.POST.get('sa_citizen', ''),
                'special_needs': request.POST.get('special_needs', ''),
                'plaque': request.POST.get('plaque', ''),
                'dry_mouth': request.POST.get('dry_mouth', ''),
                'enamel_defects': request.POST.get('enamel_defects', ''),
                'appliance': request.POST.get('appliance', ''),
                'fluoride_water': request.POST.get('fluoride_water', ''),
                'fluoride_toothpaste': request.POST.get('fluoride_toothpaste', ''),
                'topical_fluoride': request.POST.get('topical_fluoride', ''),
                'regular_checkups': request.POST.get('regular_checkups', ''),
                'sealed_pits': request.POST.get('sealed_pits', ''),
                'restorative_procedures': request.POST.get('restorative_procedures', ''),
                'enamel_change': request.POST.get('enamel_change', ''),
                'dentin_discoloration': request.POST.get('dentin_discoloration', ''),
                'white_spot_lesions': request.POST.get('white_spot_lesions', ''),
                'cavitated_lesions': request.POST.get('cavitated_lesions', ''),
                'multiple_restorations': request.POST.get('multiple_restorations', ''),
                'missing_teeth': request.POST.get('missing_teeth', ''),
                'teeth_data': teeth_fields,
            }
            )
            
            if not created:

                fields = [
                    'caregiver_treatment', 'income', 'sugar_meals', 'sugar_snacks', 'sugar_beverages',
                    'sa_citizen', 'special_needs', 'plaque', 'dry_mouth', 'enamel_defects', 'appliance',
                    'fluoride_water', 'fluoride_toothpaste', 'topical_fluoride', 'regular_checkups',
                    'sealed_pits', 'restorative_procedures', 'enamel_change', 'dentin_discoloration',
                    'white_spot_lesions', 'cavitated_lesions', 'multiple_restorations', 'missing_teeth'
                ]

                for field in fields:
                    setattr(screening, field, request.POST.get(field, ''))
                screening.teeth_data = teeth_fields
                screening.save()

            if from_dietary:
                messages.success(request, "Both dietary and dental screenings completed successfully!")
            else:
                messages.success(request, "Dental screening completed successfully!")
                
            return redirect('report', patient_id=patient_id)  #redirects to report page and sends patient_id for identification

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'assessments/dental_screening.html', {
        'permanent_upper': permanent_upper,
        'permanent_lower': permanent_lower,
        'primary_upper': primary_upper,
        'primary_lower': primary_lower,
        'from_dietary': from_dietary,
    })

def dietary_screening(request, patient_id):
    patient = Patient.objects.get(pk=patient_id)
    
    #check if this is part of a combined screening
    perform_both = request.GET.get('perform_both', 'false') == 'true'

    required_fields = [
        'sweet_sugary_foods', 'sweet_sugary_foods_daily', 'sweet_sugary_foods_weekly',
        'cold_drinks_juices', 'cold_drinks_juices_daily', 'cold_drinks_juices_weekly',
        'takeaways_processed_foods', 'takeaways_processed_foods_daily', 'takeaways_processed_foods_weekly',
        'salty_snacks', 'salty_snacks_daily', 'salty_snacks_weekly',
        'spreads', 'spreads_daily', 'spreads_weekly'
    ]
    
    if request.method == 'POST':
        try:
            #check for missing required fields
            missing = [field for field in required_fields if not request.POST.get(field)]
            if missing:
                messages.error(request, f"Please answer all required questions: {', '.join(missing)}")
                return render(request, 'assessments/dietary_screening.html', {
                    'patient': patient,
                    'perform_both': perform_both,
                })

            #create or update dietary screening
            screening, created = DietaryScreening.objects.get_or_create(
                patient=patient,
                defaults={
                    'sweet_sugary_foods': request.POST.get('sweet_sugary_foods', ''),
                    'sweet_sugary_foods_daily': request.POST.get('sweet_sugary_foods_daily', ''),
                    'sweet_sugary_foods_weekly': request.POST.get('sweet_sugary_foods_weekly', ''),
                    'cold_drinks_juices': request.POST.get('cold_drinks_juices', ''),
                    'cold_drinks_juices_daily': request.POST.get('cold_drinks_juices_daily', ''),
                    'cold_drinks_juices_weekly': request.POST.get('cold_drinks_juices_weekly', ''),
                    'takeaways_processed_foods': request.POST.get('takeaways_processed_foods', ''),
                    'takeaways_processed_foods_daily': request.POST.get('takeaways_processed_foods_daily', ''),
                    'takeaways_processed_foods_weekly': request.POST.get('takeaways_processed_foods_weekly', ''),
                    'salty_snacks': request.POST.get('salty_snacks', ''),
                    'salty_snacks_daily': request.POST.get('salty_snacks_daily', ''),
                    'salty_snacks_weekly': request.POST.get('salty_snacks_weekly', ''),
                    'spreads': request.POST.get('spreads', ''),
                    'spreads_daily': request.POST.get('spreads_daily', ''),
                    'spreads_weekly': request.POST.get('spreads_weekly', ''),
                }
            )
            
            if not created:
                #update existing screening
                fields = [
                    'sweet_sugary_foods', 'sweet_sugary_foods_daily', 'sweet_sugary_foods_weekly',
                    'cold_drinks_juices', 'cold_drinks_juices_daily', 'cold_drinks_juices_weekly',
                    'takeaways_processed_foods', 'takeaways_processed_foods_daily', 'takeaways_processed_foods_weekly',
                    'salty_snacks', 'salty_snacks_daily', 'salty_snacks_weekly',
                    'spreads', 'spreads_daily', 'spreads_weekly'
                ]

                for field in fields:
                    setattr(screening, field, request.POST.get(field, ''))
                screening.save()

            messages.success(request, "Dietary screening completed successfully!")
            
            #check if we need to proceed to dental screening
            if perform_both or request.POST.get('proceed_to_dental') == 'true':
                return redirect(f'/assessments/dental_screening/{patient_id}/?from_dietary=true')
            else:
                return redirect('report', patient_id=patient_id)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'assessments/dietary_screening.html', {
        'patient': patient,
        'perform_both': perform_both,
    })
