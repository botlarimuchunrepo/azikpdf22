# fileName : plugins/dm/id.py
# copyright ÂŠī¸ 2021 nabilanavab

from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as ILovePDF
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup

#--------------->
#--------> Config var.
#------------------->

BANNED_USERS=Config.BANNED_USERS
ADMIN_ONLY=Config.ADMIN_ONLY
ADMINS=Config.ADMINS

#--------------->
#--------> LOCAL VARIABLES
#------------------->

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz đ"

button=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "đ Administrator đ",
                    url="https://t.me/azik_developer"
                )
            ]
       ]
    )

#--------------->
#--------> GET USER ID (/id)
#------------------->

@ILovePDF.on_message(filters.private & ~filters.edited & filters.command(["id"]))
async def userId(bot, message):
    try:
        await message.reply_chat_action("typing")
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(UCantUse, reply_markup=button)
            return
        await message.reply_text(
            f'Sizning IDyingiz: `{message.chat.id}`', quote=True
        )
    except Exception:
        pass

#                                                                                  Telegram: @nabilanavab
