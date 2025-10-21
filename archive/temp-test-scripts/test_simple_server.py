"""
Simple test server to verify FastAPI works
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test Server", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Hello World", "status": "OK"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Server is running"}

if __name__ == "__main__":
    print("Starting simple test server...")
    print("Server will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)
