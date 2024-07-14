from packaging import version
from .info import get_qq_registry_values_async

async def is_qq_version_at_least_9_9_12() -> bool:
    registry_values = await get_qq_registry_values_async()
    display_version_value = registry_values.get("DisplayVersion")
    target_version = "9.9.12"

    if display_version_value:
        # 如果版本号至少是9.9.12，返回True
        return version.parse(display_version_value) >= version.parse(target_version)
    else:
        return False
