from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
from PIL import Image
import io
import os
from datetime import datetime
import logging
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock database for storage
users_db = {}
analysis_history = {}

app = FastAPI(title="EyeSense API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock AI predictor for demonstration
class MockPredictor:
    def predict(self, image):
        try:
            # Simulate AI analysis with realistic probabilities
            risk_levels = ['Normal', 'Slightly High', 'High']
            
            # Generate random but realistic probabilities
            base_prob = [0.7, 0.2, 0.1]  # Mostly normal
            
            # Add some randomness for demo
            if random.random() < 0.3:  # 30% chance of higher risk
                base_prob = [0.3, 0.4, 0.3]
            
            # Normalize probabilities to sum to 1
            total = sum(base_prob)
            probabilities = [p/total for p in base_prob]
            
            risk_index = random.choices(range(3), weights=probabilities)[0]
            confidence = probabilities[risk_index] + random.uniform(0.1, 0.2)
            confidence = min(confidence, 0.95)
            
            return {
                'risk_level': risk_levels[risk_index],
                'confidence': float(confidence),  # Convert to Python float
                'probabilities': [float(p) for p in probabilities]  # Convert to Python float
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'risk_level': 'Normal',
                'confidence': 0.85,
                'probabilities': [0.85, 0.10, 0.05]
            }
    
    def analyze_image_quality(self, image):
        try:
            # Convert to grayscale for analysis if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Calculate basic quality metrics
            brightness = np.mean(gray)
            contrast = np.std(gray)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var() if gray.size > 0 else 100
            
            # Normalize quality score
            quality_score = min(1.0, (contrast / 100 + sharpness / 1000) / 2)
            
            return {
                'quality_score': float(quality_score),  # Convert to Python float
                'brightness': float(brightness),        # Convert to Python float
                'contrast': float(contrast),            # Convert to Python float
                'sharpness': float(sharpness),          # Convert to Python float
                'is_acceptable': bool(quality_score > 0.4)  # Convert to Python bool
            }
        except Exception as e:
            logger.error(f"Quality analysis error: {e}")
            return {
                'quality_score': 0.8,
                'brightness': 127.0,
                'contrast': 50.0,
                'sharpness': 500.0,
                'is_acceptable': True
            }

predictor = MockPredictor()

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

@app.get("/")
async def root():
    return {"message": "EyeSense API - AI Powered Eye Health Monitoring", "status": "active"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "message": "Backend is running perfectly!"
    }

@app.post("/api/analyze-eye")
async def analyze_eye_image(
    file: UploadFile = File(...),
    user_id: str = "demo_user"
):
    try:
        logger.info(f"📸 Received analysis request from {user_id}")
        
        # Read and validate image
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file received")
        
        # Convert bytes to image
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array
        image_np = np.array(image)
        logger.info(f"🖼️ Image shape: {image_np.shape}")
        
        # Handle different image formats
        if len(image_np.shape) == 2:  # Grayscale
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
        elif image_np.shape[2] == 4:  # RGBA
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        
        logger.info(f"✅ Image processed successfully: {image_np.shape}")
        
        # Analyze image quality
        quality_result = predictor.analyze_image_quality(image_np)
        logger.info(f"📊 Quality analysis: {quality_result}")
        
        # Analyze image for glaucoma risk
        result = predictor.predict(image_np)
        logger.info(f"🔬 Risk analysis: {result}")
        
        # Generate recommendations
        recommendations = generate_recommendations(result, quality_result)
        
        # Prepare analysis data
        analysis_data = {
            'image_info': {
                'size': [int(dim) for dim in image_np.shape],  # Convert to Python int
                'quality_score': float(quality_result.get('quality_score', 0)),
                'is_acceptable': bool(quality_result.get('is_acceptable', False))
            },
            'analysis_result': result,
            'recommendations': recommendations,
            'quality_assessment': quality_result
        }
        
        # Convert all numpy types to Python native types
        analysis_data = convert_numpy_types(analysis_data)
        
        # Store analysis history
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if user_id not in analysis_history:
            analysis_history[user_id] = []
        analysis_history[user_id].append(analysis_data)
        
        logger.info(f"✅ Analysis completed: {result['risk_level']} (Confidence: {result['confidence']:.2f})")
        
        return JSONResponse(content=analysis_data)
        
    except Exception as e:
        logger.error(f"❌ Analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/user-history/{user_id}")
async def get_user_history(user_id: str):
    try:
        history = analysis_history.get(user_id, [])
        # Convert numpy types in history
        history = convert_numpy_types(history)
        return {
            "user_id": user_id,
            "analysis_count": len(history),
            "history": history[-10:]  # Last 10 analyses
        }
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_recommendations(result: dict, quality_result: dict) -> list:
    """Generate personalized recommendations"""
    try:
        risk_level = result['risk_level']
        confidence = result['confidence']
        
        base_recommendations = {
            'Normal': [
                "✅ Your eye health appears normal. Continue regular eye care habits.",
                "📅 Schedule annual comprehensive eye exams.",
                "💻 Practice the 20-20-20 rule to reduce digital eye strain.",
                "🥗 Maintain a balanced diet rich in eye-healthy nutrients."
            ],
            'Slightly High': [
                "⚠️ Moderate risk detected. Increased monitoring recommended.",
                "👁️ Practice eye relaxation exercises daily.",
                "🕒 Reduce continuous screen time; take frequent breaks.",
                "🏥 Consider consulting an eye specialist for evaluation.",
                "📊 Monitor changes weekly with follow-up images."
            ],
            'High': [
                "🚨 Higher risk level detected. Professional consultation advised.",
                "👨‍⚕️ Schedule an appointment with an ophthalmologist promptly.",
                "📵 Significantly reduce screen time and eye strain.",
                "🧘 Practice eye exercises 3-4 times daily.",
                "💧 Maintain proper hydration and monitor blood pressure."
            ]
        }
        
        recommendations = base_recommendations.get(risk_level, [])
        
        # Add quality-based recommendations
        if not quality_result.get('is_acceptable', False):
            recommendations.insert(0, "📸 Image quality is low. For better analysis, ensure good lighting and focus.")
        
        if confidence < 0.7:
            recommendations.append("ℹ️ Analysis confidence is moderate. Consider retaking the image with better lighting.")
        
        return recommendations
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return ["Please consult an eye specialist for professional evaluation."]

if __name__ == "__main__":
    print("🚀 Starting FIXED EyeSense Backend on http://127.0.0.1:8000")
    print("✅ API Health Check: http://localhost:8000/api/health")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)