import factory
from factory.declarations import LazyAttribute, LazyFunction, SubFactory
from assessments.models import DentalScreening, DietaryScreening
import random
from faker import Faker as StdFaker

# Create single faker instance
fake = StdFaker()

class DentalFactory(factory.django.DjangoModelFactory):
    """
    DentalFactory generates realistic test instances of the DentalScreening model for use in Django tests.
    It provides randomized data for various dental screening fields, including patient information, oral health indicators,
    fluoride exposure, and dental procedures. The factory also simulates realistic teeth data using the FDI numbering system,
    randomly selecting between primary, mixed, or permanent dentition types to match typical age-related dental development.
    Attributes:
        patient (PatientFactory): Related patient instance.
        caregiver_treatment (str): Randomly "yes" or "no".
        sa_citizen (str): Randomly "yes" or "no".
        special_needs (str): Randomly "yes" or "no".
        plaque (str): Randomly "yes" or "no".
        dry_mouth (str): Randomly "yes" or "no", weighted by prevalence.
        enamel_defects (str): Randomly "yes" or "no".
        appliance (str): Randomly "yes" or "no".
        fluoride_water (str): Randomly "yes" or "no".
        fluoride_toothpaste (str): Randomly "yes" or "no".
        topical_fluoride (str): Randomly "yes" or "no".
        regular_checkups (str): Randomly "yes" or "no".
        sealed_pits (str): Randomly "yes" or "no".
        restorative_procedures (str): Randomly "yes" or "no".
        enamel_change (str): Randomly "yes" or "no".
        dentin_discoloration (str): Randomly "yes" or "no".
        white_spot_lesions (str): Randomly "yes" or "no".
        cavitated_lesions (str): Randomly "yes" or "no".
        multiple_restorations (str): Randomly "yes" or "no".
        missing_teeth (str): Randomly "yes" or "no".
        teeth_data (dict): Simulated teeth status using FDI numbering, reflecting primary, mixed, or permanent dentition.
    """

    class Meta: # type: ignore
        model = DentalScreening

    # Can be used standalone or with RelatedFactory
    patient = SubFactory('patient.factory.PatientFactory')

    caregiver_treatment = LazyFunction(lambda: random.choice(["yes", "no"]))
    sa_citizen = LazyFunction(lambda: random.choice(["yes", "no"]))
    special_needs = LazyFunction(lambda: random.choice(["yes", "no"]))
    plaque = LazyFunction(lambda: random.choice(["yes", "no"]))
    dry_mouth = LazyFunction(lambda: random.choices(["yes", "no"], weights=[0.242, 0.758], k=1)[0]) #Used distribution in Çiftçi and Aşantoğrol BMC Oral Health (2024) 24:430, variable = Dry Mouth
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
    
    # Teeth data as JSON - using FDI numbering system to match dental screening form
    # Generates realistic teeth data based on random dentition type
    teeth_data = LazyFunction(lambda: {
        # Randomly choose dentition type (primary, mixed, or permanent)
        **({
            # Primary dentition only (ages 2-6)
            **{f"tooth_{tooth}": fake.random_element(elements=["A", "B", "C", "D", "E", "X", "F"]) 
               for tooth in ["55", "54", "53", "52", "51", "61", "62", "63", "64", "65",
                            "85", "84", "83", "82", "81", "71", "72", "73", "74", "75"]}
        } if random.random() < 0.3 else {  # 30% chance primary only
            # Mixed dentition (ages 6-12) - some permanent, some primary
            **{f"tooth_{tooth}": fake.random_element(elements=["0", "1", "2", "6", "8"]) 
               for tooth in ["16", "11", "21", "26", "36", "31", "41", "46"]},
            **{f"tooth_{tooth}": fake.random_element(elements=["A", "B", "C", "D", "E", "X", "F"]) 
               for tooth in ["54", "53", "52", "62", "63", "64", "74", "73", "72", "82", "83", "84"]}  # Remaining primary teeth
        } if random.random() < 0.4 else {    # 40% chance mixed (of remaining 70%)
            # Permanent dentition (ages 12+)
            **{f"tooth_{tooth}": fake.random_element(elements=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]) 
               for tooth in ["18", "17", "16", "15", "14", "13", "12", "11", 
                            "21", "22", "23", "24", "25", "26", "27", "28",
                            "48", "47", "46", "45", "44", "43", "42", "41", 
                            "31", "32", "33", "34", "35", "36", "37", "38"]}
        })
    })


