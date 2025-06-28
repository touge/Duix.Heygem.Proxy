# proxy_service/config.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import settings

def create_app() -> FastAPI:
    if not settings.root_dir.exists():
        raise RuntimeError(f"根目录不存在: {settings.root_dir}")
    for d in (settings.audio_dir, settings.char_dir, settings.real_video_dir):
        d.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("proxy").info("Starting TTS-Video Proxy")

    app = FastAPI(
        title="TTS-Video Proxy",
        version="0.1.0",
        description="局域网代理服务"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
