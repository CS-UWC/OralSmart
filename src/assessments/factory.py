import factory
from factory.declarations import LazyAttribute, LazyFunction, SubFactory
from assessments.models import DentalScreening, DietaryScreening
import random
from faker import Faker as StdFaker

# Create single faker instance
fake = StdFaker()

class DentalFactory(factory.django.DjangoModelFactory):

    class Meta: # type: ignore
        model = DentalScreening

    # Can be used standalone or with RelatedFactory
    patient = SubFactory('patient.factory.PatientFactory')

    caregiver_treatment = LazyFunction(lambda: random.choice(["yes", "no"]))
    income = LazyFunction(lambda: random.choice(["0", "1-2500", "2501-5000", "5000-10000", "10001-20000", "20001-40000", "40001-70000", "70001+"]))
    sugar_meals = LazyFunction(lambda: random.choice(["yes", "no"]))
    sugar_snacks = LazyFunction(lambda: random.choice(["yes", "no"]))
    sugar_beverages = LazyFunction(lambda: random.choice(["yes", "no"]))
    sa_citizen = LazyFunction(lambda: random.choice(["yes", "no"]))
    special_needs = LazyFunction(lambda: random.choice(["yes", "no"]))
    plaque = LazyFunction(lambda: random.choice(["yes", "no"]))
    dry_mouth = LazyFunction(lambda: random.choice(["yes", "no"]))
    enamel_defects = LazyFunction(lambda: random.choice(["yes", "no"]))
    appliance = LazyFunction(lambda: random.choice(["yes", "no"]))
    fluoride_water = LazyFunction(lambda: random.choice(["yes", "no"]))
    fluoride_toothpaste = LazyFunction(lambda: random.choice(["yes", "no"]))
    topical_fluoride = LazyFunction(lambda: random.choice(["yes", "no"]))
    regular_checkups = LazyFunction(lambda: random.choice(["yes", "no"]))
    sealed_pits = LazyFunction(lambda: random.choice(["yes", "no"]))
    restorative_procedures = LazyFunction(lambda: random.choice(["yes", "no"]))
    enamel_change = LazyFunction(lambda: random.choice(["yes", "no"]))
    dentin_discoloration = LazyFunction(lambda: random.choice(["yes", "no"]))
    white_spot_lesions = LazyFunction(lambda: random.choice(["yes", "no"]))
    cavitated_lesions = LazyFunction(lambda: random.choice(["yes", "no"]))
    multiple_restorations = LazyFunction(lambda: random.choice(["yes", "no"]))
    missing_teeth = LazyFunction(lambda: random.choice(["yes", "no"]))
    
    # Teeth data as JSON - simplified structure
    teeth_data = LazyFunction(lambda: {
        f"tooth_{i}": fake.random_element(elements=["healthy", "cavity", "filling", "missing"])
        for i in range(1, 33)  # Assuming 32 teeth
    })


