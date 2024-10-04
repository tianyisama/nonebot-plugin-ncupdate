from nonebot import on_command, get_driver, on
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message
from nonebot.permission import SUPERUSER
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from .config import Config, config
from .version import is_qq_version_at_least_9_9_12, get_qq_patch_number, ciallo, get_qq_version_info, qq_version
from .restart_12 import start_program_async
from .notice import notice
from .dialog import tkinter_dialog
from packaging import version
import httpx
import aiofiles
import zipfile
import os
import shutil
import nonebot
import asyncio
import json
import psutil
import platform
import subprocess
from datetime import datetime

__plugin_meta__ = PluginMetadata(
    name="指令更新NapCat",
    description="指令更新NapCat",
    usage="""更新nc: 更新napcat并自动重启
重启nc: 重新启动napcat
柚子更新nc: 自己作为机器人触发的更新
柚子重启nc: 自己作为机器人触发的重启""",
    type="application",
    homepage="https://github.com/tianyisama/nonebot-plugin-ncupdate",
    config=Config,
    supported_adapters={"~onebot.v11"},
)
driver = get_driver()
base_path = config.base_path
topfolder = config.topfolder
napcat_mode = config.napcat_mode
nc_proxy = config.nc_proxy
nc_proxy_port = config.nc_proxy_port
nc_self_update = config.nc_self_update 
nc_self_restart = config.nc_self_restart
nc_reconnect = config.nc_reconnect
nc_restart_way = config.nc_restart_way
nc_self_check_update = config.nc_self_check_update
nc_self_qq_version = config.nc_self_qq_version

current_dir = os.path.dirname(os.path.abspath(__file__))
mode_file = os.path.join(current_dir, 'mode.json')
update_nc = on_command("更新nc", priority=5, permission=SUPERUSER)
restart = on_command("重启nc", priority=5, permission=SUPERUSER)
help = on_command("nc帮助", priority=5, permission=SUPERUSER)
update_info = on_command("nc检查更新", priority=5, permission=SUPERUSER)
on_message_sent = on("message_sent", block=False)
global bot_id

async def create_client():
    if nc_proxy:
        proxies = {
            "http://": f"http://127.0.0.1:{nc_proxy_port}",
            "https://": f"http://127.0.0.1:{nc_proxy_port}",
        }
        return httpx.AsyncClient(proxies=proxies, follow_redirects=True)
    else:
        return httpx.AsyncClient(follow_redirects=True)

async def get_latest_release(napcat_mode, version_info, specific_version=None):
    asset_keyword = {
        "win": "win32.x64",
        "win_32": "win32.ia32",
        "linux": "linux.x64",
        "linux_arm": "linux.arm64"
    }
    if specific_version:
        release_url = f"https://api.github.com/repos/NapNeko/NapCatQQ/releases/tags/{specific_version}"
    else:
        release_url = "https://api.github.com/repos/NapNeko/NapCatQQ/releases/latest"
    async with await create_client() as client:
        resp = await client.get(release_url)
        if resp.status_code == 404:
            raise ValueError(f"指定的版本 {specific_version} 不存在。")
        resp.raise_for_status()
        release_data = resp.json()
        latest_version = release_data["tag_name"]
        current_version = f"v{version_info['app_version']}"

        if latest_version.startswith("v2"):
            asset_keyword = {
                "win": "NapCat.Shell.zip",
                "win_32": "NapCat.Shell.zip",
                "linux": "NapCat.Shell.zip",
                "linux_arm": "NapCat.Shell.zip"
            }[napcat_mode]
        else:
            asset_keyword = asset_keyword[napcat_mode]
        
        asset = next((asset for asset in release_data["assets"] if asset_keyword in asset["name"]), None)
        if not asset:
            raise ValueError(f"未找到对应的release")
        
        return asset, latest_version, current_version

