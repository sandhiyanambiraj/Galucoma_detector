import torch
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.eye_model import GlaucomaRiskPredictor

def predict_single_image(image_path, model_path="models/best_eyesense_model.pth"):
    """Predict glaucoma risk for a single image"""
    
    # Initialize predictor
    predictor = GlaucomaRiskPredictor(model_path=model_path)
    
    # Load and preprocess image
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Analyze image quality
        quality_result = predictor.analyze_image_quality(image)
        print("Image Quality Analysis:")
        print(f"  Quality Score: {quality_result.get('quality_score', 0):.3f}")
        print(f"  Brightness: {quality_result.get('brightness', 0):.1f}")
        print(f"  Contrast: {quality_result.get('contrast', 0):.1f}")
        print(f"  Sharpness: {quality_result.get('sharpness', 0):.1f}")
        print(f"  Acceptable: {quality_result.get('is_acceptable', False)}")
        
        # Predict glaucoma risk
        result = predictor.predict(image)
        
        print("\nGlaucoma Risk Prediction:")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Confidence: {result['confidence']:.3f}")
        print(f"  Probabilities: {result['probabilities']}")
        
        # Display results
        display_prediction(image, result, quality_result)
        
        return result
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

def display_prediction(image, result, quality_result):
    """Display the prediction results with visualization"""
    plt.figure(figsize=(15, 5))
    
    # Original image
    plt.subplot(1, 3, 1)
    plt.imshow(image)
    plt.title('Input Image')
    plt.axis('off')
    
    # Risk level
    plt.subplot(1, 3, 2)
    risk_level = result['risk_level']
    confidence = result['confidence']
    probabilities = result['probabilities']
    
    colors = ['green', 'orange', 'red']
    risk_labels = ['Normal', 'Slightly High', 'High']
    
    bars = plt.bar(risk_labels, probabilities, color=colors, alpha=0.7)
    plt.title(f'Risk Probabilities\nPredicted: {risk_level} ({confidence:.1%})')
    plt.ylabel('Probability')
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for bar, prob in zip(bars, probabilities):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{prob:.3f}', ha='center', va='bottom')
    
    # Quality metrics
    plt.subplot(1, 3, 3)
    quality_metrics = ['Brightness', 'Contrast', 'Sharpness']
    quality_values = [
        quality_result.get('brightness', 0),
        quality_result.get('contrast', 0),
        quality_result.get('sharpness', 0)
    ]
    
    # Normalize for display
    normalized_values = [
        min(1.0, quality_values[0] / 255),
        min(1.0, quality_values[1] / 100),
        min(1.0, quality_values[2] / 1000)
    ]
    
    bars = plt.bar(quality_metrics, normalized_values, color=['blue', 'purple', 'cyan'])
    plt.title('Image Quality Metrics')
    plt.ylabel('Normalized Score')
    plt.xticks(rotation=45)
    plt.ylim(0, 1)
    
    # Add value labels
    for bar, value, norm_value in zip(bars, quality_values, normalized_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{value:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Test with a sample image
    sample_image = "data/raw/synthetic/normal_0.jpg"  # Change this path as needed
    
    if os.path.exists(sample_image):
        print("Testing prediction with sample image...")
        result = predict_single_image(sample_image)
    else:
        print(f"Sample image not found at {sample_image}")
        print("Please provide a valid image path.")