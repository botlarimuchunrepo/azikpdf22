# fileName : plugins/dm/callBack/rename.py
# copyright ©️ 2021 nabilanavab

import os
import time
from pdf import PROCESS
from pyromod import listen
from pyrogram import filters
from Configs.dm import Config
from plugins.progress import progress
from pyrogram.types import ForceReply
from pyrogram import Client as ILovePDF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
#------------------->

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> RENAME PDF
#------------------->

rename = filters.create(lambda _, __, query: query.data.startswith("rename"))

@ILovePDF.on_callback_query(rename)
async def _encrypt(bot, callbackQuery):
    try:
        # CHECKS PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇",
            )
            return
        # ADDED TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # PYROMOD ADD-ON (REQUESTING FOR NEW NAME)
        newName=await bot.ask(
            chat_id=callbackQuery.message.chat.id,
            reply_to_message_id=callbackQuery.message.message_id,
            text="__PDFni qayta nomlash »\nEndi PDFni yangi yonimi kiriting:__\n\nBekor qilish uchun /exit ni bosing",
            filters=filters.text,
            reply_markup=ForceReply(True)
        )
        # /exit CANCELS
        if newName.text == "/exit":
            await newName.reply_text(
                "`Jarayon bekor qilindi.. `😏"
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        # DOWNLOADING MESSAGE
        downloadMessage=await callbackQuery.message.reply_text(
            "`PDFingiz yuklab olinmoqda..` ⏳", quote=True
        )
        # ADDS .pdf IF DONT HAVE AN EXTENSION
        if newName.text[-4:] == ".pdf":
            newName=newName.text
        else:
            newName=newName.text + ".pdf"
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        input_file=callbackQuery.message.reply_to_message.document.file_name
        # DOWNLOAD PROGRESS
        c_time=time.time()
        downloadLoc=await bot.download_media(
            message=file_id,
            file_name=f"./{newName}",
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        # CHECKS IF DOWNLOADING COMPLETED
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Sizga yuborilmoqda..`🏋️"
        )
        await bot.send_chat_action(
            callbackQuery.message.chat.id, "upload_document"
        )
        #SEND DOCUMENT
        await callbackQuery.message.reply_document(
            document=open(newName, "rb"),
            thumb=PDF_THUMBNAIL,
            caption="Eski nomi: `{}`\nYangi nomi: `{}`".format(
                input_file, newName
            )
        )
        # DELETES DOWNLOAD MESSAGE
        await downloadMessage.delete()
        os.remove(newName)
        PROCESS.remove(callbackQuery.message.chat.id)
    except Exception as e:
        try:
            print("Qayta nomlash: ",e)
            PROCESS.remove(callbackQuery.message.chat.id)
            os.remove(newName)
            await downloadMessage.delete()
        except Exception:
            pass

#                                                                                  Telegram: @nabilanavab
