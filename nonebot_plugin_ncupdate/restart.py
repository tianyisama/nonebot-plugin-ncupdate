import os
import aiofiles
import json
import platform
import nonebot
from packaging import version
from .notice import notice
from .version import is_qq_version_at_least_9_9_12
from .sysexec import kill_cmd_process, kill_target_processes, start_powershell_script, start_script, start_program_async,kill_napcat_screens, start_napcat_screen

current_dir = os.path.dirname(os.path.abspath(__file__))
mode_file = os.path.join(current_dir, 'mode.json')

class BotRestarter:
    def __init__(self, bot_id, base_path, topfolder, disconnect, bot= None, event= None, send_message=True):
        self.bot = bot
        self.event = event
        self.bot_id = bot_id
        self.base_path = base_path
        self.topfolder = topfolder
        self.disconnect = disconnect
        self.send_message = send_message
        target_path = os.path.normcase(os.path.normpath(os.path.join(self.base_path, self.topfolder)))
        self.target_path = target_path
    async def send_restart_notice(self, message):
        if self.send_message:
            await self.bot.send(self.event, message)

    async def get_parsed_app_version(self):
        version_info = await self.bot.get_version_info()
        app_version = version_info['app_version']
        return version.parse(app_version)
    
    async def restart_bot(self, nc_restart_way):

        try:
            await self.send_restart_notice("正在重启，请稍候")
            if nc_restart_way == 1:
                await self.restart_method_1(self.disconnect)
            elif nc_restart_way == 2:
                await self.restart_method_2(self.target_path,self.disconnect)
            elif nc_restart_way == 3:
                await self.restart_method_3(self.disconnect)
            elif nc_restart_way == 4:
                await self.restart_method_4(self.target_path,self.disconnect)
            elif nc_restart_way == 5:
                await self.restart_method_5(self.target_path,self.disconnect)
            elif nc_restart_way == 6:
                await self.restart_method_6(self.target_path,self.disconnect)
            elif nc_restart_way == 7:
                await self.restart_method_7(self.disconnect)
        except Exception as e:
            await self.send_restart_notice(f"发送重启请求时出现错误：{str(e)}")
            async with aiofiles.open(mode_file, 'w') as f:
                await f.write(json.dumps({}))
    async def restart_method_1(self, disconnect):
        if disconnect:
            await self.restart_method_6(self.target_path,self.disconnect)
            return
        await notice(self.bot, self.event)
        await self.bot.set_restart(delay=1000)

    async def restart_method_2(self, target_path, disconnect):
        if platform.system().lower() == 'windows':
            version_up = await is_qq_version_at_least_9_9_12()
            if version_up:
                await self.send_restart_notice("Baka!9.9.12以上不能用这个方法登录！")
                return
            if not disconnect:
                await notice(self.bot, self.event)
            found = await kill_cmd_process(target_path)
            if found:
                await start_script(target_path, self.bot_id, bat='napcat-utf8.bat', q_option=True)
            else:
                nonebot.logger.info('No matching CMD process found, starting script directly')
                await start_script(target_path, self.bot_id, bat='napcat-utf8.bat', q_option=True)
        else:
            await self.send_restart_notice("只有Windows才能用这个方法啦！")
    async def restart_method_3(self,disconnect):
        if platform.system().lower() == 'windows':
            version_up = await is_qq_version_at_least_9_9_12()
            if not disconnect:
                await notice(self.bot, self.event)
            if version_up:
                await start_program_async(self.bot_id)
        else:
            await self.send_restart_notice("只有Windows才能用这个方法啦！")
    async def restart_method_4(self, target_path, disconnect):
        if platform.system().lower() == 'windows':
            if not disconnect:
                app_version_parsed = await self.get_parsed_app_version()
                if app_version_parsed < version.parse("1.7.2"):
                    await self.send_restart_notice("笨蛋！Napcat版本太低啦\n至少要为1.7.2!")
                    return
                await notice(self.bot, self.event)
            found = await kill_target_processes('powershell.exe', target_path)
            if found:
                await start_powershell_script(target_path, self.bot_id)
            else:
                nonebot.logger.info('No matching PS process found, starting script directly')
                await start_powershell_script(target_path, self.bot_id)
        else:
            await self.send_restart_notice("只有Windows才能用这个方法啦！")
    async def restart_method_5(self, target_path, disconnect):
        if platform.system().lower() == 'windows':
            if not disconnect:
                app_version_parsed = await self.get_parsed_app_version()
                if app_version_parsed < version.parse("2.4.6"):
                    await self.send_restart_notice("笨蛋！Napcat版本太低啦\n至少要为2.4.6!")
                    return
                await notice(self.bot, self.event)
            found = await kill_target_processes('cmd.exe', target_path)
            if found:
                await start_script(target_path, self.bot_id, bat='launcher-win10', q_option=False)
            else:
                nonebot.logger.info('No matching CMD process found, starting script directly')
                await start_script(target_path, self.bot_id, bat='launcher-win10', q_option=False)
        else:
            await self.send_restart_notice("只有Windows才能用这个方法啦！")
    async def restart_method_6(self, target_path, disconnect):
        if platform.system().lower() == 'windows':
            if not disconnect:
                app_version_parsed = await self.get_parsed_app_version()
                if app_version_parsed < version.parse("2.4.6"):
                    await self.send_restart_notice("笨蛋！Napcat版本太低啦\n至少要为2.4.6!")
                    return
                await notice(self.bot, self.event)
            found = await kill_target_processes('cmd.exe', target_path)
            if found:
                await start_script(target_path, self.bot_id, bat='launcher.bat', q_option=False)
            else:
                nonebot.logger.info('No matching CMD process found, starting script directly')
                await start_script(target_path, self.bot_id, bat='launcher.bat', q_option=False)
        else:
            await self.send_restart_notice("只有Windows才能用这个方法啦！")
    async def restart_method_7(self, disconnect):
        if platform.system().lower() == 'linux':
            if not disconnect:
                await notice(self.bot, self.event)
            await kill_napcat_screens()
            await start_napcat_screen(self.bot_id)
        else:
            await self.send_restart_notice("只有linux才能用这个方法啦！")



