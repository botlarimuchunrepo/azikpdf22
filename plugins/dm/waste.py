# fileName : plugins/dm/waste.py
# copyright ©️ 2021 nabilanavab

from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as ILovePDF
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup

#--------------->
#--------> Config var.
#------------------->

BANNED_USERS = Config.BANNED_USERS
ADMIN_ONLY = Config.ADMIN_ONLY
ADMINS = Config.ADMINS

#--------------->
#--------> LOCAL VARIABLES
#------------------->

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"


button=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "😉 Administrator 😉",
                    url="https://t.me/azik_developer"
                )
            ]
       ]
    )

#--------------->
#--------> PDF REPLY BUTTON
#------------------->

@ILovePDF.on_message(filters.private & ~filters.edited)
async def spam(bot, message):
    try:
        await message.reply_chat_action("typing")
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse, reply_markup=button
            )
            return
        await message.reply_text(
            f"`Tushunarli!` Matnni Pdfga aylantirmoqchi bo'lsangiz /txt2pdf ni bosing.", quote=True
        )
    except Exception:
        pass

#                                                          Telegram: @nabilanavab
