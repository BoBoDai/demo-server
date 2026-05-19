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


MODEL_EXTENSIONS = {".pt", ".onnx", ".yaml", ".cvimodel"}


def _find_model_file(folder: Path) -> Path | None:
    """在文件夹中查找模型文件"""
    for f in folder.iterdir():
        if f.suffix in MODEL_EXTENSIONS:
            return f
    return None


@app.get("/api/models")
async def list_models():
    """列出所有可用的模型（文件夹名称）"""
    models = []
    if MODELS_DIR.exists():
        for folder in MODELS_DIR.iterdir():
            if not folder.is_dir():
                continue
            model_file = _find_model_file(folder)
            if model_file:
                models.append({
                    "name": folder.name,
                    "file": model_file.name,
                    "size": model_file.stat().st_size,
                    "type": model_file.suffix[1:]
                })
    return {"models": models}


@app.get("/api/models/{folder_name}")
async def download_model(folder_name: str):
    """下载指定文件夹中的模型"""
    from fastapi.responses import FileResponse
    folder_path = MODELS_DIR / folder_name
    if not folder_path.is_dir():
        return {"error": "Model not found"}, 404
    model_file = _find_model_file(folder_path)
    if model_file is None:
        return {"error": "No model file in folder"}, 404
    return FileResponse(path=model_file, filename=model_file.name, media_type="application/octet-stream")


@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)