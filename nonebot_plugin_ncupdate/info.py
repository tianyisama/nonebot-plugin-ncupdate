import platform
import asyncio
from typing import Dict
try:
    import winreg
except ImportError:
    winreg = None
# 从注册表获取ntqq安装信息
async def get_qq_registry_values_async() -> Dict[str, str]:
    if not winreg:
        raise OSError("winreg module is only available on Windows.")
    
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\QQ"
    access_flags = winreg.KEY_READ
    if platform.architecture()[0] == '64bit':
        reg_path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\QQ"
        access_flags |= winreg.KEY_WOW64_32KEY
    # 安装位置及版本号
    key_names = ["DisplayIcon", "DisplayVersion"]
    
    def get_values():
        values = {}
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, access_flags)
            for name in key_names:
                try:
                    value, regtype = winreg.QueryValueEx(registry_key, name)
                    values[name] = value
                except WindowsError:
                    values[name] = None
            winreg.CloseKey(registry_key)
        except WindowsError:
            pass
        return values
    
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_values)