# proxy_service/routers/characters.py

import json
from datetime import datetime
import shutil
from pathlib import Path
from typing import List               # 新增
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from settings import settings
from proxy_service.utils import validate_api_key, probe_video
from proxy_service.models import CharacterListItem, CharacterDetail

router = APIRouter()

@router.post("/characters/upload")
async def upload_character_video(
    name:       str        = Form(..., description="角色名称，可含下划线"),
    video_file: UploadFile = File(..., description="mp4 文件"),
    x_api_key             = validate_api_key
):
    name = name.strip()
    json_path = settings.char_dir / f"{name}.json"
    if json_path.exists():
        raise HTTPException(400, f"角色 '{name}' 已存在")

    orig     = Path(video_file.filename).name
    vid_name = f"{name}_{orig}"
    vid_path = settings.char_dir / vid_name
    with vid_path.open("wb") as f:
        shutil.copyfileobj(video_file.file, f)

    mv = probe_video(vid_path)
    meta = {
        "character_name": name,
        "filename":       vid_name,
        "upload_time":    datetime.utcnow().isoformat(),
        "size":           vid_path.stat().st_size,
        **mv
    }
    json_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return {"character_name": name}


@router.get("/characters", response_model=List[CharacterListItem])
def list_characters(x_api_key = validate_api_key):
    items = [
        CharacterListItem(character_name=p.stem)
        for p in settings.char_dir.glob("*.json")
    ]
    return sorted(items, key=lambda x: x.character_name)


@router.get("/characters/{name}", response_model=CharacterDetail)
def get_character_detail(
    name:       str,
    x_api_key = validate_api_key
):
    name = name.strip()
    json_path = settings.char_dir / f"{name}.json"
    if not json_path.exists():
        raise HTTPException(404, f"角色 '{name}' 未找到")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return CharacterDetail(**data)