class DietaryFactory(factory.django.DjangoModelFactory):

    class Meta: # type: ignore
        model = DietaryScreening

    # Can be used standalone or with RelatedFactory
    patient = SubFactory('patient.factory.PatientFactory')

    # Section 1: Sweet/Sugary Foods
    sweet_sugary_foods = LazyFunction(lambda: random.choice(["yes", "no"]))
    sweet_sugary_foods_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=5)) if o.sweet_sugary_foods == "yes" else "0")
    sweet_sugary_foods_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.sweet_sugary_foods == "yes" else "0")
    sweet_sugary_foods_timing = LazyAttribute(lambda o: fake.random_element(elements=["morning", "afternoon", "evening", "night"]) if o.sweet_sugary_foods == "yes" else "")
    sweet_sugary_foods_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.sweet_sugary_foods == "yes" else "no")

    # Section 2: Take-aways and Processed Foods
    takeaways_processed_foods = LazyFunction(lambda: random.choice(["yes", "no"]))
    takeaways_processed_foods_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=3)) if o.takeaways_processed_foods == "yes" else "0")
    takeaways_processed_foods_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.takeaways_processed_foods == "yes" else "0")

    # Section 3: Fresh Fruit
    fresh_fruit = LazyFunction(lambda: random.choice(["yes", "no"]))
    fresh_fruit_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=8)) if o.fresh_fruit == "yes" else "0")
    fresh_fruit_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.fresh_fruit == "yes" else "0")
    fresh_fruit_timing = LazyAttribute(lambda o: fake.random_element(elements=["morning", "afternoon", "evening", "night"]) if o.fresh_fruit == "yes" else "")
    fresh_fruit_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.fresh_fruit == "yes" else "no")

    # Section 4: Cold Drinks, Juices and Flavoured Water and Milk
    cold_drinks_juices = LazyFunction(lambda: random.choice(["yes", "no"]))
    cold_drinks_juices_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=6)) if o.cold_drinks_juices == "yes" else "0")
    cold_drinks_juices_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.cold_drinks_juices == "yes" else "0")
    cold_drinks_juices_timing = LazyAttribute(lambda o: fake.random_element(elements=["morning", "afternoon", "evening", "night"]) if o.cold_drinks_juices == "yes" else "")
    cold_drinks_juices_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.cold_drinks_juices == "yes" else "no")

    # Section 5: Processed Fruit
    processed_fruit = LazyFunction(lambda: random.choice(["yes", "no"]))
    processed_fruit_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=4)) if o.processed_fruit == "yes" else "0")
    processed_fruit_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.processed_fruit == "yes" else "0")
    processed_fruit_timing = LazyAttribute(lambda o: fake.random_element(elements=["morning", "afternoon", "evening", "night"]) if o.processed_fruit == "yes" else "")
    processed_fruit_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.processed_fruit == "yes" else "no")

    # Section 6: Spreads
    spreads = LazyFunction(lambda: random.choice(["yes", "no"]))
    spreads_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=3)) if o.spreads == "yes" else "0")
    spreads_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.spreads == "yes" else "0")
    spreads_timing = LazyAttribute(lambda o: fake.random_element(elements=["morning", "afternoon", "evening", "night"]) if o.spreads == "yes" else "")
    spreads_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.spreads == "yes" else "no")

    # Section 7: Added Sugars
    added_sugars = LazyFunction(lambda: random.choice(["yes", "no"]))
    added_sugars_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=4)) if o.added_sugars == "yes" else "0")
    added_sugars_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.added_sugars == "yes" else "0")
    added_sugars_timing = LazyAttribute(lambda o: fake.random_element(elements=["morning", "afternoon", "evening", "night"]) if o.added_sugars == "yes" else "")
    added_sugars_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.added_sugars == "yes" else "no")

    # Section 8: Salty Snacks
    salty_snacks = LazyFunction(lambda: random.choice(["yes", "no"]))
    salty_snacks_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=3)) if o.salty_snacks == "yes" else "0")
    salty_snacks_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.salty_snacks == "yes" else "0")
    salty_snacks_timing = LazyAttribute(lambda o: fake.random_element(elements=["morning", "afternoon", "evening", "night"]) if o.salty_snacks == "yes" else "")

    # Section 9: Dairy Products
    dairy_products = LazyFunction(lambda: random.choice(["yes", "no"]))
    dairy_products_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=5)) if o.dairy_products == "yes" else "0")
    dairy_products_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.dairy_products == "yes" else "0")

    # Section 10: Vegetables
    vegetables = LazyFunction(lambda: random.choice(["yes", "no"]))
    vegetables_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=8)) if o.vegetables == "yes" else "0")
    vegetables_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.vegetables == "yes" else "0")

    # Section 11: Water
    water = LazyFunction(lambda: random.choice(["yes", "no"]))
    water_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "throughout day", "before bed"]) if o.water == "yes" else "")
    water_glasses = LazyAttribute(lambda o: str(fake.random_int(min=1, max=12)) if o.water == "yes" else "0")

    # Section 12: Xylitol-containing Products
    xylitol_products = LazyFunction(lambda: random.choice(["yes", "no"]))
    xylitol_products_daily = LazyAttribute(lambda o: str(fake.random_int(min=1, max=3)) if o.xylitol_products == "yes" else "0")
    xylitol_products_weekly = LazyAttribute(lambda o: str(fake.random_int(min=1, max=7)) if o.xylitol_products == "yes" else "0")