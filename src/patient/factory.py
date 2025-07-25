import factory
from factory.declarations import LazyAttribute, LazyFunction, RelatedFactory
from factory.faker import Faker
from patient.models import Patient
from django.contrib.auth.models import User
import random
from faker import Faker as StdFaker

# Age distribution data for South African population
AGE_DISTRIBUTION = ["0", "1", "2", "3", "4", "5", "6"]
AGE_WEIGHTS = [0.22, 0.20, 0.18, 0.15, 0.12, 0.08, 0.05]

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

class PatientWithAssessmentsFactory(PatientFactory):
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


