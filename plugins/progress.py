# fileName : plugins/progress.py
# copyright Â©ï¸ 2021 nabilanavab

import time, math
from pyrogram.types import Message
from pyrogram import Client, filters
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> DOWNLOAD PROGRESS
#------------------->


async def progress(current, t, total, message, start):
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ð«Bekor qilish", callback_data = "closeme")
            ]
        ]
    )
    now = time.time()
    diff = now - start
    
    if round(diff % 10) in [0, 8] or current == total:
        # if round(current / total * 100, 0) % 10 == 0:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress = "[{0}{1}] \n".format(
            ''.join(["â" for _ in range(math.floor(percentage / 5))]),
            ''.join(["â" for _ in range(20 - math.floor(percentage / 5))])
        )
        tmp = progress + "**\nTugallandi â : **{0}/{1}\n**Tezligi ð:** {2}/s\n**Qolgan vaqt â³:** {3}".format(
            await gSF(current),
            await gSF(total),
            await gSF(speed),
            TimeFormatter(time_to_completion)
        )
        
        await message.edit_text(
            text="Yuklab olinmoqda..ð¡ï¸\n{}".format(
                tmp
            ),
            reply_markup=reply_markup
        )


#--------------->
#--------> TIME FORMATTER
#------------------->

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

#                                                                                  Telegram: @nabilanavab