async def download_file(download_url, filename):
    async with await create_client() as client:
        download_resp = await client.get(download_url)
        download_resp.raise_for_status()
        file_path = os.path.join(base_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as file:
            await file.write(download_resp.content)
        return file_path
# 1.x版本的解压方式
async def unzip_v1(zip_file_path, base_path, topfolder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            try:
                relative_path = member.partition('/')[2]
                if relative_path:
                    new_path = os.path.join(base_path, topfolder, relative_path)
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    with zip_ref.open(member, 'r') as source, open(new_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
            except zipfile.BadZipFile:
                continue
            except OSError:
                continue
# 2.x版本的解压方式
async def unzip_v2(zip_file_path, base_path, topfolder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            try:
                relative_path = member if member.endswith('/') else member
                if relative_path:
                    new_path = os.path.join(base_path, topfolder, relative_path)
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    if not member.endswith('/'):
                        with zip_ref.open(member, 'r') as source, open(new_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
            except zipfile.BadZipFile:
                continue
            except OSError:
                continue
@help.handle()
async def help_():
    await help.send(f"﻿Ciallo～(∠・ω<)⌒⚡\n本插件可判断2.5.1及之前的版本是否与ntqq兼容。\n可使用如下指令：\n更新nc：更新Napcat最新版。若后接具体的版本号可指定具体的版本，例如：更新nc1.8.2\n重启nc，重新启动Napcat\n查看qq版本：查看当前的QQ版本号\nnc检查更新：检查最新的版本及其更新的内容和版本要求")

@update_nc.handle()
async def handle_update_nc(bot: Bot, event: Event, args: Message = CommandArg()):
    global bot_id
    specific_version = args.extract_plain_text().strip()
    try:
        version_info = await bot.get_version_info()
        try:
            if specific_version:
                asset, latest_version, current_version = await get_latest_release(
                    napcat_mode, version_info, specific_version=f"v{specific_version}")
            else:
                asset, latest_version, current_version = await get_latest_release(napcat_mode, version_info)
        except ValueError as e:            
            await update_nc.finish(str(e)) 
        if latest_version == current_version:
            await update_nc.finish(f"已经是最新版了~\n当前版本:{current_version}")
        
        if platform.system().lower() == 'windows':
            odoo = await ciallo(latest_version)
            if not odoo:
                await update_nc.finish(f"警告:NTQQ版本与该版本NapCat不兼容。\n已取消本次更新")

        await update_nc.send("正在更新，请稍候")
        download_url = asset["browser_download_url"]
        file_path = await download_file(download_url, asset['name'])
        try:
            await update_nc.send("正在执行文件替换")
            nonebot.logger.info(f"{latest_version}")
            if latest_version.startswith("v1"):
                await unzip_v1(file_path, base_path, topfolder)
            elif latest_version.startswith("v2"):
                
                await unzip_v2(file_path, base_path, topfolder)
        except Exception as e:
            await update_nc.finish(f"文件替换过程出现错误:{e}")

        await handle_restart(bot, event)

    except FinishedException:
        pass
    except Exception as e:
        await update_nc.send(f"发生错误：{e}")
@restart.handle()
async def handle_restart(bot: Bot, event: Event):
    global bot_id
    target_path = os.path.normcase(os.path.normpath(os.path.join(base_path, topfolder)))
    try:
        await restart.send("正在重启，请稍候")
        if nc_restart_way == 1:
            await notice(bot, event)
            await bot.set_restart(delay=1000)
        elif nc_restart_way == 2:
            if platform.system().lower() == 'windows':
                version_up = await is_qq_version_at_least_9_9_12()
                if version_up:
                    await bot.send(event, "Baka!9.9.12以上不能用这个方法登录！")
                    return
            await notice(bot, event)
            found = await kill_cmd_process(target_path)
            if found:
                await start_script(target_path, bot_id, bat='napcat-utf8.bat', q_option=True)
            else:
                nonebot.logger.info('No matching CMD process found, starting script directly')
                await start_script(target_path, bot_id, bat='napcat-utf8.bat', q_option=True)
        elif nc_restart_way == 3:
            if platform.system().lower() == 'windows':
                version_up = await is_qq_version_at_least_9_9_12()
                if version_up:
                    value = 1
                    await notice(bot, event)
                    await start_program_async(bot, event, value, bot_id)
                else:
                    await bot.send(event , "QQ版本都没有9.9.12，你莫不是在消遣洒家！")
                    return
            else:
                await bot.send(event, "只有Windows才能用这个方法啦！")
                return
        elif nc_restart_way == 4:
            if platform.system().lower() == 'windows':
                version_info = await bot.get_version_info()
                app_version = version_info['app_version']
                app_version_parsed = version.parse(app_version)
                if app_version_parsed < version.parse("1.7.2"):
                    await bot.send(event, "笨蛋！Napcat版本太低啦\n至少要为1.7.2！")
                    return
                else:
                    await notice(bot, event)
                    found = await kill_target_processes('powershell.exe', target_path)
                    if found:
                        await start_powershell_script(target_path, bot_id)
                    else:
                        await start_powershell_script(target_path, bot_id)
            else:
                await bot.send(event, "只有Windows才能用这个方法啦！")
        elif nc_restart_way == 5:
            if platform.system().lower() == 'windows':
                version_info = await bot.get_version_info()
                app_version = version_info['app_version']
                app_version_parsed = version.parse(app_version)
                if app_version_parsed < version.parse("2.4.6"):
                    await bot.send(event, "笨蛋！Napcat版本太低啦\n至少要为2.4.6!")
                    return
                else:
                    await notice(bot, event)
                    found = await kill_target_processes('cmd.exe', target_path)
                    if found:
                        await start_script(target_path, bot_id, bat='launcher-win10.bat', q_option=False)
                    else:
                        await start_script(target_path, bot_id, bat='launcher-win10.bat', q_option=False)
            else:
                await bot.send(event, "只有Windows才能用这个方法啦！")
        elif nc_restart_way == 6:
            if platform.system().lower() == 'windows':
                version_info = await bot.get_version_info()
                app_version = version_info['app_version']
                app_version_parsed = version.parse(app_version)
                if app_version_parsed < version.parse("2.4.6"):
                    await bot.send(event, "笨蛋！Napcat版本太低啦\n至少要为2.4.6!")
                    return
                else:
                    await notice(bot, event)
                    found = await kill_target_processes('cmd.exe', target_path)
                    if found:
                        await start_script(target_path, bot_id, bat='launcher.bat', q_option=False)
                    else:
                        await start_script(target_path, bot_id, bat='launcher.bat', q_option=False)
            else:
                await bot.send(event, "只有Windows才能用这个方法啦！")
    except Exception as e:
        await restart.send(f"发送重启请求时出现错误：{str(e)}")

@update_info.handle()
async def handle_update_info():
    
    release_url = "https://api.github.com/repos/NapNeko/NapCatQQ/releases/latest"
    try:
        async with await create_client() as client:
            resp = await client.get(release_url)
            resp.raise_for_status()
            release_data = resp.json()
            tag_name = release_data["tag_name"]
            body = release_data["body"]
            qq_version = await get_qq_version_info()
            message = f"最新版本: {tag_name}\n更新内容:\n{body}\n当前的QQ版本是:{qq_version}"

            await update_info.send(message)

    except httpx.HTTPStatusError as e:
        await update_info.send(f"获取最新版本信息失败，状态码：{e.response.status_code}")
    except Exception as e:
        await update_info.send(f"发生错误：{e}")


@driver.on_bot_connect
async def reconnected(bot: Bot):
    version_info = await bot.get_version_info()
    appname = version_info["app_name"]
    version = version_info["app_version"]
    message = MessageSegment.text(f"操作完成！\n当前运行框架: {appname}\n当前版本:{version}")
    try:
        async with aiofiles.open(mode_file, 'r') as f:
            mode_data = json.loads(await f.read())

        if not mode_data or 'type' not in mode_data:
            pass
        else:
            if mode_data["type"] == "group":
                await bot.send_group_msg(group_id=mode_data["id"], message=message)
            else:
                await bot.send_private_msg(user_id=mode_data["id"], message=message)

        async with aiofiles.open(mode_file, 'w') as f:
            await f.write(json.dumps({}))
    except FileNotFoundError:
        return
    except Exception as e:
        nonebot.logger.error(f"发送操作成功消息时发生错误：{e}")
    
    global bot_id
    bot_id = nonebot.get_bot().self_id
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

async def start_powershell_script(target_path, bot_id):
    ps1_path = os.path.join(target_path, 'BootWay05.ps1')
    command = f'start powershell.exe -NoExit -ExecutionPolicy Bypass -File "{ps1_path}" -q {bot_id}'

    try:
        process = subprocess.Popen(command, cwd=target_path, shell=True)
        nonebot.logger.info(f'Started BootWay05.ps1 in a new window')
    except Exception as e:
        nonebot.logger.error(f'Failed to start the script: {e}')
@driver.on_bot_disconnect
async def reconnect(bot: Bot):
    global bot_id

    if not nc_reconnect:
        nonebot.logger.info("未开启断线重连，已跳过重连请求")
        return
    if platform.system().lower() == 'linux':
        nonebot.logger.warning('暂不支持linux重连')
        return
    try:
        async with aiofiles.open(mode_file, 'r') as f:
            mode_data = await f.read()
            mode_data = json.loads(mode_data)
            if mode_data:
                nonebot.logger.info("检测到指令重启，跳过重连")
                return
    except FileNotFoundError:
        return
    except Exception as e:
        nonebot.logger.error(f"Error reading mode.json: {e}")
        return

    nonebot.logger.info('检测到连接已断开，将在10s后自动发起重连')
    dialog_result = await tkinter_dialog()
    if dialog_result == "restart":
        version_up = await is_qq_version_at_least_9_9_12()
        # 9.9.12版本的启动方式
        if platform.system().lower() == 'windows' and version_up:
            nonebot.logger.info(f"获取到bot_id:{bot_id}")
            await start_program_async(bot_id = bot_id)
            return
        # 9.9.11及之前版本的启动方式
        target_path = os.path.normcase(os.path.normpath(os.path.join(base_path, topfolder)))
        found = await kill_cmd_process(target_path)
        if found:
            await start_script(target_path, bot_id, bat='napcat-utf8.bat')
        else:
            nonebot.logger.info('No matching CMD process found, starting script directly')
            await start_script(target_path, bot_id, bat='napcat-utf8.bat')
    elif dialog_result == "cancel":
        nonebot.logger.info('已取消本次重连')
        return


@on_message_sent.handle()
async def handle_message_sent(bot: Bot, event: Event):
    if isinstance(event, Event):
        if nc_self_update in event.raw_message:
            args_index = event.raw_message.find(nc_self_update) + len(nc_self_update)
            args_str = event.raw_message[args_index:].strip()
            args_message = Message(args_str)
            await handle_update_nc(bot, event, args_message)
        elif nc_self_restart == event.raw_message:
            await handle_restart(bot, event)
        elif nc_self_check_update == event.raw_message:
            await handle_update_info()
        elif nc_self_qq_version == event.raw_message:
            await qq_version()


