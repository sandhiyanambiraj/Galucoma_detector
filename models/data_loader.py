import os
import kaggle
import zipfile
import torch
from torch.utils.data import Dataset, DataLoader
import cv2
import pandas as pd
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
from PIL import Image
import glob
import random

class EyeDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        self.class_names = ['Normal', 'Glaucoma', 'Other']
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
                
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if self.transform:
                image = self.transform(image=image)['image']
                
            return image, label
            
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Return a dummy image if loading fails
            dummy_image = np.ones((224, 224, 3), dtype=np.uint8) * 128
            if self.transform:
                dummy_image = self.transform(image=dummy_image)['image']
            return dummy_image, label

def download_kaggle_dataset():
    """Download the Ocular Disease Recognition dataset from Kaggle"""
    dataset_name = "andrewmvd/ocular-disease-recognition-odir5k"
    download_path = "data/raw"
    
    os.makedirs(download_path, exist_ok=True)
    
    try:
        print("Downloading dataset from Kaggle...")
        kaggle.api.dataset_download_files(dataset_name, path=download_path, unzip=True)
        print("Dataset downloaded successfully!")
        return True
    except Exception as e:
        print(f"Kaggle download failed: {e}")
        print("Please download manually from:")
        print("https://www.kaggle.com/datasets/andrewmvd/ocular-disease-recognition-odir5k")
        return False

def create_synthetic_samples():
    """Create synthetic eye images for demonstration"""
    print("Creating synthetic samples for prototype...")
    os.makedirs('data/raw/synthetic', exist_ok=True)
    
    # Create different colored circles to simulate eyes
    for i in range(50):
        # Normal (greenish)
        img = np.zeros((224, 224, 3), dtype=np.uint8)
        cv2.circle(img, (112, 112), 50, (0, 100, 0), -1)
        cv2.imwrite(f'data/raw/synthetic/normal_{i}.jpg', img)
        
        # Glaucoma (reddish)
        img = np.zeros((224, 224, 3), dtype=np.uint8)
        cv2.circle(img, (112, 112), 50, (0, 0, 150), -1)
        cv2.imwrite(f'data/raw/synthetic/glaucoma_{i}.jpg', img)
        
        # Other (yellowish)
        img = np.zeros((224, 224, 3), dtype=np.uint8)
        cv2.circle(img, (112, 112), 50, (0, 150, 150), -1)
        cv2.imwrite(f'data/raw/synthetic/other_{i}.jpg', img)

def prepare_eye_dataset(data_path="data/raw"):
    """Prepare the eye dataset for training with glaucoma focus"""
    
    # If dataset doesn't exist, create synthetic data
    if not os.path.exists(data_path) or len(glob.glob(os.path.join(data_path, "*.jpg"))) == 0:
        print("No dataset found. Creating synthetic data for demonstration...")
        create_synthetic_samples()
        data_path = "data/raw/synthetic"
    
    images = []
    labels = []
    
    # Map filenames to labels
    for image_path in glob.glob(os.path.join(data_path, "**", "*.jpg"), recursive=True):
        filename = os.path.basename(image_path).lower()
        
        if 'normal' in filename:
            label = 0
        elif 'glaucoma' in filename:
            label = 1
        else:
            label = 2  # Other
            
        images.append(image_path)
        labels.append(label)
    
    print(f"Found {len(images)} images")
    print(f"Class distribution: Normal: {labels.count(0)}, Glaucoma: {labels.count(1)}, Other: {labels.count(2)}")
    
    return images, labels, ['Normal', 'Glaucoma', 'Other']

def create_data_loaders(batch_size=32, data_path="data/raw"):
    """Create data loaders for training and validation"""
    
    # Get images and labels
    images, labels, class_names = prepare_eye_dataset(data_path)
    
    if len(images) == 0:
        raise ValueError("No images found in dataset!")
    
    # Split data
    train_images, val_images, train_labels, val_labels = train_test_split(
        images, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Data transformations
    train_transform = A.Compose([
        A.Resize(224, 224),
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.Rotate(limit=15, p=0.3),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])
    
    val_transform = A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])
    
    # Create datasets
    train_dataset = EyeDataset(train_images, train_labels, transform=train_transform)
    val_dataset = EyeDataset(val_images, val_labels, transform=val_transform)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader, class_names

# Test data loading
if __name__ == "__main__":
    train_loader, val_loader, classes = create_data_loaders()
    print(f"Classes: {classes}")
    print(f"Train batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}")