from django.core.management.base import BaseCommand
from patient.models import Patient
from assessments.models import DentalScreening, DietaryScreening

class Command(BaseCommand):
    help = 'Create sample screening data for testing email functionality'

    def handle(self, *args, **options):
        # Find a patient with dental screening data
        patients_with_dental = []
        patients = Patient.objects.all()
        
        for patient in patients:
            dental_count = DentalScreening.objects.filter(patient_id=patient.pk).count()
            if dental_count > 0:
                patients_with_dental.append((patient, dental_count))
        
        if not patients_with_dental:
            self.stdout.write(self.style.ERROR('No patients with dental screening data found'))
            return
        
        self.stdout.write(self.style.SUCCESS('=== PATIENTS WITH DENTAL SCREENING DATA ==='))
        
        for patient, count in patients_with_dental[:5]:  # Show first 5
            self.stdout.write(f"\n--- Patient ID: {patient.pk} ---")
            self.stdout.write(f"Name: {patient.name} {patient.surname}")
            self.stdout.write(f"Parent ID: {patient.parent_id}")
            self.stdout.write(f"Contact: {patient.parent_contact}")
            self.stdout.write(f"Dental Screenings: {count}")
            
            # Check for dietary screening
            dietary_count = DietaryScreening.objects.filter(patient_id=patient.pk).count()
            if dietary_count > 0:
                self.stdout.write(self.style.SUCCESS(f"✓ Has {dietary_count} Dietary Screening(s)"))
            else:
                self.stdout.write(self.style.ERROR("✗ No Dietary Screening"))
        
        # Suggest a patient for testing
        if patients_with_dental:
            test_patient = patients_with_dental[0][0]
            self.stdout.write(f"\n{self.style.SUCCESS('SUGGESTED PATIENT FOR EMAIL TESTING:')}")
            self.stdout.write(f"Patient ID: {test_patient.pk}")
            self.stdout.write(f"Name: {test_patient.name} {test_patient.surname}")
            self.stdout.write(f"URL: http://localhost:8000/reports/report/{test_patient.pk}/")
            
            # Show recent dental screening data
            dental_screening = DentalScreening.objects.filter(patient_id=test_patient.pk).first()
            if dental_screening:
                self.stdout.write(f"SA Citizen: {dental_screening.sa_citizen}")
                self.stdout.write(f"Special Needs: {dental_screening.special_needs}")
                self.stdout.write(f"Plaque: {dental_screening.plaque}")
