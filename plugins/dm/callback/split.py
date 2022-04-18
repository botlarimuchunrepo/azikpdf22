# fileName : plugins/dm/callBack/split.py
# copyright ©️ 2021 nabilanavab

import time
import shutil
from pdf import PROCESS
from pyromod import listen
from pyrogram import filters
from Configs.dm import Config
from plugins.checkPdf import checkPdf
from plugins.progress import progress
from pyrogram.types import ForceReply
from pyrogram import Client as ILovePDF
from PyPDF2 import PdfFileWriter, PdfFileReader
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

pdfInfoMsg = """`Ushbu fayl bilan nima qilishni xohlaysiz.?`

Fayl Nomi: `{}`
Fayl Hajmi: `{}`

`Sahifalar soni: {}`ta✌️
"""

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

# ----- ----- ----- ----- ----- ----- ----- CALLBACK SPLITTING PDF ----- ----- ----- ----- ----- ----- -----

split = filters.create(lambda _, __, query: query.data == "split")
Ksplit = filters.create(lambda _, __, query: query.data.startswith("Ksplit|"))

splitR = filters.create(lambda _, __, query: query.data == "splitR")
splitS = filters.create(lambda _, __, query: query.data == "splitS")

KsplitR = filters.create(lambda _, __, query: query.data.startswith("KsplitR|"))
KsplitS = filters.create(lambda _, __, query: query.data.startswith("KsplitS|"))



# Split pgNo (with unknown pdf page number)
@ILovePDF.on_callback_query(split)
async def _split(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "PDFni kesish »      \n\nUmumiy sahifalar soni:__ `noma'lum`",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Sahifalar soni bilan kesish ✂ ", callback_data="splitR")
                    ],[
                        InlineKeyboardButton("Bitta sahifani kesish ✂ ", callback_data="splitS")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data="BTPM")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Split pgNo (with known pdf page number)
