import psutil
import nonebot
import os
import asyncio
import subprocess
import shlex
from datetime import datetime
from .info import get_qq_registry_values_async

# 干掉指定目录下的cmd
async def kill_cmd_process(target_path):
    found = False
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cwd']):
        if proc.info['name'] == 'cmd.exe':
            pid = proc.info['pid']
            cwd = proc.info['cwd']
            normalized_cwd = os.path.normcase(os.path.normpath(cwd))

            nonebot.logger.info(f'PID: {pid}, CWD: {normalized_cwd}')
            if normalized_cwd == target_path:
                proc.kill()
                nonebot.logger.info(f'Killed process with PID: {pid}')
                found = True
                break
    return found

# 启动指定目录下的bat
async def start_script(target_path, bot_id, bat=None, q_option=True):
    if bat is None:
        bat = 'napcat-utf8.bat'

    bat_path = os.path.join(target_path, bat)
    param = '-q' if q_option else ''
    command = f'cmd.exe /c start "" "{bat_path}" {param} {bot_id}'

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=target_path
        )
        nonebot.logger.info(f'已启动 {bat} 的新进程')
    except Exception as e:
        nonebot.logger.error(f'启动登录脚本失败: {e}')
        raise ValueError(f"脚本不存在")

# 干掉指定目录下的进程
async def kill_target_processes(target_name, target_path):
    def kill_related_processes(proc_name, proc_create_time):
        for proc in psutil.process_iter(['name', 'create_time']):
            if proc.info['name'].lower() == proc_name.lower():
                create_time = datetime.fromtimestamp(proc.info['create_time'])
                if create_time > proc_create_time:
                    proc.kill()
                    proc.wait(timeout=3)
                    nonebot.logger.info(f'Killed related process {proc_name} with PID: {proc.pid}')

    def kill_proc_and_children(proc):
        children = proc.children(recursive=True)
        for child in children:
            child.kill()
            child.wait(timeout=3)
            nonebot.logger.info(f'Killed child process with PID: {child.pid}')
        proc.kill()
        proc.wait(timeout=3)
        nonebot.logger.info(f'Killed {target_name} parent process with PID: {proc.pid}')

    found = False
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
        try:
            if proc.info['name'].lower() == target_name.lower():
                cwd = proc.cwd()
                normalized_cwd = os.path.normcase(os.path.normpath(cwd))
                nonebot.logger.info(f'PID: {proc.info["pid"]}, CWD: {normalized_cwd}')
                if normalized_cwd == os.path.normcase(os.path.normpath(target_path)):
                    found = True
                    proc_create_time = datetime.fromtimestamp(proc.info['create_time'])
                    nonebot.logger.info(f'{target_name} PID: {proc.info["pid"]} started at {proc_create_time}')
                    kill_related_processes('QQ.exe', proc_create_time)
                    kill_proc_and_children(proc)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return found

# 启动指定目录下的ps
async def start_powershell_script(target_path, bot_id):
    ps1_path = os.path.join(target_path, 'BootWay05.ps1')
    command = f'start powershell.exe -NoExit -ExecutionPolicy Bypass -File "{ps1_path}" -q {bot_id}'

    try:
        process = subprocess.Popen(command, cwd=target_path, shell=True)
        nonebot.logger.info(f'Started BootWay05.ps1 in a new window')
    except Exception as e:
        nonebot.logger.error(f'Failed to start the script: {e}')


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

# 9.9.12特有的启动方式（exe启动方式/way03）
async def start_program_async(bot_id=None):
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
        proc = await asyncio.create_subprocess_shell(command, cwd=exe_dir, shell=True)
        await proc.communicate()
    except Exception as e:
        nonebot.logger.error(f"An error occurred: {e}")

async def kill_napcat_screens():
    cmd_find = "screen -ls | grep 'napcat'"
    find_process = await asyncio.create_subprocess_shell(
        cmd_find,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await find_process.communicate()

    if find_process.returncode == 0:
        sessions = stdout.decode().strip().split('\n')
        for session in sessions:
            session_id = session.split()[0]
            if 'Dead' in session or 'dead' in session:
                cmd_wipe = f"screen -wipe {session_id}"
                await asyncio.create_subprocess_shell(
                    cmd_wipe,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                nonebot.logger.info(f"Wiped dead screen session {session_id}")
            else:
                cmd_kill = f"screen -S {session_id} -X quit"
                await asyncio.create_subprocess_shell(
                    cmd_kill,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                nonebot.logger.info(f"Killed screen session {session_id}")
    else:
        nonebot.logger.error(f"Error finding napcat screen sessions: {stderr.decode().strip()}")

async def start_napcat_screen(bot_id):
    cmd_start = f'screen -dmS napcat bash -c "xvfb-run -a qq --no-sandbox -q {bot_id}"'
    process = await asyncio.create_subprocess_shell(
        cmd_start,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        nonebot.logger.info(f"Started napcat screen session with bot_id: {bot_id}")
    else:
        nonebot.logger.error(f"Failed to start napcat screen session with bot_id: {bot_id}. Error: {stderr.decode()}")
