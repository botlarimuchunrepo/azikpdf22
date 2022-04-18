# fileName : plugins/dm/callBack/text.py
# copyright ©️ 2021 nabilanavab

import time
import fitz
import shutil
from pdf import PROCESS
from pyrogram import filters
from Configs.dm import Config
from plugins.checkPdf import checkPdf
from plugins.progress import progress
from pyrogram import Client as ILovePDF
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
#------------------->

pdfInfoMsg = """`Ushbu fayl bilan nima qilishni xohlaysiz.?`

Fayl Nomi: `{}`
Fayl hajmi: `{}`

`Sahifalar soni: {}ta`✌️
"""

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> VARIABLES
#------------------->

"""
______VARIABLES______

M = matnli xabar
T = matn fayli
H = html fayli
J = json fayli

'K' for pg no known pdfs
"""

#--------------->
#--------> PDF TO TEXT
#------------------->


M = filters.create(lambda _, __, query: query.data in ["M", "KM"])
T = filters.create(lambda _, __, query: query.data in ["T", "KT"])
J = filters.create(lambda _, __, query: query.data in ["J", "KJ"])
H = filters.create(lambda _, __, query: query.data in ["H", "KH"])

toText = filters.create(lambda _, __, query: query.data == "toText")
KtoText = filters.create(lambda _, __, query: query.data.startswith("KtoText|"))


# pdf to images (with unknown pdf page number)
@ILovePDF.on_callback_query(toText)
async def _toText(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__PDFni Matnga o'tkazish. \nUmumiy sahifalar: Noma'lum 😐         \nEndi, Formatni belgilang__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Matn holatida 📜", callback_data="M"),
                        InlineKeyboardButton("Txt fayl holatida 🧾", callback_data="T")
                    ],[
                        InlineKeyboardButton("Html 🌐", callback_data="H"),
                        InlineKeyboardButton("Json 🎀", callback_data="J")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data="BTPM")
                    ]
                ]
            )
        )
    except Exception:
        pass

