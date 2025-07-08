from django.core.management.base import BaseCommand
from patient.models import Patient
from assessments.models import DentalScreening, DietaryScreening

class Command(BaseCommand):
    help = 'Check existing patients and their screening data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== EXISTING PATIENTS ==='))
        
        patients = Patient.objects.all()
        
        if not patients:
            self.stdout.write(self.style.WARNING('No patients found in the database'))
            return
        
        for patient in patients:
            self.stdout.write(f"\n--- Patient ID: {patient.pk} ---")
            self.stdout.write(f"Name: {patient.name} {patient.surname}")
            self.stdout.write(f"Parent ID: {patient.parent_id}")
            self.stdout.write(f"Contact: {patient.parent_contact}")
            
            # Check for dental screening
            try:
                dental = DentalScreening.objects.filter(patient_id=patient.pk).first()
                if dental:
                    self.stdout.write(self.style.SUCCESS("✓ Has Dental Screening"))
                else:
                    self.stdout.write(self.style.ERROR("✗ No Dental Screening"))
            except Exception as e:
                self.stdout.write(self.style.ERROR("✗ No Dental Screening"))
            
            # Check for dietary screening
            try:
                dietary = DietaryScreening.objects.filter(patient_id=patient.pk).first()
                if dietary:
                    self.stdout.write(self.style.SUCCESS("✓ Has Dietary Screening"))
                else:
                    self.stdout.write(self.style.ERROR("✗ No Dietary Screening"))
            except Exception as e:
                self.stdout.write(self.style.ERROR("✗ No Dietary Screening"))
        
        self.stdout.write(f"\nTotal patients: {patients.count()}")