@ILovePDF.on_callback_query(Ksplit)
async def _Ksplit(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"PDFni kesish »         \n\nUmumiy sahifalar soni: {number_of_pages}ta__",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Sahifalar soni bilan kesish ✂ ", callback_data=f"KsplitR|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Bitta sahifani kesish ✂ ", callback_data=f"KsplitS|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"KBTPM|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Split (with unknown pdf page number)
@ILovePDF.on_callback_query(splitR)
async def _splitROrS(bot, callbackQuery):
    try:
        # CHECKS IF USER IN PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # PYROMOD (ADD-ON)
        nabilanavab = True; i = 0
        while(nabilanavab):
            # REQUEST FOR PG NUMBER (MAX. LIMIT 5)
            if i >= 5:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`5 marta urinish.. Jarayon bekor qilindi..`😏"
                )
                break
            i += 1
            needPages = await bot.ask(
                text="PDFni kesish. Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /exit ni bosing.__",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            # IF /exit PROCESS CANCEL
            if needPages.text == "/exit":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Jarayon bekor qilindi..` 😏"
                )
                break
            pageStartAndEnd=list(needPages.text.replace('-',':').split(':'))
            if len(pageStartAndEnd) > 2:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi. `🚶"
                )
            elif len(pageStartAndEnd) == 2:
                start = pageStartAndEnd[0]
                end = pageStartAndEnd[1]
                if start.isdigit() and end.isdigit():
                    if (1 <= int(pageStartAndEnd[0])):
                        if (int(pageStartAndEnd[0]) < int(pageStartAndEnd[1])):
                            nabilanavab = False
                            break
                        else:
                            await bot.send_message(
                                callbackQuery.message.chat.id,
                                "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.`🚶"
                            )
                    else:
                        await bot.send_message(
                            callbackQuery.message.chat.id,
                            "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.`🚶"
                        )
                else:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.`🧠"
                    )
            else:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.` 🚶"
                )
        # nabilanavab=True iff AN ERROR OCCURS
        if nabilanavab == True:
            PROCESS.remove(callbackQuery.message.chat.id)
        if nabilanavab == False:
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
                "`Yuklab olish tugallandi..🤞`"
            )
            checked = await checkPdf(f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
            splitInputPdf = PdfFileReader(f"{callbackQuery.message.message_id}/pdf.pdf")
            number_of_pages = splitInputPdf.getNumPages()
            if not(int(pageStartAndEnd[1]) <= int(number_of_pages)):
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Birinchi sahifalar sonini tekshiring` 😏"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                shutil.rmtree(f"{callbackQuery.message.message_id}")
                return
            splitOutput = PdfFileWriter()
            for i in range(int(pageStartAndEnd[0])-1, int(pageStartAndEnd[1])):
                splitOutput.addPage(
                    splitInputPdf.getPage(i)
                )
            file_path=f"{callbackQuery.message.message_id}/split.pdf"
            with open(file_path, "wb") as output_stream:
                splitOutput.write(output_stream)
            await callbackQuery.message.reply_chat_action("upload_document")
            await callbackQuery.message.reply_document(
                file_name="Kesilgan PDF @azik_pdfbot.pdf", thumb=PDF_THUMBNAIL, quote=True,
                document=f"{callbackQuery.message.message_id}/split.pdf",
                caption=f"`Ushbu kesilgan pdf avvalgi pdfning {pageStartAndEnd[0]}` dan  `{pageStartAndEnd[1]}` gacha sahifalarni o'z ichiga oladi.\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
            )
            await downloadMessage.delete()
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("Kesilgan: ",e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

# Split (with unknown pdf page number)
@ILovePDF.on_callback_query(splitS)
async def _splitS(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        PROCESS.append(callbackQuery.message.chat.id)
        newList = []
        nabilanavab = True; i = 0
        while(nabilanavab):
            if i >= 5:
                bot.send_message(
                    callbackQuery.message.chat.id,
                    "`5 marta urinish.. Jarayon bekor qilindi..`😏"
                )
                break
            i += 1
            needPages = await bot.ask(
                text="PDFni kesish. Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini  bilan kiriting.\nMasalan 3 yoki 7\n\nBekor qilish uchun /exit ni bosing.",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            singlePages = list(needPages.text.replace(',',':').split(':'))
            if needPages.text == "/exit":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Jarayon bekor qilindi..` 😏"
                )
                break
            elif 1 <= len(singlePages) <= 100:
                try:
                    for i in singlePages:
                        if i.isdigit():
                            newList.append(i)
                    if newList != []:
                        nabilanavab = False
                        break
                    elif newList == []:
                        await bot.send_message(
                            callbackQuery.message.chat.id,
                            "`Hech qanday raqamni topib bo'lmadi..`😏"
                        )
                        continue
                except Exception:
                    pass
            else:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Nimadir xato ketdi..`😅"
                )
        if nabilanavab == True:
            PROCESS.remove(callbackQuery.message.chat.id)
        if nabilanavab == False:
            downloadMessage = await callbackQuery.message.reply_text(
                text="`PDFingiz yuklab olinmoqda..`⏳", quote=True
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
                "`Yuklab olish tugallandi..🤞`"
            )
            checked = await checkPdf(f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
            splitInputPdf=PdfFileReader(f'{callbackQuery.message.message_id}/pdf.pdf')
            number_of_pages=splitInputPdf.getNumPages()
            splitOutput=PdfFileWriter()
            for i in newList:
                if int(i) <= int(number_of_pages):
                    splitOutput.addPage(
                        splitInputPdf.getPage(
                            int(i)-1
                        )
                    )
            with open(
                f"{callbackQuery.message.message_id}/split.pdf", "wb"
            ) as output_stream:
                splitOutput.write(output_stream)
            await callbackQuery.message.reply_chat_action("upload_document")
            await callbackQuery.message.reply_document(
                file_name="Kesilgan PDF @azik_pdfbot.pdf", thumb=PDF_THUMBNAIL,
                document=f"{callbackQuery.message.message_id}/split.pdf",
                caption=f"Sahifalar : `{newList}`ta\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊", quote=True
            )
            await downloadMessage.delete()
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("Kesilgan ;", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

# Split (with known pdf page number)
@ILovePDF.on_callback_query(KsplitR)
async def _KsplitR(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        PROCESS.append(callbackQuery.message.chat.id)
        _, number_of_pages=callbackQuery.data.split("|")
        number_of_pages=int(number_of_pages)
        nabilanavab = True; i = 0
        while(nabilanavab):
            if i >= 5:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`5 marta urinish.. Jarayon bekor qilindi...`😏"
                )
                break
            i += 1
            needPages = await bot.ask(
                text=f"PDFni kesish » Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4\nUmumiy sahifalar: __`{number_of_pages}`ta\n\nBekor qilish uchun /exit ni bosing.__",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            if needPages.text == "/exit":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Jarayon bekor qilindi..` 😏"
                )
                break
            pageStartAndEnd=list(needPages.text.replace('-',':').split(':'))
            if len(pageStartAndEnd) > 2:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5inchidan 9inchigacga sahifalarni olib beradi.`🚶"
                )
            elif len(pageStartAndEnd) == 2:
                start = pageStartAndEnd[0]
                end = pageStartAndEnd[1]
                if start.isdigit() and end.isdigit():
                    if (int(1) <= int(start) and int(start) < number_of_pages):
                        if (int(start) < int(end) and int(end) <= number_of_pages):
                            nabilanavab = False
                            break
                        else:
                            await bot.send_message(
                                callbackQuery.message.chat.id,
                                "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5inchidan 9inchigacha sahifalarni olib beradi.`🚶"
                            )
                    else:
                        await bot.send_message(
                            callbackQuery.message.chat.id,
                            "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5inchidan 9inchigacha sahifalarni olib beradi.`🚶"
                        )
                else:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5inchidan 9inchigacha sahifalarni olib beradi.` 🚶"
                    )
            else:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5inchidan 9inchigacha sahifalarni olib beradi.` 🚶"
                )
        if nabilanavab == True:
            PROCESS.remove(callbackQuery.message.chat.id)
        if nabilanavab == False:
            downloadMessage = await callbackQuery.message.reply_text(
                text="`PDFingiz yuklab olinmqoda..` ⏳", quote=True
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
                "`Yuklab olish tugallandi..🤞`"
            )
            splitInputPdf = PdfFileReader(f"{callbackQuery.message.message_id}/pdf.pdf")
            number_of_pages = splitInputPdf.getNumPages()
            if not(int(pageStartAndEnd[1]) <= int(number_of_pages)):
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Birinchi sahifalar sonini tekshiring!` 😏"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                shutil.rmtree(f"{callbackQuery.message.message_id}")
                return
            splitOutput = PdfFileWriter()
            for i in range(int(pageStartAndEnd[0])-1, int(pageStartAndEnd[1])):
                splitOutput.addPage(
                    splitInputPdf.getPage(i)
                )
            file_path=f"{callbackQuery.message.message_id}/split.pdf"
            with open(file_path, "wb") as output_stream:
                splitOutput.write(output_stream)
            await callbackQuery.message.reply_chat_action("upload_document")
            await callbackQuery.message.reply_document(
                file_name="Kesilgan via @azik_pdfbot.pdf", thumb=PDF_THUMBNAIL, quote=True,
                document=f"{callbackQuery.message.message_id}/split.pdf",
                caption=f"Ushbu pdf avvalgi pdfning `{pageStartAndEnd[0]}`dan  `{pageStartAndEnd[1]}`gacha sahifalarni o'z ichiga oladi.\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
            )
            await downloadMessage.delete()
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("Kesilgan :", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

# Split (with unknown pdf page number)
@ILovePDF.on_callback_query(KsplitS)
async def _KsplitS(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        PROCESS.append(callbackQuery.message.chat.id)
        _, number_of_pages = callbackQuery.data.split("|")
        newList = []
        nabilanavab = True; i = 0
        while(nabilanavab):
            if i >= 5:
                bot.send_message(
                    callbackQuery.message.chat.id,
                    "`5 marta urinish.. Jarayon bekor qilindi..`😏"
                )
                break
            i += 1
            needPages = await bot.ask(
                text=f"PDFni kesish » Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4\nUmumiy sahifalar: __`{number_of_pages}`ta\n\nBekor qilish uchun /exit ni bosing.__",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            singlePages = list(needPages.text.replace(',',':').split(':'))
            if needPages.text == "/exit":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Jarayon bekor qilindi..` 😏"
                )
                break
            elif 1 <= int(len(singlePages)) and int(len(singlePages)) <= 100:
                try:
                    for i in singlePages:
                        if (i.isdigit() and int(i) <= int(number_of_pages)):
                            newList.append(i)
                    if newList == []:
                        await bot.send_message(
                             callbackQuery.message.chat.id,
                            f"`{number_of_pages} dan kichik raqamlarni kiriting..`😏"
                        )
                        continue
                    else:
                        nabilanavab = False
                        break
                except Exception:
                    pass
            else:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Nimdir xato ketdi..`😅"
                )
        if nabilanavab == True:
            PROCESS.remove(callbackQuery.message.chat.id)
        if nabilanavab == False:
            downloadMessage = await callbackQuery.message.reply_text(
                text="`PDFingiz yuklab olinmoqda..`⏳", quote=True
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
                "`Yuklab olish tugallandi..🤞`"
            )
            splitInputPdf = PdfFileReader(f'{callbackQuery.message.message_id}/pdf.pdf')
            number_of_pages = splitInputPdf.getNumPages()
            splitOutput = PdfFileWriter()
            for i in newList:
                if int(i) <= int(number_of_pages):
                    splitOutput.addPage(
                        splitInputPdf.getPage(
                            int(i)-1
                        )
                    )
            with open(
                f"{callbackQuery.message.message_id}/split.pdf", "wb"
            ) as output_stream:
                splitOutput.write(output_stream)
            await callbackQuery.message.reply_chat_action("upload_document")
            await callbackQuery.message.reply_document(
                file_name="Kesilgan via @azik_pdfbot.pdf", thumb=PDF_THUMBNAIL,
                document=f"{callbackQuery.message.message_id}/split.pdf",
                caption=f"Sahifalar: `{newList}`ta\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊", quote=True
            )
            await downloadMessage.delete()
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("Kesilgan: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

#                                                                                                                                    Telegram: @nabilanavab
