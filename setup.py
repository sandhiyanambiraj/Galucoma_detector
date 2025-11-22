import os
import subprocess
import sys
import zipfile

def setup_environment():
    """Setup the EyeSense project environment"""
    print("Setting up EyeSense environment...")
    
    # Create necessary directories
    directories = [
        'data/raw',
        'data/processed', 
        'models',
        'backend',
        'frontend',
        'uploads',
        'static',
        'tests'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Install requirements
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        print("Please install manually: pip install -r requirements.txt")
    
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Download the dataset from Kaggle:")
    print("   https://www.kaggle.com/datasets/andrewmvd/ocular-disease-recognition-odir5k")
    print("2. Extract to 'data/raw' folder")
    print("3. Train model: python models/train_model.py")
    print("4. Run: run.bat")

if __name__ == "__main__":
    setup_environment()