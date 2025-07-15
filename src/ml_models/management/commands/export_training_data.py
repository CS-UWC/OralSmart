import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from assessments.models import DentalScreening, DietaryScreening
from patient.models import Patient
from ml_models.ml_predictor import MLPRiskPredictor


class Command(BaseCommand):
    help = 'Export database records to CSV format suitable for ML model training with 3-class risk levels (low/medium/high)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='training_data.csv',
            help='Output CSV file name (default: training_data.csv)'
        )
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Output directory path (default: project root)'
        )
        parser.add_argument(
            '--min-dmft',
            type=int,
            default=None,
            help='Minimum DMFT score for high risk classification'
        )
        parser.add_argument(
            '--risk-threshold',
            type=int,
            default=None,
            help='Custom high-risk threshold for 3-class classification (medium threshold will be 65% of this value)'
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
            
            # Skip if no data at all or only incomplete data (unless include_incomplete is True)
            if not has_dental and not has_dietary:
                continue
            
            if not options['include_incomplete'] and not (has_dental and has_dietary):
                continue
            
            # Prepare features using the ML predictor
            try:
                features = predictor.prepare_features(dental_data, dietary_data)
                feature_dict = dict(zip(predictor.feature_names, features[0]))
                
                # Calculate risk level
                risk_level = self._calculate_risk_level(
                    feature_dict, 
                    options.get('min_dmft'),
                    options.get('risk_threshold')
                )
                
                # Add risk level to the record
                feature_dict['risk_level'] = risk_level
                
                # Track risk statistics
                stats[f'{risk_level}_risk'] += 1
                
                training_records.append(feature_dict)
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Error processing patient {patient.id}: {str(e)}") # type: ignore
                )
                continue
        
        # Display statistics
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("EXPORT STATISTICS"))
        self.stdout.write("="*50)
        self.stdout.write(f"Total patients: {stats['total_patients']}")
        self.stdout.write(f"With both assessments: {stats['with_both']}")
        self.stdout.write(f"With dental only: {stats['with_dental_only']}")
        self.stdout.write(f"With dietary only: {stats['with_dietary_only']}")
        self.stdout.write(f"With no assessments: {stats['with_neither']}")
        self.stdout.write(f"Records for training: {len(training_records)}")
        self.stdout.write(f"Low risk: {stats['low_risk']}")
        self.stdout.write(f"Medium risk: {stats['medium_risk']}")
        self.stdout.write(f"High risk: {stats['high_risk']}")
        
        if len(training_records) == 0:
            raise CommandError('No valid training records found')
        
        # Check risk distribution for 3-class balance
        total_records = len(training_records)
        high_ratio = stats['high_risk'] / total_records if total_records > 0 else 0
        medium_ratio = stats['medium_risk'] / total_records if total_records > 0 else 0
        low_ratio = stats['low_risk'] / total_records if total_records > 0 else 0
        
        # Warn if any class is severely underrepresented (< 10%) or overrepresented (> 70%)
        if any(ratio < 0.1 or ratio > 0.7 for ratio in [high_ratio, medium_ratio, low_ratio]):
            self.stdout.write(
                self.style.WARNING(
                    f"Warning: Imbalanced dataset "
                    f"(Low: {low_ratio:.1%}, Medium: {medium_ratio:.1%}, High: {high_ratio:.1%}). "
                    "Consider adjusting risk thresholds or collecting more data."
                )
            )
        
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS("\nDry run completed. No file created."))
            return
        
        # Write to CSV
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                if training_records:
                    fieldnames = list(training_records[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(training_records)
            
            self.stdout.write(
                self.style.SUCCESS(f"\nTraining data exported to: {output_file}")
            )
            self.stdout.write(f"Features: {len(predictor.feature_names)}")
            self.stdout.write(f"Records: {len(training_records)}")
            
        except Exception as e:
            raise CommandError(f'Error writing CSV file: {str(e)}')

    def _calculate_risk_level(self, feature_dict, min_dmft=None, risk_threshold=None):
        """
        Calculate risk level based on feature values.
        
        Args:
            feature_dict: Dictionary of feature values
            min_dmft: Minimum DMFT score for high risk
            risk_threshold: Custom threshold for risk calculation
            
        Returns:
            str: 'low', 'medium', or 'high'
        """
        # DMFT score risk factor
        dmft_score = feature_dict.get('total_dmft_score', 0)
        
        # Use custom DMFT threshold if provided
        dmft_threshold = min_dmft if min_dmft is not None else 8
        
        # Immediate high risk if DMFT is too high
        if dmft_score >= dmft_threshold:
            return 'high'
        
        # Calculate composite risk score
        risk_score = 0
        
        # Dental risk factors (binary fields)
        dental_risk_factors = [
            'plaque', 'dry_mouth', 'enamel_defects', 'enamel_change', 
            'dentin_discoloration', 'white_spot_lesions', 'cavitated_lesions',
            'multiple_restorations', 'missing_teeth'
        ]
        
        for factor in dental_risk_factors:
            if feature_dict.get(factor, 0) == 1:
                risk_score += 2  # Higher weight for clinical findings
        
        # Protective factors (reduce risk)
        protective_factors = [
            'fluoride_water', 'fluoride_toothpaste', 'topical_fluoride',
            'regular_checkups', 'sealed_pits'
        ]
        
        for factor in protective_factors:
            if feature_dict.get(factor, 0) == 1:
                risk_score -= 1  # Protective factors reduce risk
        
        # Dietary risk factors
        dietary_risk_factors = [
            'sweet_sugary_foods', 'sweet_sugary_foods_bedtime',
            'cold_drinks_juices', 'cold_drinks_juices_bedtime',
            'processed_fruit', 'processed_fruit_bedtime',
            'spreads', 'spreads_bedtime',
            'added_sugars', 'added_sugars_bedtime'
        ]
        
        for factor in dietary_risk_factors:
            if feature_dict.get(factor, 0) == 1:
                risk_score += 1
        
        # High frequency consumption patterns
        frequency_factors = [
            'sweet_sugary_foods_daily', 'sweet_sugary_foods_weekly',
            'cold_drinks_juices_daily', 'cold_drinks_juices_weekly',
            'processed_fruit_daily', 'processed_fruit_weekly'
        ]
        
        for factor in frequency_factors:
            freq_value = feature_dict.get(factor, 0)
            if freq_value >= 3:  # High frequency
                risk_score += 1
        
        # Social risk factors
        if feature_dict.get('special_needs', 0) == 1:
            risk_score += 2
        
        if feature_dict.get('caregiver_treatment', 0) == 0:  # No caregiver treatment
            risk_score += 1
        
        # DMFT contribution
        risk_score += dmft_score * 0.5  # Each DMFT point adds 0.5 to risk
        
        # Data availability penalty (uncertainty increases risk threshold)
        has_dental = feature_dict.get('has_dental_data', 0)
        has_dietary = feature_dict.get('has_dietary_data', 0)
        data_completeness = has_dental + has_dietary
        
        # Use custom thresholds if provided, otherwise calculate based on data completeness
        if risk_threshold is not None:
            # For 3-class system, treat risk_threshold as the high threshold
            # Medium threshold is typically 60-70% of high threshold
            high_threshold = risk_threshold
            medium_threshold = risk_threshold * 0.65  # 65% of high threshold
        else:
            # More conservative thresholds when data is incomplete
            base_high_threshold = 8
            if data_completeness == 2:  # Both assessments
                high_threshold = base_high_threshold
                medium_threshold = base_high_threshold * 0.65  # ~5.2
            elif data_completeness == 1:  # Only one assessment
                high_threshold = base_high_threshold - 2  # 6
                medium_threshold = (base_high_threshold - 2) * 0.65  # ~3.9
            else:  # No assessments (shouldn't happen if validation works)
                high_threshold = base_high_threshold - 4  # 4
                medium_threshold = (base_high_threshold - 4) * 0.65  # ~2.6
        
        # Return 3-class risk level
        if risk_score >= high_threshold:
            return 'high'
        elif risk_score >= medium_threshold:
            return 'medium'
        else:
            return 'low'
