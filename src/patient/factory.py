import factory
from factory.declarations import LazyAttribute, LazyFunction, RelatedFactory
from factory.faker import Faker
from patient.models import Patient
from django.contrib.auth.models import User
import random
from faker import Faker as StdFaker

# Age distribution data for South African population
AGE_DISTRIBUTION = ["0", "1", "2", "3", "4", "5", "6"]
AGE_WEIGHTS = [0.25, 0.23, 0.17, 0.12, 0.10, 0.08, 0.05]

class PatientFactory(factory.django.DjangoModelFactory):

    class Meta: # type: ignore
        model = Patient

    created_by = LazyFunction(lambda: User.objects.order_by('?').first())

    gender = LazyFunction(lambda: random.choice(['0', '1']))
    name = LazyAttribute(lambda o: StdFaker().first_name_female() if o.gender == "1" else StdFaker().first_name_male())
    surname = Faker("last_name")

    age = LazyFunction(lambda: random.choices(AGE_DISTRIBUTION, weights=AGE_WEIGHTS, k=1)[0]) #Tried to use the distribution of the South African population

    parent_name = Faker("first_name")
    parent_surname = Faker("last_name")
    parent_id = LazyFunction(lambda: ''.join([str(random.randint(0, 9)) for _ in range(13)]))
    parent_contact = LazyFunction(lambda: ''.join([str(random.randint(0, 9)) for _ in range(10)]))

class PatientWithBothAssessmentsFactory(PatientFactory):
    """Factory that creates a patient with both dental and dietary assessments"""
    
    # Create related assessments after patient is created
    dental_screening = RelatedFactory(
        'assessments.factory.DentalFactory',
        'patient'
    )
    
    dietary_screening = RelatedFactory(
        'assessments.factory.DietaryFactory', 
        'patient'
    )


class PatientWithDentalOnlyFactory(PatientFactory):
    """Factory that creates a patient with only dental assessment"""
    
    dental_screening = RelatedFactory(
        'assessments.factory.DentalFactory',
        'patient'
    )


class PatientWithDietaryOnlyFactory(PatientFactory):
    """Factory that creates a patient with only dietary assessment"""
    
    dietary_screening = RelatedFactory(
        'assessments.factory.DietaryFactory', 
        'patient'
    )


class PatientWithMixedAssessmentsFactory(PatientFactory):
    """Factory that randomly creates patients with different assessment combinations
    
    Distribution:
    - 65% patients have both assessments
    - 20% patients have only dental assessment  
    - 15% patients have only dietary assessment
    """
    
    @classmethod
    def create(cls, **kwargs):
        """Override create method to randomly assign assessments"""
        # Create the patient first
        patient = super().create(**kwargs)
        
        # Randomly determine which assessments to create
        assessment_type = random.choices(
            ['both', 'dental_only', 'dietary_only'],
            weights=[0.65, 0.20, 0.15],
            k=1
        )[0]
        
        if assessment_type == 'both':
            from assessments.factory import DentalFactory, DietaryFactory
            DentalFactory.create(patient=patient)
            DietaryFactory.create(patient=patient)
        elif assessment_type == 'dental_only':
            from assessments.factory import DentalFactory
            DentalFactory.create(patient=patient)
        elif assessment_type == 'dietary_only':
            from assessments.factory import DietaryFactory
            DietaryFactory.create(patient=patient)
        
        return patient


# Keep the original name for backward compatibility
PatientWithAssessmentsFactory = PatientWithBothAssessmentsFactory


class PatientBatchFactory:
    """Utility class for creating batches of patients with different assessment patterns"""
    
    @staticmethod
    def create_mixed_batch(count=10):
        """Create a batch of patients with mixed assessment patterns
        
        Args:
            count (int): Number of patients to create
            
        Returns:
            list: List of created Patient instances
        """
        patients = []
        for _ in range(count):
            patient = PatientWithMixedAssessmentsFactory.create()
            patients.append(patient)
        return patients
    
    @staticmethod
    def create_specific_batch(both=5, dental_only=3, dietary_only=2):
        """Create a batch with specific counts of each assessment type
        
        Args:
            both (int): Number of patients with both assessments
            dental_only (int): Number of patients with only dental assessment
            dietary_only (int): Number of patients with only dietary assessment
            
        Returns:
            dict: Dictionary with lists of patients by assessment type
        """
        result = {
            'both': [],
            'dental_only': [],
            'dietary_only': []
        }
        
        # Create patients with both assessments
        for _ in range(both):
            patient = PatientWithBothAssessmentsFactory.create()
            result['both'].append(patient)
        
        # Create patients with dental only
        for _ in range(dental_only):
            patient = PatientWithDentalOnlyFactory.create()
            result['dental_only'].append(patient)
        
        # Create patients with dietary only
        for _ in range(dietary_only):
            patient = PatientWithDietaryOnlyFactory.create()
            result['dietary_only'].append(patient)
        
        return result


