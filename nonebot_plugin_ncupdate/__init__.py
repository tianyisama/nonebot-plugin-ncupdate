from nonebot import on_command, get_driver, on
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message,GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from .config import Config, config
from .version import ciallo, get_qq_version_info, qq_version
from .dialog import tkinter_dialog
from .restart import BotRestarter
from .unzip import unzip_v1, unzip_v2
import httpx
import aiofiles
import os
import nonebot
import json
import platform
import asyncio

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
global bot_id, cnt

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
    release_url = (
        f"https://api.github.com/repos/NapNeko/NapCatQQ/releases/tags/{specific_version}"
        if specific_version
        else "https://api.github.com/repos/NapNeko/NapCatQQ/releases/latest"
    )
    async with await create_client() as client:
        resp = await client.get(release_url)
        if resp.status_code == 404:
            raise ValueError(f"指定的版本 {specific_version} 不存在。")
        resp.raise_for_status()
        release_data = resp.json()
        latest_version = release_data["tag_name"]
        current_version = f"v{version_info['app_version']}"

        if not latest_version.startswith("v1"):
            asset_keyword = "NapCat.Shell.zip"
        else:
            asset_keyword = asset_keyword.get(napcat_mode)
        
        if asset := next((asset for asset in release_data["assets"] if asset_keyword in asset["name"]), None):
            return asset, latest_version, current_version
        else:
            raise ValueError("未找到对应的release")

async def download_file(download_url, filename):
    async with await create_client() as client:
        download_resp = await client.get(download_url)
        download_resp.raise_for_status()
        file_path = os.path.join(base_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as file:
            await file.write(download_resp.content)
        return file_path

@help.handle()
async def help_():
    await help.send(f"﻿Ciallo～(∠・ω<)⌒⚡\n"
                    "本插件可自行判断napcat版本是否与ntqq兼容。\n"
                    "可使用如下指令：\n"
                    "(柚子)更新nc：更新Napcat最新版。若后接具体的版本号可指定具体的版本，例如：更新nc1.8.2\n"
                    "(柚子)重启nc，重新启动Napcat\n"
                    "(柚子)查看qq版本/qqv：查看当前的QQ版本号\n"
                    "nc检查更新：检查最新的版本及其更新的内容和版本要求\n"
                    "柚子检查更新：人机合一时检查更新")

@update_nc.handle()
async def handle_update_nc(bot: Bot, event: Event, args: Message = CommandArg()):
    specific_version = args.extract_plain_text().strip()
    try:
        version_info = await bot.get_version_info()
        latest_version = f"v{specific_version}" if specific_version else None
        asset, latest_version, current_version = await get_latest_release(napcat_mode, version_info, specific_version=latest_version)

        if latest_version == current_version:
            await update_nc.finish(f"已经是最新版了~\n当前版本:{current_version}")

        if platform.system().lower() == 'windows':
            odoo = await ciallo(latest_version)
            if not odoo:
                await update_nc.finish(f"警告: NTQQ版本与该版本NapCat不兼容。\n已取消本次更新")

        await update_nc.send("正在更新，请稍候")
        download_url = asset["browser_download_url"]
        file_path = await download_file(download_url, asset['name'])

        await update_nc.send("正在执行文件替换")
        if latest_version.startswith("v1"):
            await unzip_v1(file_path, base_path, topfolder)
        #elif latest_version.startswith(("v2", "v3")):
        else:
            await unzip_v2(file_path, base_path, topfolder)

        await handle_restart(bot, event)
        
    except FinishedException:
        pass
    except ValueError as e:
        await update_nc.finish(str(e))
    except Exception as e:
        await update_nc.send(f"发生错误：{e}")


@restart.handle()
async def handle_restart(bot: Bot, event: Event):
    global bot_id
    restarter = BotRestarter(bot_id, base_path, topfolder, disconnect=False, bot=bot, event=event, send_message=True)
    await restarter.restart_bot(nc_restart_way)


@update_info.handle()
async def handle_update_info(bot: Bot):
    
    release_url = "https://api.github.com/repos/NapNeko/NapCatQQ/releases/latest"
    try:
        async with await create_client() as client:
            resp = await client.get(release_url)
            resp.raise_for_status()
            release_data = resp.json()
            tag_name = release_data["tag_name"]
            body = release_data["body"]
            qq_version = await get_qq_version_info()
            version_info = await bot.get_version_info()
            app_version = f"v{version_info['app_version']}"
            if tag_name == app_version:
                message = f"已是最新版本，无需更新~\n当前的QQ版本:{qq_version}\n当前的NapCat版本:{app_version}"
            else:
                message = f"最新版本: {tag_name}\n更新内容:\n{body}\n当前的QQ版本:{qq_version}\n当前的NapCat版本:{app_version}"

            await update_info.send(message)

    except httpx.HTTPStatusError as e:
        await update_info.send(f"获取最新版本信息失败，状态码：{e.response.status_code}")
    except Exception as e:
        await update_info.send(f"发生错误：{e}")



@driver.on_bot_connect
async def reconnected(bot: Bot):
    global cnt
    cnt = True
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

@driver.on_bot_disconnect
async def reconnect():
    global bot_id, cnt
    cnt = False
    if not nc_reconnect:
        nonebot.logger.info("未开启断线重连，已跳过重连请求")
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
    await asyncio.sleep(2)
    if cnt:
        nonebot.logger.warning("又好了，不用重连啦")
        return
    dialog_result = await tkinter_dialog()
    if dialog_result == "restart":
        restarter = BotRestarter(bot_id, base_path, topfolder, disconnect=True, send_message=False)
        await restarter.restart_bot(nc_restart_way)
    elif dialog_result == "cancel":
        nonebot.logger.info('已取消本次重连')
    elif dialog_result == "tkinter not available":
        await asyncio.sleep(8)
        restarter = BotRestarter(bot_id, base_path, topfolder, disconnect=True, send_message=False)
        await restarter.restart_bot(nc_restart_way)
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
            await handle_update_info(bot)
        elif nc_self_qq_version == event.raw_message:
            await qq_version()


