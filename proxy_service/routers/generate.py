# proxy_service/routers/generate.py

import uuid
import base64
import shutil
import json
from pathlib import Path
import requests

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from proxy_service.utils import validate_api_key, sign_payload, check_service_resp
from settings import settings

router = APIRouter()

@router.post("/generate-video")
async def generate_video(
    audio_file:     UploadFile       = File(None),
    base64_audio:   str              = Form(None),
    character_name: str              = Form(None),
    x_api_key      = validate_api_key
):
    # 鉴权 & 参数校验
    if not (audio_file or base64_audio):
        raise HTTPException(400, "必须提供 audio_file 或 base64_audio")
    if not character_name:
        raise HTTPException(400, "必须提供 character_name")

    # 读取角色配置
    json_path = settings.char_dir / f"{character_name}.json"
    if not json_path.exists():
        raise HTTPException(404, f"角色 '{character_name}' 未找到")
    info     = json.loads(json_path.read_text("utf-8"))
    filename = info["filename"]
    # 外部服务接收的URL前置 ../characters/
    video_path = f"../characters/{filename}"

    # 保存音频到本地
    task_code = str(uuid.uuid4())
    ext       = Path(audio_file.filename if audio_file else "").suffix or ".wav"
    out_file  = settings.audio_dir / f"{task_code}{ext}"

    if audio_file:
        with out_file.open("wb") as f:
            shutil.copyfileobj(audio_file.file, f)
    else:
        out_file.write_bytes(base64.b64decode(base64_audio))

    # 构造 audio_url：相对于 root_dir，前置 "../" 并统一用正斜杠
    try:
        rel = out_file.relative_to(settings.root_dir)
        audio_url = f"../{rel.as_posix()}"
    except Exception:
        audio_url = f"../{settings.audio_dir.name}/{out_file.name}"

    # 组装并签名 payload
    payload = {
        "audio_url":        audio_url,
        "video_url":        video_path,
        "code":             task_code,
        "chaofen":          0,
        "watermark_switch": 0,
        "pn":               1,
    }
    payload["sign"] = sign_payload(payload)

    # 调用内部服务
    resp = requests.post(settings.internal_submit, json=payload)
    if resp.status_code != 200:
        raise HTTPException(502, f"内部服务 HTTP {resp.status_code}")
    _ = check_service_resp(resp.json())

    return {"task_code": task_code}
