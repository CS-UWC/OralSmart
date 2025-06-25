from django.shortcuts import render, redirect
from django.contrib import messages
from patient.models import Patient
from .models import DentalScreening

# Create your views here.

def dental_screening(request, patient_id):

    patient = Patient.objects.get(pk=patient_id)

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

            return redirect('report', patient_id=patient_id)  #redirects to report page and sends patient_id for identification

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'assessments/dental_screening.html', {
        'permanent_upper': permanent_upper,
        'permanent_lower': permanent_lower,
        'primary_upper': primary_upper,
        'primary_lower': primary_lower,
    })
