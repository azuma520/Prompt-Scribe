"""
Vercel Serverless Function Entry Point
FastAPI application for Prompt-Scribe API
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Prompt-Scribe API",
    version="2.0.1",
    description="AI-powered tag recommendation API"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "version": "2.0.1",
        "service": "Prompt-Scribe API",
        "timestamp": "2025-10-15T16:45:00Z"
    }

@app.get("/")
async def root():
    """根端點"""
    return {"message": "Prompt-Scribe API is running!", "version": "2.0.1"}

# 直接導出 app 供 Vercel 使用
__all__ = ["app"]
