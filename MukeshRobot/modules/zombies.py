
from pyrogram import  filters
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.types import ChatPermissions
from pyrogram.enums import ChatMembersFilter
import requests,asyncio
from MukeshRobot import pbot as app,DEV_USERS,OWNER_ID,DEMONS,DRAGONS


OFFICERS = [OWNER_ID] + DEV_USERS + DRAGONS + DEMONS 

# Check if user has admin rights
async def is_administrator(user_id: int, message):
    admin = False
    administrators = []
    async for m in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        administrators.append(m)
    for user in administrators:
        if user.user.id == user_id or user_id in OFFICERS:
            admin = True
            break
    return admin

@app.on_message(filters.command("zombies", prefixes=["/","!"]) & filters.group)
async def rm_deletedacc(client, message):
    con = message.text.split(" ", 1)[1].lower() if len(message.command) > 1 else ""
    del_u = 0
    del_status = "群组已清理，未发现已注销账号。"

    if con != "clean":
        kontol = await message.reply("正在搜索已注销账号……")
        
        participants=[]
        async for member in app.get_chat_members(message.chat.id):
            participants.append(member)
        
      
        for user in participants:
            if user.user.is_deleted:
                print(user.user.is_deleted)
                del_u += 1
                await asyncio.sleep(1)
        if del_u > 0:
            del_status = (
                f"搜索完成，本群发现 {del_u} 个已注销的僵尸账号，"
                "使用命令 `/zombies clean` 清理"
            )
        return await kontol.edit(del_status)
    
    chat = await client.get_chat(message.chat.id)
    
    admin=await is_administrator(message.from_user.id,message)
    
    if not admin:
        return await message.reply("抱歉，你不是管理员！")

    memek = await message.reply("正在移除已注销账号……")
    participants=[]
    async for member in app.get_chat_members(message.chat.id):
        participants.append(member)
   
    for user in participants:
        if user.user.is_deleted:
            print(user.user.is_deleted)
            try:
                
                await client.ban_chat_member(message.chat.id, user.user.id)
                await client.unban_chat_member(message.chat.id, user.user.id)
                
            except ChatAdminRequired:
                return await message.edit("没有在该群组封禁用户的权限")
            except UserAdminInvalid:
                del_u -= 1
            await asyncio.sleep(1)
    
    if del_u > 0:
        del_status = f"已清理 {del_u} 个僵尸账号"
    
    await memek.edit(del_status)

help_text = """
*清理已注销账号*
❍ /zombies : 开始搜索群内已注销账号。
❍ /zombies clean : 将群内已注销账号移除。
"""
__mod_name__ = "僵尸账号"
