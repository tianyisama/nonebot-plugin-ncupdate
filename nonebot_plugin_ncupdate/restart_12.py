import nonebot
import asyncio
import os
import psutil
from .info import get_qq_registry_values_async
from .notice import notice
from nonebot.adapters.onebot.v11 import Bot, Event
# Kill掉NTQQ所在目录的cmd以防重复登陆
async def kill_cmd_processes_at_path(exe_path):

    exe_dir = os.path.dirname(exe_path)
    normalized_exe_dir = os.path.normpath(exe_dir).lower()
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:

            proc_cwd = proc.cwd().lower()
            normalized_proc_cwd = os.path.normpath(proc_cwd)

            if normalized_exe_dir == normalized_proc_cwd:
                nonebot.logger.info(f"Killing CMD process with PID {proc.info['pid']} at path {exe_dir}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

# 9.9.12特有的启动方式
async def start_program_async(bot=None, event=None, value=None, bot_id=None):
    try:
        registry_values = await get_qq_registry_values_async()
        
        display_icon_value = registry_values.get("DisplayIcon")

        if display_icon_value:
            exe_path = display_icon_value.split(',')[0].strip("'").strip()
            nonebot.logger.info(f"获取到NTQQ安装位置： '{exe_path}'")

            exe_dir = os.path.dirname(exe_path)

            if not exe_dir or not os.path.exists(exe_dir):
                nonebot.logger.warning(f"Invalid executable directory: '{exe_dir}'")
                return

            args = f"--enable-logging -q {bot_id}"
            await kill_cmd_processes_at_path(exe_path)
        else:
            nonebot.logger.warning("Unable to read the registry value for DisplayIcon.")
            return

        if not os.path.exists(exe_path):
            nonebot.logger.warning(f"Executable not found: {exe_path}")
            return

        batch_command = f'chcp 65001>nul && "{exe_path}" {args}'
        command = f'start cmd.exe /k "cd /d "{exe_dir}" && {batch_command}"'
        nonebot.logger.info(f"Executing command: {command}")
        if value == 1:
            await notice(bot, event)
        proc = await asyncio.create_subprocess_shell(command, cwd=exe_dir, shell=True)
        await proc.communicate()
    except Exception as e:
        nonebot.logger.error(f"An error occurred: {e}")
