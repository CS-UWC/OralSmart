import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from assessments.models import DentalScreening, DietaryScreening
from patient.models import Patient
from ml_models.ml_predictor import MLPRiskPredictor


class Command(BaseCommand):
    help = 'Export database records to CSV format with no encoding (plain ASCII/system default)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='training_data_plain.csv',
            help='Output CSV file name (default: training_data_plain.csv)'
        )
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Output directory path (default: project root)'
        )
        parser.add_argument(
            '--include-incomplete',
            action='store_true',
            help='Include records with only dental or only dietary data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show statistics without creating the file'
        )

    def handle(self, *args, **options):
        # Initialize ML predictor to get feature names
        predictor = MLPRiskPredictor()
        
        # Determine output path
        if options['path']:
            output_dir = options['path']
        else:
            output_dir = settings.BASE_DIR
        
        output_file = os.path.join(output_dir, options['output'])
        
        # Get all patients
        patients = Patient.objects.all()
        
        if not patients.exists():
            raise CommandError('No patients found in database')
        
        self.stdout.write(f"Found {patients.count()} patients in database")
        
        # Collect training data
        training_records = []
        stats = {
            'total_patients': patients.count(),
            'with_dental_only': 0,
            'with_dietary_only': 0,
            'with_both': 0,
            'with_neither': 0,
            'low_risk': 0,
            'medium_risk': 0,
            'high_risk': 0
        }
        
        for patient in patients:
            # Get dental and dietary data
            dental_data = DentalScreening.objects.filter(patient=patient).first()
            dietary_data = DietaryScreening.objects.filter(patient=patient).first()
            
            # Track statistics
            has_dental = dental_data is not None
            has_dietary = dietary_data is not None
            
            if has_dental and has_dietary:
                stats['with_both'] += 1
            elif has_dental:
                stats['with_dental_only'] += 1
            elif has_dietary:
                stats['with_dietary_only'] += 1
            else:
                stats['with_neither'] += 1
                if not options['include_incomplete']:
                    continue  # Skip patients with no assessment data
            
            # Skip if no data at all
            if not has_dental and not has_dietary:
                continue
            
            # Skip if only incomplete data (unless include_incomplete is True)
            if not options['include_incomplete'] and not (has_dental and has_dietary):
                continue
            
            # Prepare feature dictionary
            try:
                feature_dict = {}
                
                # Data availability indicators
                feature_dict['has_dental_data'] = 1 if has_dental else 0
                feature_dict['has_dietary_data'] = 1 if has_dietary else 0

                # Process dental data
                if dental_data:
                    # Binary dental fields
                    dental_binary_fields = [
                        'sa_citizen', 'special_needs', 'caregiver_treatment',
                        'appliance', 'plaque', 'dry_mouth', 'enamel_defects',
                        'fluoride_water', 'fluoride_toothpaste', 'topical_fluoride',
                        'regular_checkups', 'sealed_pits', 'restorative_procedures',
                        'enamel_change', 'dentin_discoloration', 'white_spot_lesions',
                        'cavitated_lesions', 'multiple_restorations', 'missing_teeth'
                    ]
                    
                    for field in dental_binary_fields:
                        value = getattr(dental_data, field, 'no')
                        feature_dict[field] = 1 if value == 'yes' else 0

                    # DMFT score from teeth_data
                    dmft_result = predictor.calculate_dmft_score(dental_data.teeth_data)
                    feature_dict['total_dmft_score'] = dmft_result['dmft']
                else:
                    # Set all dental fields to 0 if no dental data
                    dental_fields = [
                        'sa_citizen', 'special_needs', 'caregiver_treatment',
                        'appliance', 'plaque', 'dry_mouth', 'enamel_defects',
                        'fluoride_water', 'fluoride_toothpaste', 'topical_fluoride',
                        'regular_checkups', 'sealed_pits', 'restorative_procedures',
                        'enamel_change', 'dentin_discoloration', 'white_spot_lesions',
                        'cavitated_lesions', 'multiple_restorations', 'missing_teeth'
                    ]
                    for field in dental_fields:
                        feature_dict[field] = 0
                    feature_dict['total_dmft_score'] = 0

                # Process dietary data
                if dietary_data:
                    # Yes/no dietary fields
                    dietary_yes_no_fields = [
                        'sweet_sugary_foods', 'sweet_sugary_foods_bedtime',
                        'takeaways_processed_foods',
                        'fresh_fruit', 'fresh_fruit_bedtime',
                        'cold_drinks_juices', 'cold_drinks_juices_bedtime',
                        'processed_fruit', 'processed_fruit_bedtime',
                        'spreads', 'spreads_bedtime',
                        'added_sugars', 'added_sugars_bedtime',
                        'salty_snacks',
                        'dairy_products',
                        'vegetables',
                        'water'
                    ]
                    
                    for field in dietary_yes_no_fields:
                        value = getattr(dietary_data, field, 'no')
                        feature_dict[field] = 1 if value == 'yes' else 0
                    
                    # Encoded dietary fields
                    dietary_text_fields = [
                        'sweet_sugary_foods_daily', 'sweet_sugary_foods_weekly', 'sweet_sugary_foods_timing',
                        'takeaways_processed_foods_daily', 'takeaways_processed_foods_weekly',
                        'fresh_fruit_daily', 'fresh_fruit_weekly', 'fresh_fruit_timing',
                        'cold_drinks_juices_daily', 'cold_drinks_juices_weekly', 'cold_drinks_juices_timing',
                        'processed_fruit_daily', 'processed_fruit_weekly', 'processed_fruit_timing',
                        'spreads_daily', 'spreads_weekly', 'spreads_timing',
                        'added_sugars_daily', 'added_sugars_weekly', 'added_sugars_timing',
                        'salty_snacks_daily', 'salty_snacks_weekly', 'salty_snacks_timing',
                        'dairy_products_daily', 'dairy_products_weekly',
                        'vegetables_daily', 'vegetables_weekly',
                        'water_timing', 'water_glasses'
                    ]
                    
                    for field in dietary_text_fields:
                        value = getattr(dietary_data, field, None)
                        feature_dict[field] = predictor._encode_frequency_quantity(value)
                else:
                    # Set all dietary fields to 0 if no dietary data
                    dietary_fields = [
                        'sweet_sugary_foods', 'sweet_sugary_foods_bedtime',
                        'sweet_sugary_foods_daily', 'sweet_sugary_foods_weekly', 'sweet_sugary_foods_timing',
                        'takeaways_processed_foods', 'takeaways_processed_foods_daily', 'takeaways_processed_foods_weekly',
                        'fresh_fruit', 'fresh_fruit_bedtime', 'fresh_fruit_daily', 'fresh_fruit_weekly', 'fresh_fruit_timing',
                        'cold_drinks_juices', 'cold_drinks_juices_bedtime', 'cold_drinks_juices_daily', 'cold_drinks_juices_weekly', 'cold_drinks_juices_timing',
                        'processed_fruit', 'processed_fruit_bedtime', 'processed_fruit_daily', 'processed_fruit_weekly', 'processed_fruit_timing',
                        'spreads', 'spreads_bedtime', 'spreads_daily', 'spreads_weekly', 'spreads_timing',
                        'added_sugars', 'added_sugars_bedtime', 'added_sugars_daily', 'added_sugars_weekly', 'added_sugars_timing',
                        'salty_snacks', 'salty_snacks_daily', 'salty_snacks_weekly', 'salty_snacks_timing',
                        'dairy_products', 'dairy_products_daily', 'dairy_products_weekly',
                        'vegetables', 'vegetables_daily', 'vegetables_weekly',
                        'water', 'water_timing', 'water_glasses'
                    ]
                    for field in dietary_fields:
                        feature_dict[field] = 0

                # Calculate basic risk level (simplified)
                risk_score = 0
                
                # Major risk factors
                major_risk_fields = ['cavitated_lesions', 'multiple_restorations', 'missing_teeth', 
                                   'enamel_change', 'dentin_discoloration', 'white_spot_lesions']
                for field in major_risk_fields:
                    if feature_dict.get(field, 0) == 1:
                        risk_score += 2
                
                # Dietary risk factors
                dietary_risk_fields = ['sweet_sugary_foods', 'cold_drinks_juices', 'processed_fruit', 'added_sugars']
                for field in dietary_risk_fields:
                    if feature_dict.get(field, 0) == 1:
                        risk_score += 1
                
                # Determine risk level
                if risk_score >= 8:
                    risk_level = 'high'
                elif risk_score >= 5:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                feature_dict['risk_level'] = risk_level
                stats[f'{risk_level}_risk'] += 1
                
                training_records.append(feature_dict)
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Error processing patient {patient.pk}: {str(e)}")
                )
                continue
        
        # Display statistics
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("PLAIN CSV EXPORT STATISTICS"))
        self.stdout.write("="*50)
        self.stdout.write(f"Total patients: {stats['total_patients']}")
        self.stdout.write(f"With both assessments: {stats['with_both']}")
        self.stdout.write(f"With dental only: {stats['with_dental_only']}")
        self.stdout.write(f"With dietary only: {stats['with_dietary_only']}")
        self.stdout.write(f"Records for training: {len(training_records)}")
        self.stdout.write(f"Low risk: {stats['low_risk']}")
        self.stdout.write(f"Medium risk: {stats['medium_risk']}")
        self.stdout.write(f"High risk: {stats['high_risk']}")
        
        if len(training_records) == 0:
            raise CommandError('No valid training records found')
        
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS("\nDry run completed. No file created."))
            return
        
        # Write to CSV with NO encoding specified (uses system default)
        try:
            with open(output_file, 'w', newline='') as csvfile:
                if training_records:
                    fieldnames = list(training_records[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(training_records)
            
            self.stdout.write(
                self.style.SUCCESS(f"\nPlain CSV exported to: {output_file}")
            )
            self.stdout.write("Encoding: System default (no explicit encoding)")
            self.stdout.write("Features: 68 (all available features)")
            self.stdout.write(f"Records: {len(training_records)}")
            
        except Exception as e:
            raise CommandError(f'Error writing CSV file: {str(e)}')
