import typing
from dataclasses import dataclass
from typing import Optional

import yaml

if typing.TYPE_CHECKING:
    from .aiohttp_extansion import Application


@dataclass
class Config:
    token: Optional[str] = None
    workers_count: Optional[int] = None


def setup_config(app: "Application", config_path):
    with open(config_path, 'r', encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)

    bot_c = raw_config["bot"]

    app.config = Config(token=bot_c["token"], workers_count=bot_c["workers_count"])
