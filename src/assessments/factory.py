import factory
from factory.declarations import LazyAttribute, LazyFunction, SubFactory
from assessments.models import DentalScreening, DietaryScreening
import random
import numpy as np
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

    caregiver_treatment = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    sa_citizen = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    special_needs = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.1) == 1 else "no")
    plaque = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    dry_mouth = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.242) == 1 else "no") #Used distribution in Çiftçi and Aşantoğrol BMC Oral Health (2024) 24:430, variable = Dry Mouth
    enamel_defects = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    appliance = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    fluoride_water = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    fluoride_toothpaste = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    topical_fluoride = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    regular_checkups = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    sealed_pits = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    restorative_procedures = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    enamel_change = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    dentin_discoloration = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    white_spot_lesions = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    cavitated_lesions = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    multiple_restorations = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    missing_teeth = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    
    # Helper method to calculate tooth probabilities based on risk factors
    @classmethod
    def calculate_tooth_probabilities(cls, obj):
        """Calculate tooth status probabilities based on patient's dental AND dietary risk factors.
        Optimized for pediatric patients aged 0-6 years with primary dentition focus."""
        age = int(obj.patient.age)
        
        # Age-based base probabilities for 0-6 year old children
        if age < 1:
            # Infants - mostly unerupted teeth
            base_probs = {
                "A": 0.10,  # Sound (few teeth erupted)
                "B": 0.00,  # Filled+Decayed (very rare)
                "C": 0.02,  # Decayed (rare early caries)
                "D": 0.00,  # Filled (extremely rare)
                "E": 0.00,  # Missing due to caries (rare)
                "X": 0.88,  # Unerupted/Missing (most teeth)
                "F": 0.00   # Missing other reasons
            }
        elif age < 2:
            # Toddlers - erupting primary teeth, some ECC risk
            base_probs = {
                "A": 0.70,  # Sound
                "B": 0.01,  # Filled+Decayed (very rare)
                "C": 0.08,  # Decayed (Early Childhood Caries starting)
                "D": 0.00,  # Filled (rare at this age)
                "E": 0.01,  # Missing due to caries
                "X": 0.20,  # Unerupted/Missing
                "F": 0.00   # Missing other reasons
            }
        elif age < 3:
            # 2-year-olds - primary dentition completing, ECC peak risk
            base_probs = {
                "A": 0.60,  # Sound
                "B": 0.03,  # Filled+Decayed
                "C": 0.20,  # Decayed (ECC common, especially upper anteriors)
                "D": 0.02,  # Filled (starting to treat)
                "E": 0.03,  # Missing due to caries
                "X": 0.12,  # Unerupted/Missing
                "F": 0.00   # Missing other reasons
            }
        elif age < 4:
            # 3-year-olds - full primary dentition, high caries risk
            base_probs = {
                "A": 0.50,  # Sound
                "B": 0.08,  # Filled+Decayed
                "C": 0.28,  # Decayed (peak caries period)
                "D": 0.06,  # Filled
                "E": 0.05,  # Missing due to caries
                "X": 0.03,  # Unerupted/Missing
                "F": 0.00   # Missing other reasons
            }
        elif age < 5:
            # 4-year-olds - managing existing caries, some treatment
            base_probs = {
                "A": 0.45,  # Sound
                "B": 0.12,  # Filled+Decayed
                "C": 0.25,  # Decayed (still high)
                "D": 0.10,  # Filled (more treatment)
                "E": 0.06,  # Missing due to caries
                "X": 0.02,  # Unerupted/Missing
                "F": 0.00   # Missing other reasons
            }
        elif age < 6:
            # 5-year-olds - preparing for permanent teeth, managing primary caries
            base_probs = {
                "A": 0.42,  # Sound
                "B": 0.15,  # Filled+Decayed
                "C": 0.23,  # Decayed
                "D": 0.12,  # Filled
                "E": 0.07,  # Missing due to caries
                "X": 0.01,  # Unerupted/Missing
                "F": 0.00   # Missing other reasons
            }
        else:
            # 6+ years - early mixed dentition
            base_probs = {
                "A": 0.40,  # Sound
                "B": 0.18,  # Filled+Decayed
                "C": 0.22,  # Decayed
                "D": 0.12,  # Filled
                "E": 0.06,  # Missing due to caries
                "X": 0.01,  # Unerupted/Missing
                "F": 0.01   # Missing other reasons (trauma, etc.)
            }
        
        # Calculate risk factors with pediatric-specific weighting
        dental_risk_factors = [
            ("plaque", "yes", 3.0),  # Higher impact in young children
            ("dry_mouth", "yes", 2.0),  # More significant in children
            ("special_needs", "yes", 3.5),  # Major risk factor for young children
            ("enamel_defects", "yes", 3.0),  # Critical in primary teeth
            ("white_spot_lesions", "yes", 2.5),  # Early caries indicator
            ("cavitated_lesions", "yes", 3.0),  # Advanced caries
            ("multiple_restorations", "yes", 1.5),
            ("dentin_discoloration", "yes", 2.0),
            # Protective factors (critical in early years)
            ("fluoride_water", "no", 2.0),  # Major protective factor
            ("fluoride_toothpaste", "no", 2.5),  # Essential for young children
            ("regular_checkups", "no", 2.0),  # Early intervention crucial
            ("sealed_pits", "no", 1.0),  # Less relevant for primary teeth
        ]
        
        dental_risk = sum(weight for attr, value, weight in dental_risk_factors 
                         if getattr(obj, attr) == value)
        
        # Add dietary risk with high impact for young children
        dietary_risk = 0
        try:
            from assessments.models import DietaryScreening
            dietary_screening = DietaryScreening.objects.filter(patient=obj.patient).first()
            if dietary_screening:
                dietary_risk = DietaryFactory.calculate_dietary_risk_score(dietary_screening)
                # Dietary risk has very high impact in young children (0-6)
                dietary_risk *= 1.5
        except (ImportError, AttributeError):
            pass
        
        # Normalize total risk for pediatric scale
        max_risk = 20.0  # Higher scale for young children
        total_risk = min(1.0, (dental_risk + dietary_risk) / max_risk)
        
        # Apply risk adjustments to base probabilities
        probs = base_probs.copy()
        
        if total_risk > 0:
            # Reduce sound teeth aggressively in high-risk young children
            reduction_factor = 0.70  # Strong impact of risk factors
            probs["A"] = max(0.05, probs["A"] - (total_risk * reduction_factor))
            
            # Increase caries significantly in young children
            caries_increase = 0.50  # High susceptibility
            probs["C"] = min(0.80, probs["C"] + (total_risk * caries_increase))
            
            # Moderate increases for other conditions
            probs["B"] = min(0.40, probs["B"] + (total_risk * 0.25))
            
            # Young children: more likely to have extractions than complex fillings
            if age < 4:
                # Very young children - extractions more common than fillings
                probs["E"] = min(0.15, probs["E"] + (total_risk * 0.12))
                probs["D"] = min(0.15, probs["D"] + (total_risk * 0.08))
            else:
                # 4-6 years - can cooperate better for fillings
                probs["D"] = min(0.25, probs["D"] + (total_risk * 0.15))
                probs["E"] = min(0.12, probs["E"] + (total_risk * 0.10))
            
            # Normalize probabilities
            total = sum(probs.values())
            for key in probs:
                probs[key] /= total
                
        return probs

    # Teeth data as JSON - using FDI numbering system to match dental screening form
    teeth_data = LazyAttribute(lambda obj: {
        f"tooth_{tooth}": (
            random.choices(["A", "X"], weights=[0.95, 0.05], k=1)[0] if int(obj.patient.age) < 2 
            else (
                (lambda probs=DentalFactory.calculate_tooth_probabilities(obj): 
                    random.choices(
                        ["A", "B", "C", "D", "E", "X", "F"],
                        weights=[probs[s] for s in ["A", "B", "C", "D", "E", "X", "F"]],
                        k=1
                    )[0]
                )()
            )
        ) for tooth in ["55", "54", "53", "52", "51", "61", "62", "63", "64", "65",
                       "85", "84", "83", "82", "81", "71", "72", "73", "74", "75"]
    })