class DietaryFactory(factory.django.DjangoModelFactory):
    """
    DietaryFactory
    A DjangoModelFactory for generating mock DietaryScreening instances for testing purposes.
    This factory simulates realistic dietary screening data, including various food and drink consumption patterns, 
    timings, and frequencies, based on plausible distributions and research data.
    Attributes:
        patient: A related PatientFactory instance.
        sweet_sugary_foods: "yes" or "no" indicating sweet/sugary food consumption (weighted distribution).
        sweet_sugary_foods_daily: Daily frequency if consumed.
        sweet_sugary_foods_weekly: Weekly frequency if consumed.
        sweet_sugary_foods_timing: Timing of consumption if consumed.
        sweet_sugary_foods_bedtime: "yes" or "no" if consumed at bedtime.
        takeaways_processed_foods: "yes" or "no" for takeaways/processed foods.
        takeaways_processed_foods_daily: Daily frequency if consumed.
        takeaways_processed_foods_weekly: Weekly frequency if consumed.
        fresh_fruit: "yes" or "no" for fresh fruit consumption.
        fresh_fruit_daily: Daily frequency if consumed.
        fresh_fruit_weekly: Weekly frequency if consumed.
        fresh_fruit_timing: Timing of consumption if consumed.
        fresh_fruit_bedtime: "yes" or "no" if consumed at bedtime.
        cold_drinks_juices: "yes" or "no" for cold drinks, juices, flavoured water/milk.
        cold_drinks_juices_daily: Daily frequency if consumed.
        cold_drinks_juices_weekly: Weekly frequency if consumed.
        cold_drinks_juices_timing: Timing of consumption if consumed.
        cold_drinks_juices_bedtime: "yes" or "no" if consumed at bedtime.
        processed_fruit: "yes" or "no" for processed fruit.
        processed_fruit_daily: Daily frequency if consumed.
        processed_fruit_weekly: Weekly frequency if consumed.
        processed_fruit_timing: Timing of consumption if consumed.
        processed_fruit_bedtime: "yes" or "no" if consumed at bedtime.
        spreads: "yes" or "no" for spreads.
        spreads_daily: Daily frequency if consumed.
        spreads_weekly: Weekly frequency if consumed.
        spreads_timing: Timing of consumption if consumed.
        spreads_bedtime: "yes" or "no" if consumed at bedtime.
        added_sugars: "yes" or "no" for added sugars.
        added_sugars_daily: Daily frequency if consumed.
        added_sugars_weekly: Weekly frequency if consumed.
        added_sugars_timing: Timing of consumption if consumed.
        added_sugars_bedtime: "yes" or "no" if consumed at bedtime.
        salty_snacks: "yes" or "no" for salty snacks.
        salty_snacks_daily: Daily frequency if consumed.
        salty_snacks_weekly: Weekly frequency if consumed.
        salty_snacks_timing: Timing of consumption if consumed.
        dairy_products: "yes" or "no" for dairy products.
        dairy_products_daily: Daily frequency if consumed.
        dairy_products_weekly: Weekly frequency if consumed.
        vegetables: "yes" or "no" for vegetables.
        vegetables_daily: Daily frequency if consumed.
        vegetables_weekly: Weekly frequency if consumed.
        water: "yes" or "no" for water consumption.
        water_timing: Timing of water consumption if consumed.
        water_glasses: Number of glasses consumed daily if consumed.
    Note:
        - Most attributes are conditionally generated based on the main "yes"/"no" field for each section.
        - Frequencies and timings are randomized within plausible ranges.
        - Intended for use in tests and development environments.
    """


    class Meta: # type: ignore
        model = DietaryScreening

    # Can be used standalone or with RelatedFactory
    patient = SubFactory('patient.factory.PatientFactory')

    # Section 1: Sweet/Sugary Foods
    sweet_sugary_foods = LazyFunction(lambda: random.choices(["yes", "no"], weights=[0.663, 0.337], k=1)[0]) #Used the distribution in Çiftçi and Aşantoğrol BMC Oral Health (2024) 24:430
    sweet_sugary_foods_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=5)) if o.sweet_sugary_foods == "yes" else None)
    sweet_sugary_foods_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.sweet_sugary_foods == "yes" else None)
    sweet_sugary_foods_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "before bed", "anytime"]) if o.sweet_sugary_foods == "yes" else None)
    sweet_sugary_foods_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.sweet_sugary_foods == "yes" else None)

    # Section 2: Take-aways and Processed Foods
    takeaways_processed_foods = LazyFunction(lambda: random.choice(["yes", "no"]))
    takeaways_processed_foods_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=3)) if o.takeaways_processed_foods == "yes" else None)
    takeaways_processed_foods_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.takeaways_processed_foods == "yes" else None)

    # Section 3: Fresh Fruit
    fresh_fruit = LazyFunction(lambda: random.choice(["yes", "no"]))
    fresh_fruit_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=8)) if o.fresh_fruit == "yes" else None)
    fresh_fruit_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.fresh_fruit == "yes" else None)
    fresh_fruit_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "before bed", "anytime"]) if o.fresh_fruit == "yes" else None)
    fresh_fruit_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.fresh_fruit == "yes" else None)

    # Section 4: Cold Drinks, Juices and Flavoured Water and Milk
    cold_drinks_juices = LazyFunction(lambda: random.choice(["yes", "no"]))
    cold_drinks_juices_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=6)) if o.cold_drinks_juices == "yes" else None)
    cold_drinks_juices_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.cold_drinks_juices == "yes" else None)
    cold_drinks_juices_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "before bed", "anytime"]) if o.cold_drinks_juices == "yes" else None)
    cold_drinks_juices_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.cold_drinks_juices == "yes" else None)

    # Section 5: Processed Fruit
    processed_fruit = LazyFunction(lambda: random.choice(["yes", "no"]))
    processed_fruit_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=4)) if o.processed_fruit == "yes" else None)
    processed_fruit_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.processed_fruit == "yes" else None)
    processed_fruit_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "before bed", "anytime"]) if o.processed_fruit == "yes" else None)
    processed_fruit_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.processed_fruit == "yes" else None)

    # Section 6: Spreads
    spreads = LazyFunction(lambda: random.choice(["yes", "no"]))
    spreads_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=3)) if o.spreads == "yes" else None)
    spreads_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.spreads == "yes" else None)
    spreads_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "before bed", "anytime"]) if o.spreads == "yes" else None)
    spreads_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.spreads == "yes" else None)

    # Section 7: Added Sugars
    added_sugars = LazyFunction(lambda: random.choice(["yes", "no"]))
    added_sugars_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=4)) if o.added_sugars == "yes" else None)
    added_sugars_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.added_sugars == "yes" else None)
    added_sugars_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "before bed", "anytime"]) if o.added_sugars == "yes" else None)
    added_sugars_bedtime = LazyAttribute(lambda o: random.choice(["yes", "no"]) if o.added_sugars == "yes" else None)

    # Section 8: Salty Snacks
    salty_snacks = LazyFunction(lambda: random.choice(["yes", "no"]))
    salty_snacks_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=3)) if o.salty_snacks == "yes" else None)
    salty_snacks_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.salty_snacks == "yes" else None)
    salty_snacks_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "anytime"]) if o.salty_snacks == "yes" else None)

    # Section 9: Dairy Products
    dairy_products = LazyFunction(lambda: random.choice(["yes", "no"]))
    dairy_products_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=5)) if o.dairy_products == "yes" else None)
    dairy_products_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.dairy_products == "yes" else None)

    # Section 10: Vegetables
    vegetables = LazyFunction(lambda: random.choice(["yes", "no"]))
    vegetables_daily = LazyAttribute(lambda o: str(fake.random_int(min=0, max=8)) if o.vegetables == "yes" else None)
    vegetables_weekly = LazyAttribute(lambda o: str(fake.random_int(min=0, max=7)) if o.vegetables == "yes" else None)

    # Section 11: Water
    water = LazyFunction(lambda: random.choice(["yes", "no"]))
    water_timing = LazyAttribute(lambda o: fake.random_element(elements=["with meals", "between meals", "throughout day", "before bed"]) if o.water == "yes" else None)
    water_glasses = LazyAttribute(lambda o: str(fake.random_int(min=1, max=12)) if o.water == "yes" else None)
