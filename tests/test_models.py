import pytest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.eye_model import GlaucomaRiskPredictor
from models.data_loader import create_synthetic_samples

def test_model_initialization():
    """Test model initialization"""
    predictor = GlaucomaRiskPredictor()
    assert predictor is not None
    assert hasattr(predictor, 'model')
    assert hasattr(predictor, 'device')

def test_image_quality_analysis():
    """Test image quality analysis"""
    predictor = GlaucomaRiskPredictor()
    
    # Create test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    quality_result = predictor.analyze_image_quality(test_image)
    
    assert 'quality_score' in quality_result
    assert 'brightness' in quality_result
    assert 'contrast' in quality_result
    assert 'sharpness' in quality_result
    assert 'is_acceptable' in quality_result
    
    # Check value ranges
    assert 0 <= quality_result['quality_score'] <= 1
    assert 0 <= quality_result['brightness'] <= 255

def test_prediction_output_format():
    """Test prediction output format"""
    predictor = GlaucomaRiskPredictor()
    
    # Create test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    result = predictor.predict(test_image)
    
    assert 'risk_level' in result
    assert 'confidence' in result
    assert 'probabilities' in result
    
    # Check risk level is one of expected values
    assert result['risk_level'] in ['Normal', 'Slightly High', 'High', 'Unknown']
    
    # Check confidence range
    assert 0 <= result['confidence'] <= 1
    
    # Check probabilities sum to approximately 1
    assert abs(sum(result['probabilities']) - 1.0) < 0.01

def test_synthetic_data_creation():
    """Test synthetic data creation"""
    create_synthetic_samples()
    
    # Check if synthetic directory was created
    assert os.path.exists('data/raw/synthetic')
    
    # Check if sample images were created
    normal_images = [f for f in os.listdir('data/raw/synthetic') if 'normal' in f]
    glaucoma_images = [f for f in os.listdir('data/raw/synthetic') if 'glaucoma' in f]
    other_images = [f for f in os.listdir('data/raw/synthetic') if 'other' in f]
    
    assert len(normal_images) > 0
    assert len(glaucoma_images) > 0
    assert len(other_images) > 0

if __name__ == "__main__":
    pytest.main([__file__])