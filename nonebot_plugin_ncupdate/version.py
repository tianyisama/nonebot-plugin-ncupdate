from packaging import version
from .info import get_qq_registry_values_async
from nonebot import on_command
from nonebot.permission import SUPERUSER
import nonebot
import subprocess
import asyncio
import re
import distro
import platform
qq_version_info = on_command("查看qq版本", aliases={"查看QQ版本", "qqv"},priority=5, permission=SUPERUSER)

@qq_version_info.handle()
async def qq_version():
    version = await get_qq_version_info()
    if version == 0:
        await qq_version_info.send(f"未能获取到QQ版本，可能是不支持的系统")
    else:
        await qq_version_info.send(f"当前的QQ版本是:{version}")

async def get_qq_version_info():
    if platform.system().lower() == 'windows': 
        qq_info = await get_qq_patch_number()
    else:
        if distro.id() in ["centos","rocky"]:
            qq_info = await get_qq_version_centos()
        elif distro.id() in ["debian","ubuntu"]:
            qq_info = await get_qq_version_debian()
        else:
            qq_info = 0
    return qq_info

async def get_qq_patch_number() -> int:
    registry_values = await get_qq_registry_values_async()
    display_version_value = registry_values.get("DisplayVersion")
    if display_version_value:
        version_parts = display_version_value.split('.')
        return int(version_parts[3])
    else:
        return 0 

async def get_qq_version_centos() -> int:
    try:
        process = await asyncio.create_subprocess_exec(
            "rpm", "-q", "--queryformat", "%{VERSION}", "linuxqq",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stdout = stdout.decode('utf-8')
        if process.returncode == 0:
            version_match = re.search(r'_([0-9]+)$', stdout)
            if version_match:
                return int(version_match.group(1))
        else:
            nonebot.logger.error(f"Error: {stderr.decode('utf-8')}")
            return 0
    except Exception as e:
        nonebot.logger.error(f"发生错误: {e}")
        return 0
    return 0

async def get_qq_version_debian() -> int:
    try:
        process = await asyncio.create_subprocess_exec(
            "dpkg", "-l", "linuxqq",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        stdout, stderr = await process.communicate()
        stdout = stdout.decode('utf-8')
        if process.returncode == 0:
            match = re.search(r'\bii\s+' + re.escape("linuxqq") + r'\s+(\S+)', stdout)
            if match:
                version_str = match.group(1)
                version_int_match = re.search(r'(\d+)$', version_str)
                if version_int_match:
                    return int(version_int_match.group(1))
        else:
            nonebot.logger.error(f"Error: {stderr}")
            return 0
    except Exception as e:
        nonebot.logger.error(f"发生错误: {e}")
        return 0
    return 0

async def ciallo(latest_version: str) -> bool:

    latest_version = latest_version.lstrip('v')
    patch_number = await get_qq_version_info()


    if latest_version.startswith("1"):
        return patch_number <= 26702

    elif latest_version == "2.0.37":
        return 26702 <= patch_number <= 26909

    latest_version_parsed = version.parse(latest_version)

    if version.parse("2.1.0") <= latest_version_parsed <= version.parse("2.2.18"):
        return patch_number >= 27187

    elif version.parse("2.2.19") <= latest_version_parsed <= version.parse("2.2.29"):
        return patch_number >= 27254

    elif version.parse("2.2.30") <= latest_version_parsed <= version.parse("2.5.3"):
        return 27597 <= patch_number < 28060
    
    elif latest_version_parsed >= version.parse("2.5.4"):
        return patch_number >= 28060

    return False

async def is_qq_version_at_least_9_9_12() -> bool:
    registry_values = await get_qq_registry_values_async()
    display_version_value = registry_values.get("DisplayVersion")
    target_version = "9.9.12"

    if display_version_value:
        # 如果版本号至少是9.9.12，返回True
        return version.parse(display_version_value) >= version.parse(target_version)
    else:
        return False
