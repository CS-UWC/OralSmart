from django.core.management.base import BaseCommand
from patient.models import Patient
from assessments.models import DentalScreening, DietaryScreening


class Command(BaseCommand):
    help = 'Delete all patients and their related assessment data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without interactive prompt'
        )
    
    def handle(self, *args, **options):
        # Count current records
        patient_count = Patient.objects.count()
        dental_count = DentalScreening.objects.count()
        dietary_count = DietaryScreening.objects.count()
        
        self.stdout.write("Current counts:")
        self.stdout.write(f"  Patients: {patient_count}")
        self.stdout.write(f"  Dental Screenings: {dental_count}")
        self.stdout.write(f"  Dietary Screenings: {dietary_count}")
        
        if patient_count == 0:
            self.stdout.write(self.style.WARNING("No patients to delete."))
            return
        
        # Confirmation
        if not options['confirm']:
            confirm = input(f"\nAre you sure you want to delete ALL {patient_count} patients? (yes/no): ")
            if confirm.lower() != 'yes':
                self.stdout.write("Deletion cancelled.")
                return
        
        # Delete all related data first
        dental_deleted = DentalScreening.objects.all().delete()[0]
        dietary_deleted = DietaryScreening.objects.all().delete()[0]
        
        # Delete all patients
        patients_deleted = Patient.objects.all().delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted:\n"
                f"  {patients_deleted} patients\n"
                f"  {dental_deleted} dental screenings\n"
                f"  {dietary_deleted} dietary screenings"
            )
        )
        
        # Verify deletion
        remaining_patients = Patient.objects.count()
        if remaining_patients == 0:
            self.stdout.write(self.style.SUCCESS("All patients successfully deleted."))
        else:
            self.stdout.write(
                self.style.ERROR(f"Warning: {remaining_patients} patients still remain!")
            )