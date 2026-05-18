"""
Demo Server - 提供模型文件管理服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

app = FastAPI(title="Demo Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模型存储目录
MODELS_DIR = Path(__file__).parent / "models"


@app.get("/api/models")
async def list_models():
    """列出所有可用的模型"""
    models = []
    if MODELS_DIR.exists():
        for f in MODELS_DIR.iterdir():
            if f.suffix in [".pt", ".onnx", ".yaml", ".cvimodel"]:
                models.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "type": f.suffix[1:]
                })
    return {"models": models}


@app.get("/api/models/{filename}")
async def download_model(filename: str):
    """下载指定模型"""
    from fastapi.responses import FileResponse
    file_path = MODELS_DIR / filename
    if not file_path.exists():
        return {"error": "Model not found"}, 404
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")


@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)