import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import os
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2

class ImprovedEyeSenseModel(nn.Module):
    def __init__(self, num_classes=3, use_pretrained=True):
        super(ImprovedEyeSenseModel, self).__init__()
        
        # Use pre-trained ResNet as backbone
        self.backbone = models.resnet50(pretrained=use_pretrained)
        
        # Replace the final fully connected layer
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()  # Remove the original FC layer
        
        # Add custom classifier with dropout for regularization
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
    def forward(self, x):
        # Extract features from backbone
        features = self.backbone(x)
        
        # Classification
        output = self.classifier(features)
        
        return output

class GlaucomaRiskPredictor:
    def __init__(self, model_path=None, num_classes=3):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        self.model = ImprovedEyeSenseModel(num_classes=num_classes)
        self.classes = ['Normal', 'Slightly High', 'High']
        
        # Load model weights if available
        if model_path and os.path.exists(model_path):
            print(f"Loading model from {model_path}")
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                print("Model loaded successfully!")
            except Exception as e:
                print(f"Error loading model: {e}")
                print("Using randomly initialized weights.")
        else:
            print("No pre-trained model found. Using randomly initialized weights.")
            print("Please train the model first for accurate predictions.")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])
        
    def predict(self, image):
        """Predict glaucoma risk from eye image"""
        try:
            # Ensure image is in correct format
            if len(image.shape) == 2:  # Grayscale
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:  # RGBA
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            
            # Preprocess image
            processed = self.transform(image=image)['image']
            processed = processed.unsqueeze(0).to(self.device)
            
            # Prediction
            with torch.no_grad():
                outputs = self.model(processed)
                probabilities = F.softmax(outputs, dim=1)
                confidence, prediction = torch.max(probabilities, 1)
                
            risk_level = self.classes[prediction.item()]
            confidence_score = confidence.item()
            
            return {
                'risk_level': risk_level,
                'confidence': confidence_score,
                'probabilities': probabilities.cpu().numpy()[0].tolist()
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'risk_level': 'Unknown',
                'confidence': 0.0,
                'probabilities': [0.33, 0.33, 0.34],
                'error': str(e)
            }
    
    def analyze_image_quality(self, image):
        """Analyze image quality for better predictions"""
        try:
            # Convert to grayscale for analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Calculate image quality metrics
            brightness = np.mean(gray)
            contrast = np.std(gray)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize scores
            brightness_score = min(1.0, abs(brightness - 127) / 127)  # Ideal around 127
            contrast_score = min(1.0, contrast / 100)  # Higher contrast better
            sharpness_score = min(1.0, sharpness / 1000)  # Higher sharpness better
            
            quality_score = (contrast_score + sharpness_score + (1 - brightness_score)) / 3
            
            return {
                'quality_score': quality_score,
                'brightness': brightness,
                'contrast': contrast,
                'sharpness': sharpness,
                'is_acceptable': quality_score > 0.4 and 50 < brightness < 200
            }
        except Exception as e:
            return {'error': str(e)}