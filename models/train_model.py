import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import os
import json
import time

from models.eye_model import ImprovedEyeSenseModel
from models.data_loader import create_data_loaders

class ModelTrainer:
    def __init__(self, num_classes=3):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ImprovedEyeSenseModel(num_classes=num_classes)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-4)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, patience=5, factor=0.5)
        
        self.train_losses = []
        self.val_accuracies = []
        self.val_losses = []
        
    def train(self, train_loader, val_loader, epochs=50):
        print(f"Training on {self.device}...")
        self.model.to(self.device)
        
        best_accuracy = 0.0
        start_time = time.time()
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            running_loss = 0.0
            correct_train = 0
            total_train = 0
            
            for batch_idx, (images, labels) in enumerate(train_loader):
                images, labels = images.to(self.device), labels.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                
                running_loss += loss.item()
                
                # Training accuracy
                _, predicted = torch.max(outputs.data, 1)
                total_train += labels.size(0)
                correct_train += (predicted == labels).sum().item()
                
                if batch_idx % 10 == 0:
                    print(f'Epoch {epoch+1}/{epochs}, Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.4f}')
            
            # Validation phase
            val_accuracy, val_loss = self.validate(val_loader)
            train_accuracy = correct_train / total_train
            train_loss = running_loss / len(train_loader)
            
            self.train_losses.append(train_loss)
            self.val_accuracies.append(val_accuracy)
            self.val_losses.append(val_loss)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            print(f'\nEpoch [{epoch+1}/{epochs}]')
            print(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_accuracy:.4f}')
            print(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.4f}')
            print(f'  LR: {self.optimizer.param_groups[0]["lr"]:.6f}')
            
            # Save best model
            if val_accuracy > best_accuracy:
                best_accuracy = val_accuracy
                self.save_model('models/best_eyesense_model.pth')
                print(f'  🎯 New best model saved! Accuracy: {best_accuracy:.4f}')
        
        # Training completed
        training_time = time.time() - start_time
        print(f"\nTraining completed in {training_time:.2f} seconds")
        print(f"Best validation accuracy: {best_accuracy:.4f}")
        
        # Save final model
        self.save_model('models/final_eyesense_model.pth')
        self.plot_training_history()
        
        return self.train_losses, self.val_accuracies
    
    def validate(self, val_loader):
        self.model.eval()
        correct = 0
        total = 0
        running_loss = 0.0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                running_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = correct / total
        avg_loss = running_loss / len(val_loader)
        
        return accuracy, avg_loss
    
    def save_model(self, path):
        """Save model and training info"""
        torch.save(self.model.state_dict(), path)
        
        # Save training history
        history = {
            'train_losses': self.train_losses,
            'val_accuracies': self.val_accuracies,
            'val_losses': self.val_losses
        }
        
        with open('models/training_history.json', 'w') as f:
            json.dump(history, f)
        
        print(f"Model saved to {path}")
    
    def plot_training_history(self):
        """Plot training history"""
        plt.figure(figsize=(15, 5))
        
        # Plot loss
        plt.subplot(1, 2, 1)
        plt.plot(self.train_losses, label='Training Loss')
        plt.plot(self.val_losses, label='Validation Loss')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # Plot accuracy
        plt.subplot(1, 2, 2)
        plt.plot(self.val_accuracies, label='Validation Accuracy', color='orange')
        plt.title('Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('models/training_history.png', dpi=300, bbox_inches='tight')
        plt.show()

def evaluate_model(model, test_loader, class_names):
    """Evaluate model performance"""
    model.eval()
    all_predictions = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(model.device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())
    
    # Classification report
    print("Classification Report:")
    print(classification_report(all_labels, all_predictions, target_names=class_names))
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_predictions)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('models/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    try:
        # Create data loaders
        train_loader, val_loader, class_names = create_data_loaders(batch_size=16)
        
        print(f"Training with {len(class_names)} classes: {class_names}")
        print(f"Training samples: {len(train_loader.dataset)}")
        print(f"Validation samples: {len(val_loader.dataset)}")
        
        # Train model
        trainer = ModelTrainer(num_classes=len(class_names))
        train_losses, val_accuracies = trainer.train(train_loader, val_loader, epochs=20)
        
        print("Training completed!")
        print(f"Final Validation Accuracy: {val_accuracies[-1]:.4f}")
        
        # Evaluate model
        print("\nEvaluating model...")
        evaluate_model(trainer.model, val_loader, class_names)
        
    except Exception as e:
        print(f"Error during training: {e}")
        print("Make sure the dataset is properly set up in data/raw/")