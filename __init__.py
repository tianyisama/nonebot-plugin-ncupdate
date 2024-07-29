from nonebot import on_command, get_driver, on
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from .config import Config, config
from .version import is_qq_version_at_least_9_9_12
from .restart_12 import start_program_async
from .notice import notice
from .dialog import tkinter_dialog
import httpx
import aiofiles
import zipfile
import os
import shutil
import nonebot
import asyncio
import json
import psutil
import subprocess
import time
import platform

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
nc_http_port = config.nc_http_port
nc_self_update = config.nc_self_update 
nc_self_restart = config.nc_self_restart
nc_reconnect = config.nc_reconnect

current_dir = os.path.dirname(os.path.abspath(__file__))
mode_file = os.path.join(current_dir, 'mode.json')
update_nc = on_command("更新nc", priority=5, permission=SUPERUSER)
restart = on_command("重启nc", priority=5, permission=SUPERUSER)
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

async def get_latest_release(napcat_mode, version_info):
    asset_keyword = {
        "win": "win32.x64",
        "win_32": "win32.ia32",
        "linux": "linux.x64",
        "linux_arm": "linux.arm64"
    }[napcat_mode]
    
    async with await create_client() as client:
        resp = await client.get("https://api.github.com/repos/NapNeko/NapCatQQ/releases/latest")
        resp.raise_for_status()
        release_data = resp.json()
        latest_version = release_data["tag_name"]
        current_version = f"v{version_info['app_version']}"
        asset = next((asset for asset in release_data["assets"] if asset_keyword in asset["name"]), None)
        if not asset:
            raise ValueError("未找到对应的release")
        
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

@update_nc.handle()
async def handle_update_nc(bot: Bot, event: Event):
    global bot_id
    try:
        version_info = await bot.get_version_info()
        try:
            asset, latest_version, current_version = await get_latest_release(napcat_mode, version_info)
        except ValueError as e:
            await update_nc.finish(str(e)) 
        
        if latest_version == current_version:
            await update_nc.finish(f"已经是最新版了~\n当前版本:{current_version}")

        await update_nc.send("正在更新，请稍候")
        download_url = asset["browser_download_url"]
        file_path = await download_file(download_url, asset['name'])
        try:
            await update_nc.send("正在执行文件替换")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
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
        except:
            await update_nc.finish("文件替换过程出现错误")
        version_up = await is_qq_version_at_least_9_9_12()
        if platform.system().lower() == 'windows' and version_up:
            value = 1
            await start_program_async(bot, event, value, bot_id)
        else:   
            await handle_restart(bot, event)

    except FinishedException:
        pass
    except Exception as e:
        await update_nc.send(f"发生错误：{e}")
@restart.handle()
async def handle_restart(bot: Bot, event: Event):
    global bot_id
    try:
        await restart.send("正在重启，请稍候")
        await notice(bot, event)
        version_up = await is_qq_version_at_least_9_9_12()
        if platform.system().lower() == 'windows' and version_up:
            value = 1
            await start_program_async(bot, event, value, bot_id)
        else:
            async with httpx.AsyncClient(proxies={}) as client:
                post_resp = await client.post(url=f"http://127.0.0.1:{nc_http_port}/set_restart", data={"delay": 10})
                post_resp.raise_for_status()
    except httpx.HTTPStatusError as http_err:
        await restart.send(f"发送重启请求时出错：{http_err}")
    except Exception as e:
        await restart.send(f"发送重启请求时出现错误：{str(e)}")
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

async def start_script(target_path, bot_id):
    bat_path = os.path.join(target_path, 'napcat-utf8.bat')
    command = f'cmd.exe /c start "" "{bat_path}" -q {bot_id}'

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=target_path
        )
        nonebot.logger.info(f'Started napcat-utf8.bat with new process')
    except Exception as e:
        nonebot.logger.error(f'启动登录脚本失败: {e}')

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
            print(f"{bot_id}")
            await start_program_async(bot_id = bot_id)
            return
        # 9.9.11及之前版本的启动方式
        target_path = os.path.normcase(os.path.normpath(os.path.join(base_path, topfolder)))
        found = await kill_cmd_process(target_path)
        if found:
            await start_script(target_path, bot_id)
        else:
            nonebot.logger.info('No matching CMD process found, starting script directly')
            await start_script(target_path, bot_id)
    elif dialog_result == "cancel":
        nonebot.logger.info('已取消本次重连')
        return


@on_message_sent.handle()
async def handle_message_sent(bot: Bot, event: Event):
    if isinstance(event, Event) and event.raw_message == nc_self_update:
        await handle_update_nc(bot, event)
    elif isinstance(event, Event) and event.raw_message == nc_self_restart:
        await handle_restart(bot, event)


