from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test backend working!"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/analyze-eye")
async def analyze():
    return {
        "risk_level": "Normal",
        "confidence": 0.85,
        "message": "Test analysis successful!"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)