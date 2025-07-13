import factory
from factory.declarations import LazyAttribute, LazyFunction, RelatedFactory
from factory.faker import Faker
from patient.models import Patient
from django.contrib.auth.models import User
import random
from faker import Faker as StdFaker

class PatientFactory(factory.django.DjangoModelFactory):

    class Meta: # type: ignore
        model = Patient

    created_by = LazyFunction(lambda: User.objects.order_by('?').first())

    gender = LazyFunction(lambda: random.choice(['0', '1']))
    name = LazyAttribute(lambda o: StdFaker().first_name_female() if o.gender == "1" else StdFaker().first_name_male())
    surname = Faker("last_name")
    age = LazyFunction(lambda: random.choice(["0", "1", "2", "3", "4", "5", "6"]))

    parent_name = Faker("first_name")
    parent_surname = Faker("last_name")
    parent_id = LazyFunction(lambda: ''.join([str(random.randint(0, 9)) for _ in range(13)]))
    parent_contact = LazyFunction(lambda: ''.join([str(random.randint(0, 9)) for _ in range(10)]))

    # Timestamp (auto_now_add will handle this, but we can set it if needed)
    # created_at is handled automatically by Django

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


