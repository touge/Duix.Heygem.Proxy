# proxy_service/routers/progress.py

import asyncio
import requests
from fastapi import APIRouter, Query, HTTPException
from proxy_service.models import QueryResult
from proxy_service.utils import validate_api_key, check_service_resp, get_real_video_path
from settings import settings

router = APIRouter()

@router.get("/generate-video-progress", response_model=QueryResult)
async def generate_video_progress(
    task_code: str           = Query(..., description="generate-video 返回的 task_code"),
    x_api_key               = validate_api_key
):
    """
    轮询内部查询接口，直到 status==2（完成），并将磁盘真实路径（POSIX 格式）写入 detail["real_video_path"]。
    请求的 timeout=(None, None) 参数确保“连接”和“读取”都无限等待，不会触发 requests 超时。
    """
    data: dict = {}
    while True:
        resp = requests.get(
            settings.internal_query,
            params={"code": task_code},
            timeout=(None, None)   # (connect_timeout, read_timeout) 都设为 None，表示无限等待
        )
        if resp.status_code != 200:
            raise HTTPException(502, f"内部服务 HTTP {resp.status_code}")
        data = check_service_resp(resp.json())
        if data.get("status") == 2:
            break
        # 任务未完成时，休眠一秒再重试
        await asyncio.sleep(1)

    # 在 detail 中添加 real_video_path，使用 POSIX 风格路径（全 “/”）
    real_path = get_real_video_path(data["result"])
    data["real_video_path"] = real_path.as_posix()

    return QueryResult(
        code     = data["code"],
        status   = data["status"],
        progress = data.get("progress"),
        detail   = data,
    )
