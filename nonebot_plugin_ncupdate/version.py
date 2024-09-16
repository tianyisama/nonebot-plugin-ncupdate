from packaging import version
from .info import get_qq_registry_values_async
from nonebot import on_command
from nonebot.permission import SUPERUSER

qq_version_info = on_command("查看qq版本", aliases={"查看QQ版本"},priority=5, permission=SUPERUSER)

@qq_version_info.handle()
async def get_qq_version_info():
    qq_info = await get_qq_patch_number()
    await qq_version_info.send(f"当前的QQ版本号是:{qq_info}")

async def is_qq_version_at_least_9_9_12() -> bool:
    registry_values = await get_qq_registry_values_async()
    display_version_value = registry_values.get("DisplayVersion")
    target_version = "9.9.12"

    if display_version_value:
        # 如果版本号至少是9.9.12，返回True
        return version.parse(display_version_value) >= version.parse(target_version)
    else:
        return False

async def get_qq_patch_number() -> int:
    registry_values = await get_qq_registry_values_async()
    display_version_value = registry_values.get("DisplayVersion")

    if display_version_value:

        version_parts = display_version_value.split('.')
        if len(version_parts) > 3:
            try:

                return int(version_parts[3])
            except ValueError:

                return 0  
        else:
            return 0  
    else:
        return 0 

async def ciallo(latest_version: str) -> bool:

    latest_version = latest_version.lstrip('v')
    patch_number = await get_qq_patch_number()


    if latest_version.startswith("1"):
        return patch_number <= 26702

    elif latest_version == "2.0.37":
        return 26702 <= patch_number <= 26909

    latest_version_parsed = version.parse(latest_version)

    if version.parse("2.1.0") <= latest_version_parsed <= version.parse("2.2.18"):
        return patch_number >= 27187

    elif version.parse("2.2.19") <= latest_version_parsed <= version.parse("2.2.29"):
        return patch_number >= 27254

    elif latest_version_parsed >= version.parse("2.2.30"):
        return patch_number >= 27597

    return False