# proxy_service/utils.py

import hashlib
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional
from fastapi import Header, HTTPException
from settings import settings

SERVICE_DICT = {
   9999: "System abnormality",
  10000: "Succeeded",
  10001: "Engaged in another task",
  10002: "Parameter exception",
  10003: "Get lock exception",
  10004: "Task does not exist",
  10005: "Task processing timeout",
  10006: "Unable to submit task, please check service status",
}

def check_service_resp(r: Dict) -> Dict:
    """
    检查内部服务返回的 JSON，抛出 HTTPException 或返回 data 字段。
    """
    code = r.get("code")
    ok   = r.get("success", False)
    msg  = SERVICE_DICT.get(code, r.get("msg", "Unknown"))
    if code != 10000 or not ok:
        raise HTTPException(502, f"{code}: {msg}")
    return r["data"]

def sign_payload(data: Dict[str, str]) -> str:
    """
    对 payload 进行 sha256 签名（按 key 排序后拼接 resource_access_key）。
    """
    items = sorted((k, str(v)) for k, v in data.items())
    raw   = "&".join(f"{k}={v}" for k, v in items) + settings.resource_access_key
    return hashlib.sha256(raw.encode()).hexdigest()

def validate_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-KEY")):
    """
    校验前端传入的 X-API-KEY，支持关闭鉴权。
    """
    if not settings.auth_enabled:
        return
    if not x_api_key:
        raise HTTPException(401, "X-API-KEY missing")
    if x_api_key != settings.resource_access_key:
        raise HTTPException(403, "Invalid API key")

def probe_video(path: Path) -> Dict[str, float]:
    """
    使用系统已安装的 ffprobe 探测视频文件的宽、高、时长
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "json", str(path)
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise HTTPException(500, f"ffprobe error: {p.stderr}")
    info    = json.loads(p.stdout)
    streams = info.get("streams", [])
    width   = streams[0].get("width", 0) if streams else 0
    height  = streams[0].get("height", 0) if streams else 0
    duration = float(info.get("format", {}).get("duration", 0))
    return {"width": width, "height": height, "duration": duration}

def get_real_video_path(result_path: str) -> Path:
    """
    将内部服务返回的 result（形如 "/xxx.mp4"）转换为磁盘上真实路径
    """
    rel = result_path.lstrip("/")      # 去掉前导斜杠
    return settings.real_video_dir / rel