# pdf to images (with known page Number)
@ILovePDF.on_callback_query(KtoText)
async def _KtoText(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__PDFni Matnga o'tkazish.\nUmumiy sahifalar: {number_of_pages}ta         \nEndi, Formatni belgilang__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Matn holatida 📜", callback_data="KM"),
                        InlineKeyboardButton("Txt fayl holatida🧾", callback_data="KT")
                    ],[
                        InlineKeyboardButton("Html 🌐", callback_data="KH"),
                        InlineKeyboardButton("Json 🎀", callback_data="KJ")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"KBTPM|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

# to Text file (with unknown pdf page number)
@ILovePDF.on_callback_query(T)
async def _T(bot, callbackQuery):
    try:
        # CHECH USER PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        data=callbackQuery.data
        # DOWNLOAD MESSAGE
        downloadMessage = await callbackQuery.message.reply_text(
            "`Pdfingiz yuklab olinmoqda..` ⏳", quote=True
        )
        # DOWNLOAD PROGRESS
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        c_time=time.time()
        downloadLoc = await bot.download_media(
            message=file_id,
            file_name=f"{callbackQuery.message.message_id}/pdf.pdf",
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Yuklab olish tugallandi..`✅"
        )
        if data == "T":
            checked = await checkPdf(f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
        with fitz.open(f'{callbackQuery.message.message_id}/pdf.pdf') as doc:
            number_of_pages = doc.pageCount
            with open(f'{callbackQuery.message.message_id}/pdf.txt', "wb") as out: # open text output
                for page in doc:                               # iterate the document pages
                    text=page.get_text().encode("utf8")        # get plain text (is in UTF-8)
                    out.write(text)                            # write text of page()
                    out.write(bytes((12,)))                    # write page delimiter (form feed 0x0C)
        await callbackQuery.message.reply_chat_action("upload_document")
        await callbackQuery.message.reply_document(
            file_name="PDF via @azik_pdfbot.txt", thumb = PDF_THUMBNAIL,
            document=f"{callbackQuery.message.message_id}/pdf.txt",
            caption="__Txt fayl\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊__"
        )
        await downloadMessage.delete()
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("Matn/T: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

# to Text message (with unknown pdf page number)
@ILovePDF.on_callback_query(M)
async def _M(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        PROCESS.append(callbackQuery.message.chat.id)
        data=callbackQuery.data
        downloadMessage = await callbackQuery.message.reply_text(
            text="`PDFingiz yuklab olinmoqda...` ⏳", quote=True
        )
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        c_time=time.time()
        downloadLoc = await bot.download_media(
            message=file_id,
            file_name=f"{callbackQuery.message.message_id}/pdf.pdf",
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Yuklab olish tugallandi..` 🥱"
        )
        if data == "M":
            checked = await checkPdf(f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
        with fitz.open(f'{callbackQuery.message.message_id}/pdf.pdf') as doc:
            number_of_pages = doc.pageCount
            for page in doc:                               # iterate the document pages
                pdfText = page.get_text().encode("utf8")            # get plain text (is in UTF-8)
                if 1 <= len(pdfText) <= 1048:
                    await bot.send_chat_action(
                        callbackQuery.message.chat.id, "typing"
                    )
                    await bot.send_message(
                        callbackQuery.message.chat.id, pdfText
                    )
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("Matn/M: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

# to Html file (with unknown pdf page number)
@ILovePDF.on_callback_query(H)
async def _H(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        PROCESS.append(callbackQuery.message.chat.id)
        data=callbackQuery.data
        downloadMessage = await callbackQuery.message.reply_text(
            text="`PDFingiz yuklab olinmoqda..` ⏳", quote=True
        )
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        c_time=time.time()
        downloadLoc = await bot.download_media(
            message=file_id,
            file_name=f"{callbackQuery.message.message_id}/pdf.pdf",
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Yuklab olish tugallandi..` 🥱"
        )
        if data == "H":
            checked = await checkPdf(f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
        with fitz.open(f'{callbackQuery.message.message_id}/pdf.pdf') as doc:
            number_of_pages = doc.pageCount
            with open(f'{callbackQuery.message.message_id}/pdf.html', "wb") as out: # open text output
                for page in doc:                                # iterate the document pages
                    text = page.get_text("html").encode("utf8") # get plain text (is in UTF-8)
                    out.write(text)                             # write text of page()
                    out.write(bytes((12,)))                     # write page delimiter (form feed 0x0C)
        await callbackQuery.message.reply_chat_action("upload_document")
        await callbackQuery.message.reply_document(
            file_name="PDF.html", thumb=PDF_THUMBNAIL,
            document=f"{callbackQuery.message.message_id}/pdf.html",
            caption="__Html fayl : har qanday brauzerda pdf ko'rishga yordam beradi\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊__"
        )
        await downloadMessage.delete()
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception:
        try:
            print("Matn/H: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

# to Text file (with unknown pdf page number)
@ILovePDF.on_callback_query(J)
async def _J(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        PROCESS.append(callbackQuery.message.chat.id)
        data=callbackQuery.data
        downloadMessage = await callbackQuery.message.reply_text(
            text="`PDFingiz yuklab olinmoqda..` ⏳", quote=True
        )
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        c_time=time.time()
        downloadLoc = await bot.download_media(
            message=file_id,
            file_name=f"{callbackQuery.message.message_id}/pdf.pdf",
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Yuklab olish tugallandi..` 🥱"
        )
        if data == "J":
            checked = await checkPdf(f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
        with fitz.open(f'{callbackQuery.message.message_id}/pdf.pdf') as doc:
            number_of_pages = doc.pageCount
            with open(f'{callbackQuery.message.message_id}/pdf.json', "wb") as out: # open text output
                for page in doc:                                # iterate the document pages
                    text = page.get_text("json").encode("utf8") # get plain text (is in UTF-8)
                    out.write(text)                             # write text of page()
                    out.write(bytes((12,)))                     # write page delimiter (form feed 0x0C)
        await callbackQuery.message.reply_chat_action("upload_document")
        await bot.send_document(
            file_name="PDF via @azik_pdfbot.json", thumb=PDF_THUMBNAIL,
            document=f"{callbackQuery.message.message_id}/pdf.json",
            caption="__Json Fayl\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊__"
        )
        await downloadMessage.delete()
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception:
        try:
            print("Matn/J: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

#                                                                                  Telegram: @nabilanavab
