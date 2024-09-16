import json
import aiofiles
import os
from nonebot.adapters.onebot.v11 import Bot, Event

current_dir = os.path.dirname(os.path.abspath(__file__))
mode_file = os.path.join(current_dir, 'mode.json')

def load_mode():
    try:
        with open(mode_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
# 记录事件以便回复    
async def notice(bot: Bot, event: Event):
    mode_data = {"type": "private", "id": event.user_id}
    if event.message_type == "group":
        mode_data = {"type": "group", "id": event.group_id}
    async with aiofiles.open(mode_file, 'w') as f:
        await f.write(json.dumps(mode_data))