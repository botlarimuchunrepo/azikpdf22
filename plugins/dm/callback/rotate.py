# fileName : plugins/dm/callBack/rotate.py
# copyright ©️ 2021 nabilanavab

import os
import time
import shutil
from pdf import PROCESS
from pyrogram import filters
from Configs.dm import Config
from plugins.checkPdf import checkPdf
from plugins.progress import progress
from pyrogram import Client as ILovePDF
from PyPDF2 import PdfFileWriter, PdfFileReader
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
#------------------->

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> PDF ROTATION
#------------------->

rot = filters.create(lambda _, __, query: query.data in ["rot90", "rot180", "rot270"])
rot360 = filters.create(lambda _, __, query: query.data == "rot360")

rotate = filters.create(lambda _, __, query: query.data == "rotate")
Krotate = filters.create(lambda _, __, query: query.data.startswith("Krotate|"))

# rotate PDF (unknown pg no)
@ILovePDF.on_callback_query(rotate)
async def _rotate(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__Umumiy sahifalar: Noma'lum 😐  \nPDFni aylantirish:__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("90° ga aylantirish", callback_data="rot90"),
                        InlineKeyboardButton("180° ga aylantirish", callback_data="rot180")
                    ],[
                        InlineKeyboardButton("270° ga aylantirish", callback_data="rot270"),
                        InlineKeyboardButton("360° ga aylantirish", callback_data="rot360")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data="BTPM")
                    ]
                ]
            )
        )
    except Exception:
        pass

# rotate PDF (only change in back button)
@ILovePDF.on_callback_query(Krotate)
async def _Krotate(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Umumiy sahifalar: {number_of_pages}ta\nPDFni aylantirish:__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("90°  ga aylantirish", callback_data="rot90"),
                        InlineKeyboardButton("180° ga aylantirish", callback_data="rot180")
                    ],[
                        InlineKeyboardButton("270° ga aylantirish", callback_data="rot270"),
                        InlineKeyboardButton("360° ga aylantirish", callback_data="rot360")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"KBTPM|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

@ILovePDF.on_callback_query(rot)
async def _rot(bot, callbackQuery):
    try:
        # CALLBACK DATA
        data = callbackQuery.data
        # CHECK USER IN PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        #ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # STARTED DOWNLOADING
        downloadMessage = await callbackQuery.message.reply_to_message.reply(
            "`PDFingiz yuklab olinmoqda..`⏳",
        )
        input_file=f"{callbackQuery.message.message_id}/input.pdf"
        output_file=f"{callbackQuery.message.message_id}/rotate.pdf"
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        fileNm=callbackQuery.message.reply_to_message.document.file_name
        fileNm, fileExt=os.path.splitext(fileNm)        # seperates name & extension
        # DOWNLOAD PROGRESS
        c_time=time.time()
        downloadLoc=await bot.download_media(
            message=file_id,
            file_name=input_file,
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
            "`Aylantirish boshlandi` 🤸"
        )
        #CHECK PDF
        checked=await checkPdf(
            input_file,
            callbackQuery
        )
        if not(checked == "pass"):
            await downloadMessage.delete()
            return
        #STARTED ROTATING
        pdf_writer=PdfFileWriter()
        pdf_reader=PdfFileReader(input_file)
        number_of_pages=pdf_reader.numPages
        # ROTATE 90°
        if data=="rot90":
            # Rotate page 90 degrees to the right
            for i in range(number_of_pages):
                page=pdf_reader.getPage(i).rotateClockwise(90)
                pdf_writer.addPage(page)
            caption="__ 90° ga aylantirildi\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
        # ROTATE 180°
        if data=="rot180":
            # Rotate page 180 degrees to the right
            for i in range(number_of_pages):
                page=pdf_reader.getPage(i).rotateClockwise(180)
                pdf_writer.addPage(page)
            caption="__180° ga aylantirildi\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
        # ROTATE 270°
        if data=="rot270":
            # Rotate page 270 degrees to the right
            for i in range(number_of_pages):
                page=pdf_reader.getPage(i).rotateCounterClockwise(90)
                pdf_writer.addPage(page)
            caption="__270° ga aylantirildi\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
        with open(output_file, 'wb') as fh:
            pdf_writer.write(fh)
        await bot.send_chat_action(
            callbackQuery.message.chat.id, "upload_document"
        )
        await downloadMessage.edit(
            "`Sizga yuborilmoqda..`🏋️"
        )
        # SEND ROTATED DOCUMENT
        await callbackQuery.message.reply_document(
            file_name=f"@azik_pdfbot.pdf", #{fileNm} via 
            document=open(output_file, "rb"),
            thumb=PDF_THUMBNAIL, quote=True,
            caption=caption
        )
        # DELETES DOWNLOAD MESSAGE
        await downloadMessage.delete()
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("rotate: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

@ILovePDF.on_callback_query(rot360)
async def _rot360(bot, callbackQuery):
    try:
        await callbackQuery.answer(
            "Sizda katta muammo bor..🙂"
        )
    except Exception:
        pass

#                                                                                  Telegram: @nabilanavab
