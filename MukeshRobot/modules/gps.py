from pyrogram import  enums, filters, idle
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from requests import get
import asyncio
from MukeshRobot import pbot as mukesh
from pyrogram.handlers import MessageHandler
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
@mukesh.on_message(filters.command(["gps"]))
async def gps(bot, message):
#     await message.delete()
    if len(message.command) < 2:
        return await message.reply_text(
            "**示例：**\n\n`/gps [纬度 , 经度]`")
    x = message.text.split(' ')[1].split(',')
   

    try:
        
        """
        ---------github :-NOOB-MUKESH -----
        ---------telegram : @itz_legend_coder-----
        """
        geolocator = Nominatim(user_agent="legend-Mukesh")
#         zoom=[0-18]


        location = geolocator.reverse(x,addressdetails=True, zoom=18)
        address=location.raw['address'] 
        # Traverse the data
        city = address.get('city', '')
        state = address.get('state', '')
        country = address.get('country', '')
        latitude = location.latitude
        longitude = location.longitude
        url=[

            [IKB

             ("用谷歌地图打开 🌏",url=f"https://www.google.com/maps/search/{latitude},{longitude}")

            ]

            ]

    #     await message.reply_text(f"{gm}")
        await message.reply_venue(latitude, longitude,f"{city}",f"{state} ,{country}",reply_markup=IKM(url))
    except Exception as e:
        await message.reply_text(f"无法找到该位置 \n错误：{e}")
@mukesh.on_message(filters.command(["distance"]))
async def distance(bot, message):
    await message.delete()
    if len(message.command) < 2:
        return await message.reply_text(
            "**示例：**\n\n`/distance [纬度 , 经度],[纬度 , 经度]`")

    x = message.text.split(" ")[1].split(',',2)[0:2]
    y = message.text.split(" ")[1].split(',',4)[2:4]

    


    try:

        """
        ---------github :-NOOB-MUKESH -----
        ---------telegram : @itz_legend_coder-----
        """
        distance=(great_circle(x,y).miles)

        await message.reply_text(f"{x[0]},{x[1]} 与 {y[0]},{y[1]} 之间的总距离为 {distance} 英里")

    except Exception as e:
        await message.reply_text(f"无法计算距离 \n错误：{e}")
        
# mukesh.add_handler(MessageHandler(gps))     
# mukesh.add_handler(MessageHandler(distance))

__help__ = """
发送指定查询的 GPS 位置信息……

 ❍ /gps <坐标>*:* 获取 GPS 位置。
 ❍ /distance  测量两点之间的距离
"""

__mod_name__ = "GPS 定位"
