# fileName : Plugins/dm/photo.py
# copyright ยฉ๏ธ 2021 nabilanavab

import os
from pdf import PDF
from PIL import Image
from pdf import invite_link
from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as ILovePDF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> Config var.
#------------------->

UPDATE_CHANNEL=Config.UPDATE_CHANNEL
BANNED_USERS=Config.BANNED_USERS
ADMIN_ONLY=Config.ADMIN_ONLY
ADMINS=Config.ADMINS

#--------------->
#--------> LOCAL VARIABLES
#------------------->

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz ๐"

imageAdded = """`{} ta sahifa sizning pdfingizga qo'shildi..`๐ค

PDF yaratish uchun /generate komandasini yuboring ๐ค"""

forceSubMsg = """To'xtang [{}](tg://user?id={})..!!

Katta yuzaga keladigan yuk tufayli bu botdan faqat kanal a'zolari foydalanishi mumkin ๐ถ

Bu mendan foydalanish uchun quyida ko'rsatilgan kanalga qo'shilishingiz kerakligini bildiradi!

qo'shilgandan keyin "Qayta urinishโป๏ธ" tugmasini bosing.. ๐"""

button=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "๐ Administrator ๐",
                    url="https://t.me/azik_developer"
                )
            ]
       ]
    )

#--------------->
#--------> REPLY TO IMAGES
#------------------->

@ILovePDF.on_message(filters.private & ~filters.edited & filters.photo)
async def images(bot, message):
    try:
        global invite_link
        await message.reply_chat_action("typing")
        # CHECK USER IN CHANNEL (IF UPDATE_CHANNEL ADDED)
        if UPDATE_CHANNEL:
            try:
                await bot.get_chat_member(
                    str(UPDATE_CHANNEL), message.chat.id
                )
            except Exception:
                if invite_link == None:
                    invite_link=await bot.create_chat_invite_link(
                        int(UPDATE_CHANNEL)
                    )
                await message.reply_text(
                    forceSubMsg.format(
                        message.from_user.first_name, message.chat.id
                    ),
                    reply_markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "๐ Proyektlar kanali ๐",
                                    url=invite_link.invite_link
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Qayta urinish โป๏ธ",
                                    callback_data="refresh"
                                )
                            ]
                        ]
                    )
                )
                return
        # CHECKS IF USER BAN/ADMIN..
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse, reply_markup=button
            )
            return
        imageReply = await message.reply_text(
            "`Rasmingiz yuklab olinmoqda..โณ`", quote=True
        )
        if not isinstance(PDF.get(message.chat.id), list):
            PDF[message.chat.id] = []
        await message.download(
            f"{message.chat.id}/{message.chat.id}.jpg"
        )
        img = Image.open(
            f"{message.chat.id}/{message.chat.id}.jpg"
        ).convert("RGB")
        PDF[message.chat.id].append(img)
        await imageReply.edit(
            imageAdded.format(len(PDF[message.chat.id]))
        )
    except Exception:
        pass


#                                                                                  Telegram: @nabilanavab
