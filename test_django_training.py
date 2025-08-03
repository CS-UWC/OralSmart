#!/usr/bin/env python
"""
Test script to demonstrate the enhanced Django management command for ML training.
This shows how to use the terminal-based training with various options.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and display output."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print("-" * 60)
    
    try:
        # Run the command and capture output in real-time
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print(f"\n✅ {description} completed successfully!")
        else:
            print(f"\n❌ {description} failed with return code {process.returncode}")
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"\n❌ Error running command: {str(e)}")
        return False

def main():
    """Demonstrate various training options."""
    
    # Check if we're in the right directory
    if not os.path.exists('src/manage.py'):
        print("❌ Please run this script from the oralsmart project root directory")
        sys.exit(1)
    
    # Path to training data
    training_data = "src/balanced_3class_training_data.csv"
    
    if not os.path.exists(training_data):
        print(f"❌ Training data not found: {training_data}")
        print("Please ensure the training data file exists")
        sys.exit(1)
    
    print("🎯 Enhanced ML Model Training via Django Management Commands")
    print("This script demonstrates various training options available in the terminal.")
    print("\nAvailable training modes:")
    print("1. Full Enhancement (Feature Selection + Hyperparameter Tuning)")
    print("2. Fast Mode (Feature Selection only)")
    print("3. Baseline Mode (No enhancements)")
    print("4. Custom Configuration")
    
    # Ask user which mode to run
    while True:
        try:
            choice = input("\nSelect training mode (1-4) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                print("👋 Goodbye!")
                sys.exit(0)
            
            choice = int(choice)
            if 1 <= choice <= 4:
                break
            else:
                print("❌ Please enter a number between 1-4")
        except ValueError:
            print("❌ Please enter a valid number")
    
    base_cmd = f"cd src && python manage.py train_ml_model {training_data}"
    
    if choice == 1:
        # Full Enhancement Training
        cmd = f"{base_cmd} --feature-selection-method importance --n-features 40"
        description = "Full Enhancement Training (Feature Selection + Hyperparameter Tuning)"
        
    elif choice == 2:
        # Fast Mode
        cmd = f"{base_cmd} --fast --feature-selection-method kbest --n-features 30"
        description = "Fast Training Mode (Feature Selection Only)"
        
    elif choice == 3:
        # Baseline Mode
        cmd = f"{base_cmd} --baseline"
        description = "Baseline Training (No Enhancements)"
        
    elif choice == 4:
        # Custom Configuration
        print("\n🔧 Custom Configuration Options:")
        print("Feature Selection Methods: importance, kbest, rfe")
        print("Number of features: 20-60 recommended")
        
        method = input("Feature selection method (default: importance): ").strip() or "importance"
        n_features = input("Number of features (default: 40): ").strip() or "40"
        
        disable_tuning = input("Disable hyperparameter tuning for faster training? (y/n, default: n): ").strip().lower()
        tuning_flag = " --no-hyperparameter-tuning" if disable_tuning == 'y' else ""
        
        cmd = f"{base_cmd} --feature-selection-method {method} --n-features {n_features}{tuning_flag}"
        description = f"Custom Training ({method} selection, {n_features} features)"
    
    # Run the selected training
    success = run_command(cmd, description)
    
    if success:
        print("\n🎉 Training completed! You can now:")
        print("  • Test predictions using the web interface")
        print("  • Run model evaluation scripts")
        print("  • Deploy the model for production use")
        
        # Show help for other management commands
        print(f"\n💡 Other available commands:")
        print(f"  • cd src && python manage.py train_ml_model --help")
        print(f"  • cd src && python manage.py test_ai_integration")
        print(f"  • cd src && python manage.py export_training_data")
    else:
        print("\n❌ Training failed. Check the error messages above.")

if __name__ == "__main__":
    main()
