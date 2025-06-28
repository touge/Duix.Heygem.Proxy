# settings.py
import yaml
from pathlib import Path
from pydantic import BaseModel, HttpUrl

class Settings(BaseModel):
    root_dir: Path
    real_video_subdir: str
    audio_subdir: str
    char_subdir:  str

    host: str
    port: int

    resource_access_key: str
    auth_enabled: bool

    internal_submit: HttpUrl
    internal_query: HttpUrl

    @property
    def real_video_dir(self) -> Path:
        return self.root_dir / self.real_video_subdir

    @property
    def audio_dir(self) -> Path:
        return self.root_dir / self.audio_subdir

    @property
    def char_dir(self) -> Path:
        return self.root_dir / self.char_subdir

# 加载并校验配置
cfg_path = Path(__file__).parent / "config.yaml"
cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
settings = Settings(**cfg)