class DietaryFactory(factory.django.DjangoModelFactory):
    @classmethod
    def get_realistic_frequency(cls, age, food_type, frequency_type='daily'):
        """
        Return a more realistic frequency for daily/weekly consumption based on age and food type.
        Optimized for pediatric patients aged 0-6 years.
        Args:
            age (int): Patient age (0-6 years).
            food_type (str): The food group.
            frequency_type (str): 'daily' or 'weekly' to return appropriate choices.
        Returns:
            str: Frequency code.
        """
        age = int(age)
        
        # Daily frequency choices
        daily_choices = ["1-3_day", "3-4_day", "4-6_day"]
        weekly_choices = ["1-3_week", "3-4_week", "4-6_week"]
        
        if frequency_type == 'daily':
            if food_type == 'sweet_sugary_foods':
                if age < 2:
                    # Infants/toddlers - limited sweets exposure
                    return random.choices(daily_choices, weights=[0.9, 0.1, 0.0])[0]
                elif age < 4:
                    # Preschoolers - more sweets but still controlled
                    return random.choices(daily_choices, weights=[0.6, 0.3, 0.1])[0]
                else:
                    # 4-6 years - higher sweet consumption
                    return random.choices(daily_choices, weights=[0.4, 0.4, 0.2])[0]
                    
            elif food_type == 'cold_drinks_juices':
                if age < 1:
                    # Infants - mostly milk/water
                    return random.choices(daily_choices, weights=[0.95, 0.05, 0.0])[0]
                elif age < 3:
                    # Toddlers - some juice introduction
                    return random.choices(daily_choices, weights=[0.7, 0.25, 0.05])[0]
                else:
                    # 3-6 years - more juice/drinks
                    return random.choices(daily_choices, weights=[0.4, 0.4, 0.2])[0]
                    
            elif food_type == 'fresh_fruit':
                if age < 1:
                    # Infants - limited solid fruits
                    return random.choices(daily_choices, weights=[0.8, 0.2, 0.0])[0]
                elif age < 3:
                    # Toddlers - increasing fruit
                    return random.choices(daily_choices, weights=[0.3, 0.5, 0.2])[0]
                else:
                    # 3-6 years - regular fruit consumption
                    return random.choices(daily_choices, weights=[0.2, 0.4, 0.4])[0]
                    
            elif food_type == 'vegetables':
                if age < 2:
                    # Infants/toddlers - limited vegetables
                    return random.choices(daily_choices, weights=[0.8, 0.2, 0.0])[0]
                elif age < 4:
                    # Preschoolers - picky eating phase
                    return random.choices(daily_choices, weights=[0.7, 0.25, 0.05])[0]
                else:
                    # 4-6 years - slightly better acceptance
                    return random.choices(daily_choices, weights=[0.6, 0.3, 0.1])[0]
            return random.choice(daily_choices)
        
        else:  # weekly
            if food_type == 'sweet_sugary_foods':
                if age < 2:
                    return random.choices(weekly_choices, weights=[0.8, 0.2, 0.0])[0]
                elif age < 4:
                    return random.choices(weekly_choices, weights=[0.5, 0.3, 0.2])[0]
                else:
                    return random.choices(weekly_choices, weights=[0.3, 0.4, 0.3])[0]
                    
            elif food_type == 'cold_drinks_juices':
                if age < 2:
                    return random.choices(weekly_choices, weights=[0.9, 0.1, 0.0])[0]
                elif age < 4:
                    return random.choices(weekly_choices, weights=[0.6, 0.3, 0.1])[0]
                else:
                    return random.choices(weekly_choices, weights=[0.4, 0.4, 0.2])[0]
            return random.choice(weekly_choices)

    @classmethod
    def get_realistic_timing(cls, age, food_type):
        """
        Return a more realistic timing for food consumption based on age and food type.
        Args:
            age (int): Patient age.
            food_type (str): The food group.
        Returns:
            str: Timing code.
        """
        if food_type in ["sweet_sugary_foods", "cold_drinks_juices"]:
            if int(age) < 12:
                return random.choices(["with_meals", "between_meals"], weights=[0.7, 0.3])[0]
            else:
                return random.choices(["between_meals", "both", "with_meals"], weights=[0.5, 0.3, 0.2])[0]
        return random.choice(["with_meals", "between_meals", "both"])

    @classmethod
    def consistency_postgen(cls, obj, create, extracted, **kwargs):
        """
        Ensure consistency for related fields. If a main food is 'no', related fields are None.
        """
        for prefix in [
            'sweet_sugary_foods', 'cold_drinks_juices', 'fresh_fruit', 'processed_fruit',
            'spreads', 'added_sugars', 'salty_snacks', 'dairy_products', 'vegetables', 'takeaways_processed_foods']:
            if getattr(obj, prefix, None) == 'no':
                for suffix in ['daily', 'weekly', 'timing', 'bedtime']:
                    field = f'{prefix}_{suffix}'
                    if hasattr(obj, field):
                        setattr(obj, field, None)
    """
    DietaryFactory
    A DjangoModelFactory for generating mock DietaryScreening instances for testing purposes.
    This factory simulates realistic dietary screening data, including various food and drink consumption patterns, 
    timings, and frequencies, based on plausible distributions and research data. Includes age-aware distributions
    and dietary risk calculation for connection to dental outcomes.
    Attributes:
        patient: A related PatientFactory instance.
        sweet_sugary_foods: "yes" or "no" indicating sweet/sugary food consumption (age-adjusted distribution).
        sweet_sugary_foods_daily: Daily frequency if consumed.
        sweet_sugary_foods_weekly: Weekly frequency if consumed.
        sweet_sugary_foods_timing: Timing of consumption if consumed.
        sweet_sugary_foods_bedtime: "yes" or "no" if consumed at bedtime.
        takeaways_processed_foods: "yes" or "no" for takeaways/processed foods.
        takeaways_processed_foods_daily: Daily frequency if consumed.
        takeaways_processed_foods_weekly: Weekly frequency if consumed.
        fresh_fruit: "yes" or "no" for fresh fruit consumption (age-adjusted).
        fresh_fruit_daily: Daily frequency if consumed.
        fresh_fruit_weekly: Weekly frequency if consumed.
        fresh_fruit_timing: Timing of consumption if consumed.
        fresh_fruit_bedtime: "yes" or "no" if consumed at bedtime.
        cold_drinks_juices: "yes" or "no" for cold drinks, juices, flavoured water/milk (age-adjusted).
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
        vegetables: "yes" or "no" for vegetables (age-adjusted).
        vegetables_daily: Daily frequency if consumed.
        vegetables_weekly: Weekly frequency if consumed.
        water: "yes" or "no" for water consumption.
        water_timing: Timing of water consumption if consumed.
        water_glasses: Number of glasses consumed daily if consumed.
    Note:
        - Most attributes are conditionally generated based on the main "yes"/"no" field for each section.
        - Frequencies and timings are randomized within plausible ranges.
        - Age-adjusted probabilities reflect realistic consumption patterns by age group.
        - Intended for use in tests and development environments.
    """


    class Meta: # type: ignore
        model = DietaryScreening

    # Can be used standalone or with RelatedFactory
    patient = SubFactory('patient.factory.PatientFactory')

    # Helper methods for age-aware distributions and dietary risk calculation
    @classmethod
    def get_age_adjusted_probability(cls, base_prob, age, adjustment_rules=None):
        """Adjust probabilities based on patient age"""
        if adjustment_rules:
            for age_range, multiplier in adjustment_rules:
                if int(age) in age_range:
                    return min(0.95, max(0.05, base_prob * multiplier))
        return base_prob

    @classmethod
    def calculate_dietary_risk_score(cls, obj):
        """Calculate cariogenic risk based on dietary patterns"""
        risk_score = 0
        
        # High cariogenic foods
        if getattr(obj, 'sweet_sugary_foods', 'no') == 'yes':
            risk_score += 2.5
            if getattr(obj, 'sweet_sugary_foods_bedtime', 'no') == 'yes':
                risk_score += 1.5  # Bedtime consumption is highest risk
            timing = getattr(obj, 'sweet_sugary_foods_timing', '')
            if timing == 'between_meals':
                risk_score += 1.2
            elif timing == 'both':
                risk_score += 0.8
        
        if getattr(obj, 'cold_drinks_juices', 'no') == 'yes':
            risk_score += 2.0
            if getattr(obj, 'cold_drinks_juices_bedtime', 'no') == 'yes':
                risk_score += 1.2
            timing = getattr(obj, 'cold_drinks_juices_timing', '')
            if timing == 'between_meals':
                risk_score += 1.0
            elif timing == 'both':
                risk_score += 0.6
        
        if getattr(obj, 'processed_fruit', 'no') == 'yes':
            risk_score += 1.5
            if getattr(obj, 'processed_fruit_bedtime', 'no') == 'yes':
                risk_score += 1.0
        
        if getattr(obj, 'added_sugars', 'no') == 'yes':
            risk_score += 2.0
            if getattr(obj, 'added_sugars_bedtime', 'no') == 'yes':
                risk_score += 1.0
        
        if getattr(obj, 'spreads', 'no') == 'yes':
            risk_score += 1.0  # Spreads often contain sugars
        
        if getattr(obj, 'takeaways_processed_foods', 'no') == 'yes':
            risk_score += 1.5  # Often high in sugars and acids
        
        # Protective factors
        if getattr(obj, 'water', 'no') == 'yes':
            glasses = getattr(obj, 'water_glasses', '')
            if glasses == '2-4':
                risk_score -= 0.8
            elif glasses == '5+':
                risk_score -= 1.2
            water_timing = getattr(obj, 'water_timing', '')
            if 'after_sweets' in water_timing:
                risk_score -= 0.5
        
        if getattr(obj, 'dairy_products', 'no') == 'yes':
            risk_score -= 0.5  # Calcium and casein protective effects
        
        if getattr(obj, 'vegetables', 'no') == 'yes':
            risk_score -= 0.3  # Fiber and pH buffering
        
        if getattr(obj, 'fresh_fruit', 'no') == 'yes':
            # Fresh fruit is less cariogenic than processed
            timing = getattr(obj, 'fresh_fruit_timing', '')
            if timing == 'with_meals':
                risk_score -= 0.2  # Better when with meals
        
        return max(0, risk_score)

    # Section 1: Sweet/Sugary Foods - age-appropriate for 0-6 years
    sweet_sugary_foods = LazyAttribute(lambda o: "yes" if np.random.binomial(1, 
        p=DietaryFactory.get_age_adjusted_probability(0.50, o.patient.age, 
        [(range(0, 2), 0.5), (range(2, 4), 0.8), (range(4, 7), 1.1)])) == 1 else "no")  # Lower baseline, increasing with age
    sweet_sugary_foods_daily = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'sweet_sugary_foods', 'daily') if o.sweet_sugary_foods == "yes" else None)
    sweet_sugary_foods_weekly = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'sweet_sugary_foods', 'weekly') if o.sweet_sugary_foods == "yes" else None)
    sweet_sugary_foods_timing = LazyAttribute(lambda o: DietaryFactory.get_realistic_timing(o.patient.age, 'sweet_sugary_foods') if o.sweet_sugary_foods == "yes" else None)
    sweet_sugary_foods_bedtime = LazyAttribute(lambda o: (
        "yes" if np.random.binomial(1, p=0.5) == 1 else "no"
    ) if o.sweet_sugary_foods == "yes" else None)

    # Section 2: Take-aways and Processed Foods - limited in young children
    takeaways_processed_foods = LazyAttribute(lambda o: "yes" if np.random.binomial(1, 
        p=DietaryFactory.get_age_adjusted_probability(0.30, o.patient.age, 
        [(range(0, 2), 0.3), (range(2, 4), 0.6), (range(4, 7), 0.9)])) == 1 else "no")  # Increasing with age as diet diversifies
    takeaways_processed_foods_daily = LazyAttribute(lambda o: fake.random_element(elements=["1-3_day", "3-4_day", "4-6_day"]) if o.takeaways_processed_foods == "yes" else None)
    takeaways_processed_foods_weekly = LazyAttribute(lambda o: fake.random_element(elements=["1-3_week", "3-4_week", "4-6_week"]) if o.takeaways_processed_foods == "yes" else None)

    # Section 3: Fresh Fruit - encouraged early, varies by introduction
    fresh_fruit = LazyAttribute(lambda o: "yes" if np.random.binomial(1, 
        p=DietaryFactory.get_age_adjusted_probability(0.60, o.patient.age, 
        [(range(0, 1), 0.3), (range(1, 3), 0.8), (range(3, 7), 1.1)])) == 1 else "no")  # Low in infants, increasing with solid food introduction
    fresh_fruit_daily = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'fresh_fruit', 'daily') if o.fresh_fruit == "yes" else None)
    fresh_fruit_weekly = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'fresh_fruit', 'weekly') if o.fresh_fruit == "yes" else None)
    fresh_fruit_timing = LazyAttribute(lambda o: DietaryFactory.get_realistic_timing(o.patient.age, 'fresh_fruit') if o.fresh_fruit == "yes" else None)
    fresh_fruit_bedtime = LazyAttribute(lambda o: (
        "yes" if np.random.binomial(1, p=0.5) == 1 else "no"
    ) if o.fresh_fruit == "yes" else None)

    # Section 4: Cold Drinks, Juices - limited in infants, increasing with age
    cold_drinks_juices = LazyAttribute(lambda o: "yes" if np.random.binomial(1, 
        p=DietaryFactory.get_age_adjusted_probability(0.40, o.patient.age, 
        [(range(0, 1), 0.2), (range(1, 3), 0.6), (range(3, 7), 1.2)])) == 1 else "no")  # Very low in infants (mostly milk/water), increasing with age
    cold_drinks_juices_daily = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'cold_drinks_juices', 'daily') if o.cold_drinks_juices == "yes" else None)
    cold_drinks_juices_weekly = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'cold_drinks_juices', 'weekly') if o.cold_drinks_juices == "yes" else None)
    cold_drinks_juices_timing = LazyAttribute(lambda o: DietaryFactory.get_realistic_timing(o.patient.age, 'cold_drinks_juices') if o.cold_drinks_juices == "yes" else None)
    cold_drinks_juices_bedtime = LazyAttribute(lambda o: (
        "yes" if np.random.binomial(1, p=0.5) == 1 else "no"
    ) if o.cold_drinks_juices == "yes" else None)

    # Section 5: Processed Fruit
    processed_fruit = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    processed_fruit_daily = LazyAttribute(lambda o: fake.random_element(elements=["1-3_day", "3-4_day", "4-6_day"]) if o.processed_fruit == "yes" else None)
    processed_fruit_weekly = LazyAttribute(lambda o: fake.random_element(elements=["1-3_week", "3-4_week", "4-6_week"]) if o.processed_fruit == "yes" else None)
    processed_fruit_timing = LazyAttribute(lambda o: fake.random_element(elements=["with_meals", "between_meals", "both"]) if o.processed_fruit == "yes" else None)
    processed_fruit_bedtime = LazyAttribute(lambda o: (
        "yes" if np.random.binomial(1, p=0.5) == 1 else "no"
    ) if o.processed_fruit == "yes" else None)

    # Section 6: Spreads
    spreads = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.67) == 1 else "no")
    spreads_daily = LazyAttribute(lambda o: fake.random_element(elements=["1-3_day", "3-4_day", "4-6_day"]) if o.spreads == "yes" else None)
    spreads_weekly = LazyAttribute(lambda o: fake.random_element(elements=["1-3_week", "3-4_week", "4-6_week"]) if o.spreads == "yes" else None)
    spreads_timing = LazyAttribute(lambda o: fake.random_element(elements=["with_meals", "between_meals", "both"]) if o.spreads == "yes" else None)
    spreads_bedtime = LazyAttribute(lambda o: (
        "yes" if np.random.binomial(1, p=0.5) == 1 else "no"
    ) if o.spreads == "yes" else None)

    # Section 7: Added Sugars
    added_sugars = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.73) == 1 else "no")
    added_sugars_daily = LazyAttribute(lambda o: fake.random_element(elements=["1-3_day", "3-4_day", "4-6_day"]) if o.added_sugars == "yes" else None)
    added_sugars_weekly = LazyAttribute(lambda o: fake.random_element(elements=["1-3_week", "3-4_week", "4-6_week"]) if o.added_sugars == "yes" else None)
    added_sugars_timing = LazyAttribute(lambda o: fake.random_element(elements=["with_meals", "between_meals", "both"]) if o.added_sugars == "yes" else None)
    added_sugars_bedtime = LazyAttribute(lambda o: (
        "yes" if np.random.binomial(1, p=0.5) == 1 else "no"
    ) if o.added_sugars == "yes" else None)

    # Section 8: Salty Snacks
    salty_snacks = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.5) == 1 else "no")
    salty_snacks_daily = LazyAttribute(lambda o: fake.random_element(elements=["1-3_day", "3-4_day", "4-6_day"]) if o.salty_snacks == "yes" else None)
    salty_snacks_weekly = LazyAttribute(lambda o: fake.random_element(elements=["1-3_week", "3-4_week", "4-6_week"]) if o.salty_snacks == "yes" else None)
    salty_snacks_timing = LazyAttribute(lambda o: fake.random_element(elements=["with_meals", "between_meals", "both"]) if o.salty_snacks == "yes" else None)

    # Section 9: Dairy Products
    dairy_products = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.60) == 1 else "no")
    dairy_products_daily = LazyAttribute(lambda o: fake.random_element(elements=["1-3_day", "3-4_day", "4-6_day"]) if o.dairy_products == "yes" else None)
    dairy_products_weekly = LazyAttribute(lambda o: fake.random_element(elements=["1-3_week", "3-4_week", "4-6_week"]) if o.dairy_products == "yes" else None)

    # Section 10: Vegetables - challenging in young children, gradual introduction
    vegetables = LazyAttribute(lambda o: "yes" if np.random.binomial(1, 
        p=DietaryFactory.get_age_adjusted_probability(0.45, o.patient.age, 
        [(range(0, 1), 0.4), (range(1, 3), 0.6), (range(3, 5), 0.7), (range(5, 7), 0.9)])) == 1 else "no")  # Gradual acceptance, still challenging in preschoolers
    vegetables_daily = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'vegetables', 'daily') if o.vegetables == "yes" else None)
    vegetables_weekly = LazyAttribute(lambda o: DietaryFactory.get_realistic_frequency(o.patient.age, 'vegetables', 'weekly') if o.vegetables == "yes" else None)

    # Section 11: Water
    water = LazyFunction(lambda: "yes" if np.random.binomial(1, p=0.95) == 1 else "no")
    water_timing = LazyAttribute(lambda o: fake.random_element(elements=["with_meals", "between_meals", "after_sweets", "before_bedtime"]) if o.water == "yes" else None)
    water_glasses = LazyAttribute(lambda o: fake.random_element(elements=["<2", "2-4", "5+"]) if o.water == "yes" else None)
    
    # Usage examples for linked dietary-dental assessments:
    # 1. Standard linked assessment:
    #    patient = PatientFactory()
    #    dietary = DietaryFactory(patient=patient)
    #    dental = DentalFactory(patient=patient)  # Will consider dietary risk automatically
    # 
    # 2. High-risk dietary profile:
    #    high_risk_dietary = DietaryFactory(
    #        patient=patient,
    #        sweet_sugary_foods="yes",
    #        sweet_sugary_foods_bedtime="yes",
    #        cold_drinks_juices="yes",
    #        water="no"
    #    )
    #    dental = DentalFactory(patient=patient)  # Will reflect increased caries risk
