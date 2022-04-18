# fileName : plugins/dm/cancel.py
# copyright ©️ 2021 nabilanavab

from pdf import PROCESS
from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as ILovePDF
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup

#--------------->
#--------> config vars
#------------------->

BANNED_USERS=Config.BANNED_USERS
ADMIN_ONLY=Config.ADMIN_ONLY
ADMINS=Config.ADMINS

#--------------->
#--------> LOCAL VARIABLES
#------------------->

UCantUse = "🚫Botdan banlanganingiz uchun siz ushbu botdan foydalana olmaysiz🚫\n\n Bandan olinish uchun administratorga murojaat qiling!"

button=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Administrator🧑‍💻",
                    url="https://t.me/azik_developer"
                )
            ]
       ]
    )

#--------------->
#--------> CANCELS CURRENT PDF TO IMAGES WORK
#------------------->


@ILovePDF.on_message(filters.private & ~filters.edited & filters.command(["cancel"]))
async def cancelP2I(bot, message):
    try:
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse,
                reply_markup=button,
            )
            return
        PROCESS.remove(message.chat.id)
        await message.delete()          # delete /cancel if process canceled
    except Exception:
        try:
            await message.reply_chat_action("typing")
            await message.reply_text(
                '🤔', quote=True
            )
        except Exception:
            pass

#                                                                                  Telegram: @nabilanavab
