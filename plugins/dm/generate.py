# fileName : plugins/dm/generate.py
# copyright ©️ 2021 nabilanavab

import os
import shutil
from pdf import PDF
from time import sleep
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

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"

feedbackMsg = "[Bot haqida taklif va shikoyatlar yozishingiz mumkin 📋](https://t.me/azik_projects_support)"

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
#--------> REPLY TO /generate MESSAGE
#------------------->

@ILovePDF.on_message(filters.private & filters.command(["generate"]) & ~filters.edited)
async def generate(bot, message):
    try:
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse,
                reply_markup=button
            )
            return
        
        # newName : new file name(/generate ___)
        newName = str(message.text.replace("/generate", ""))
        images = PDF.get(message.chat.id)
        
        if isinstance(images, list):
            pgnmbr = len(PDF[message.chat.id])
            del PDF[message.chat.id]
        
        # IF NO IMAGES SEND BEFORE
        if not images:
            await message.reply_chat_action("typing")
            imagesNotFounded = await message.reply_text(
                "`Rasm topilmadi.!!`😒"
            )
            sleep(5)
            await message.delete()
            await imagesNotFounded.delete()
            return
        
        gnrtMsgId = await message.reply_text(
            f"`PDF yaratilmoqda..`💚"
        )
        
        if newName == " name":
            fileName = f"{message.from_user.first_name}" + ".pdf"
        elif len(newName) > 1 and len(newName) <= 45:
            fileName = f"{newName}" + ".pdf"
        elif len(newName) > 45:
            fileName = f"" + "@azik_pdfbot.pdf" #{message.from_user.first_name}
        else:
            fileName = f"" + "@azik_pdfbot.pdf" #{message.chat.id}
        
        images[0].save(fileName, save_all = True, append_images = images[1:])
        await gnrtMsgId.edit(
            "`PDF sizga yuborilmoqda.. `🏋️",
        )
        await message.reply_chat_action("upload_document")
        generated = await bot.send_document(
            chat_id=message.chat.id,
            document=open(fileName, "rb"),
            thumb=Config.PDF_THUMBNAIL,
            caption=f"Fayl Nomi: `{fileName}`\n`Umumiy sahifalar: {pgnmbr}`ta\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊\n\n"
        )
        await gnrtMsgId.edit(
            "`Muvaffaqiyatli yuklandi.. `🤫",
        )
        os.remove(fileName)
        shutil.rmtree(f"{message.chat.id}")
        sleep(5)
        await message.reply_chat_action("typing")
        await message.reply_text(
            feedbackMsg, disable_web_page_preview = True
        )
    except Exception:
        try:
            os.remove(fileName)
            shutil.rmtree(f"{message.chat.id}")
        except Exception:
            pass

#                                                                                  Telegram: @nabilanavab
