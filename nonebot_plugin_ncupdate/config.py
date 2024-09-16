from pydantic import BaseModel
from typing import Optional
from nonebot import get_plugin_config

class Config(BaseModel):
    base_path: Optional[str] = "C:\\napcat"
    topfolder: Optional[str] = "NapCat.win32.x64"
    napcat_mode: Optional[str] = "win"
    nc_proxy: Optional[bool] = False
    nc_proxy_port: Optional[int] = 11451
    nc_self_update: Optional[str] = "柚子更新nc"
    nc_self_restart: Optional[str] = "柚子重启nc"
    nc_self_check_update: Optional[str] = "柚子检查更新"
    nc_self_qq_version: Optional[str] = "柚子查看qq版本"
    nc_reconnect: Optional[bool] = False
    nc_restart_way: Optional[int] = 1

config = get_plugin_config(Config)