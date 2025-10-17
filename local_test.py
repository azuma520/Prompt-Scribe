"""
簡化的本地測試版本
用於快速啟動本地 API 伺服器進行測試
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Prompt-Scribe API (Local Test)",
    version="2.0.1",
    description="本地測試版本的 Prompt-Scribe API"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根端點"""
    return {
        "message": "Prompt-Scribe API (Local Test) is running!",
        "version": "2.0.1",
        "environment": "local"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "version": "2.0.1",
        "service": "Prompt-Scribe API (Local Test)",
        "environment": "local"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """測試端點"""
    return {
        "message": "Test endpoint working!",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("local_test:app", host="0.0.0.0", port=8000, reload=True)
