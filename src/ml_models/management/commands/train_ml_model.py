from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ml_models.ml_predictor import MLPRiskPredictor
import os


class Command(BaseCommand):
    help = 'Train the MLP risk predictor model with data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing training data'
        )
        parser.add_argument(
            '--target-column',
            type=str,
            default='risk_level',
            help='Name of the target column (default: risk_level)'
        )
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create a sample training data file'
        )
        parser.add_argument(
            '--sample-size',
            type=int,
            default=1000,
            help='Number of samples to generate (default: 1000)'
        )

    def handle(self, *args, **options):
        predictor = MLPRiskPredictor()
        
        # Create sample data if requested
        if options['create_sample']:
            csv_file = options['csv_file']
            sample_size = options['sample_size']
            
            self.stdout.write(
                self.style.WARNING(f'Creating sample training data with {sample_size} samples...')
            )
            
            try:
                predictor.create_sample_training_data(csv_file, sample_size)
                self.stdout.write(
                    self.style.SUCCESS(f'Sample data created successfully at {csv_file}')
                )
                return
            except Exception as e:
                raise CommandError(f'Error creating sample data: {str(e)}')
        
        # Train the model
        csv_file = options['csv_file']
        target_column = options['target_column']
        
        # Check if file exists
        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file not found: {csv_file}')
        
        self.stdout.write(
            self.style.WARNING(f'Training model with data from {csv_file}...')
        )
        
        try:
            results = predictor.train_from_csv(csv_file, target_column)
            
            self.stdout.write(
                self.style.SUCCESS('Model training completed successfully!')
            )
            
            # Display results
            self.stdout.write(f'Training samples: {results["train_samples"]}')
            self.stdout.write(f'Test samples: {results["test_samples"]}')
            self.stdout.write(f'Train accuracy: {results["train_accuracy"]:.4f}')
            self.stdout.write(f'Test accuracy: {results["test_accuracy"]:.4f}')
            self.stdout.write(f'Features used: {results["features_used"]}')
            
            # Display classification report
            self.stdout.write('\nClassification Report:')
            self.stdout.write(results['classification_report'])
            
            # Display model info
            model_info = predictor.get_model_info()
            self.stdout.write(f'\nModel saved to: {model_info["model_path"]}')
            
        except Exception as e:
            raise CommandError(f'Error training model: {str(e)}')
