# fileName : plugins/dm/callBack/toImages.py
# copyright ©️ 2021 nabilanavab

import os
import fitz
import time
import shutil
from PIL import Image
from pdf import PROCESS
from pyromod import listen
from pyrogram import filters
from Configs.dm import Config
from plugins.checkPdf import checkPdf
from plugins.progress import progress
from pyrogram.types import ForceReply
from pyrogram import Client as ILovePDF
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InputMediaPhoto, InputMediaDocument
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
#------------------->

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

mediaDoc={}; media={}

cancel=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Bekor qilish 💤", callback_data="cancelP2I")
            ]
        ]
    )

canceled=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Bekor qilindi 🍄", callback_data="canceled")
            ]
        ]
    )

completed=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Tugallandi 😎", callback_data="completed")
            ]
        ]
    )

#--------------->
#--------> PDF TO IMAGES
#------------------->

KcbExtract = ["KIA|", "KIR|", "KDA|", "KDR|", "KIS|", "KDS|"]
EXTRACT = filters.create(lambda _, __, query: query.data in ["IA", "DA", "IR", "DR", "IS", "DS"])
KEXTRACT = filters.create(lambda _, __, query: query.data.startswith(tuple(KcbExtract)))

# Extract pgNo (with unknown pdf page number)
@ILovePDF.on_callback_query(EXTRACT)
async def _EXTRACT(bot, callbackQuery):
    try:
        # CALLBACK DATA
        data = callbackQuery.data
        # CHECK USER PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        # ADD USER TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        
        # ACCEPTING PAGE NUMBER
        if data in ["IA", "DA"]:
            nabilanavab = False
        # RANGE (START:END)
        elif data in ["IR", "DR"]:
            nabilanavab = True; i = 0
            # 5 EXCEPTION, BREAK MERGE PROCESS
            while(nabilanavab):
                if i >= 5:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`5 marta urinish.. Jarayon bekor qilindi..`😏"
                    )
                    break
                i += 1
                # PYROMOD ADD-ON (PG NO REQUEST)
                needPages=await bot.ask(
                    text="__PDFni Rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /exit ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                # EXIT PROCESS
                if needPages.text=="/exit":
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Jarayon bekor qilindi..` 😏"
                    )
                    break
                # SPLIT STRING TO START & END
                pageStartAndEnd=list(needPages.text.replace('-',':').split(':'))
                # IF STRING HAVE MORE THAN 2 LIMITS
                if len(pageStartAndEnd) > 2:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.`🚶"
                    )
                # CORRECT FORMAT
                elif len(pageStartAndEnd)==2:
                    start=pageStartAndEnd[0]
                    end=pageStartAndEnd[1]
                    if start.isdigit() and end.isdigit():
                        if (1 <= int(pageStartAndEnd[0])):
                            if (int(pageStartAndEnd[0]) < int(pageStartAndEnd[1])):
                                nabilanavab=False
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
                # ERPOR MESSAGE
                else:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.`🚶"
                    )
        # SINGLE PAGES
        else:
            newList=[]
            nabilanavab=True; i=0
            # 5 REQUEST LIMIT
            while(nabilanavab):
                if i >= 5:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`5 marta urinish.. Jarayon bekor qilindi..`😏"
                    )
                    break
                i+=1
                # PYROMOD ADD-ON
                needPages=await bot.ask(
                    text="__PDFni rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /exit ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                # SPLIT PAGE NUMBERS (,)
                singlePages=list(needPages.text.replace(',',':').split(':'))
                # PROCESS CANCEL
                if needPages.text=="/exit":
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Jarayon bekor qilindi..` 😏"
                    )
                    break
                # PAGE NUMBER LESS THAN 100
                elif 1 <= len(singlePages) <= 100:
                    # CHECK IS PAGE NUMBER A DIGIT(IF ADD TO A NEW LIST)
                    for i in singlePages:
                        if i.isdigit():
                            newList.append(i)
                    if newList != []:
                        nabilanavab=False
                        break
                    # AFTER SORTING (IF NO DIGIT PAGES RETURN)
                    elif newList==[]:
                        await bot.send_message(
                            callbackQuery.message.chat.id,
                            "`Hech qanday raqam topilmadi..`😏"
                        )
                        continue
                else:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Nimadir xato ketdi..`😅"
                    )
        if nabilanavab==True:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        if nabilanavab==False:
            # DOWNLOAD MESSAGE
            downloadMessage=await callbackQuery.message.reply_text(
                text="`PDFingiz yuklab olinmqoda..` ⏳", quote=True
            )
            file_id=callbackQuery.message.reply_to_message.document.file_id
            fileSize=callbackQuery.message.reply_to_message.document.file_size
            # DOWNLOAD PROGRESS
            c_time=time.time()
            downloadLoc=await bot.download_media(
                message=file_id,
                file_name=f"{callbackQuery.message.message_id}/pdf.pdf",
                progress=progress,
                progress_args=(
                    fileSize,
                    downloadMessage,
                    c_time
                )
            )
            # CHECK DOWNLOAD COMPLETED/CANCELED
            if downloadLoc is None:
                PROCESS.remove(callbackQuery.message.chat.id)
                return
            # CHECK PDF CODEC, ENCRYPTION..
            checked=await checkPdf(
                f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery
            )
            if not(checked=="pass"):
                await downloadMessage.delete()
                return
            # OPEN PDF WITH FITZ
            doc=fitz.open(f'{callbackQuery.message.message_id}/pdf.pdf')
            number_of_pages=doc.pageCount
            if data in ["IA", "DA"]:
                pageStartAndEnd=[1, int(number_of_pages)]
            if data in ["IR", "DR"]:
                if not(int(pageStartAndEnd[1]) <= int(number_of_pages)):
                    await downloadMessage.edit(
                        f"`PDFingizda faqat{number_of_pages}ta sahifa bor!`"
                    )
                    PROCESS.remove(callbackQuery.message.chat.id)
                    shutil.rmtree(f"{callbackQuery.message.message_id}")
                    return
            zoom=2
            mat=fitz.Matrix(zoom, zoom)
            if data in ["IA", "DA", "IR", "DR"]:
                if int(int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])) >= 11:
                    await bot.pin_chat_message(
                        chat_id=callbackQuery.message.chat.id,
                        message_id=downloadMessage.message_id,
                        disable_notification=True,
                        both_sides=True
                    )
                await downloadMessage.edit(
                    text=f"`Umumiy sahifalar: {int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])}..⏳`",
                    reply_markup=cancel
                )
                totalPgList=range(int(pageStartAndEnd[0]), int(pageStartAndEnd[1])+1)
                cnvrtpg=0
                for i in range(0, len(totalPgList), 10):
                    pgList=totalPgList[i:i+10]
                    os.mkdir(f'{callbackQuery.message.message_id}/pgs')
                    for pageNo in pgList:
                        page=doc.loadPage(pageNo-1)
                        pix=page.getPixmap(matrix = mat)
                        cnvrtpg+=1
                        if cnvrtpg % 5 == 0:
                            await downloadMessage.edit(
                                text=f"`O'zgartirildi: {cnvrtpg}/{int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])}ta sahifalar.. 🤞`",
                                reply_markup=cancel
                            )
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                await downloadMessage.edit(
                                    text=f"`Bekor qilindi {cnvrtpg}/{int(int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0]))}ta sahifalar.. 🙄`",
                                    reply_markup=canceled
                                )
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        with open(
                            f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg','wb'
                        ):
                            pix.writePNG(f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg')
                    await downloadMessage.edit(
                        text=f"`Albom tayyorlanmqoda..` 🤹",
                        reply_markup=cancel
                    )
                    directory=f'{callbackQuery.message.message_id}/pgs'
                    imag=[os.path.join(directory, file) for file in os.listdir(directory)]
                    imag.sort(key=os.path.getctime)
                    if data in ["IA", "IR"]:
                        media[callbackQuery.message.chat.id]=[]
                    else:
                        mediaDoc[callbackQuery.message.chat.id]=[]
                    for file in imag:
                        qualityRate=95
                        for i in range(200):
                            if os.path.getsize(file) >= 1000000:
                                picture = Image.open(file)
                                picture.save(
                                    file, "JPEG",
                                    optimize=True,
                                    quality=qualityRate
                                )
                                qualityRate-=5
                            else:
                                if data in ["IA", "IR"]:
                                    media[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaPhoto(media=file)
                                    )
                                else:
                                    mediaDoc[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaDocument(media=file)
                                    )
                                break
                    await downloadMessage.edit(
                        text=f"`Yuborilmoqda: {cnvrtpg}/{int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])} sahifalar.. 🐬`",
                        reply_markup=cancel
                    )
                    if data in ["IA", "IR"]:
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_photo")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                media[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del media[callbackQuery.message.chat.id]
                    if data in ["DA", "DR"]:
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_document")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                mediaDoc[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del mediaDoc[callbackQuery.message.chat.id]
                    shutil.rmtree(f'{callbackQuery.message.message_id}/pgs')
                PROCESS.remove(callbackQuery.message.chat.id)
                doc.close()
                await downloadMessage.edit(
                    text=f'`Yuborish tugallandi.. `🏌️',
                    reply_markup=completed
                )
                shutil.rmtree(f'{callbackQuery.message.message_id}')
            if data in ["IS", "DS"]:
                if int(len(newList)) >= 11:
                    await bot.pin_chat_message(
                        chat_id=callbackQuery.message.chat.id,
                        message_id=downloadMessage.message_id,
                        disable_notification=True,
                        both_sides=True
                    )
                totalPgList = []
                for i in newList:
                    if 1 <= int(i) <= number_of_pages:
                        totalPgList.append(i)
                if len(totalPgList) < 1:
                    await downloadMessage.edit(
                        text=f"`PDFingizda faqat{number_of_pages}ta sahifa mavjud`😏"
                    )
                    PROCESS.remove(callbackQuery.message.chat.id)
                    shutil.rmtree(f'{callbackQuery.message.message_id}')
                    doc.close()
                    return
                await downloadMessage.edit(
                    text=f"`Umumiy sahifalar: {len(totalPgList)}ta..⏳`",
                    reply_markup=cancel
                )
                cnvrtpg = 0
                for i in range(0, len(totalPgList), 10):
                    pgList = totalPgList[i:i+10]
                    os.mkdir(f'{callbackQuery.message.message_id}/pgs')
                    for pageNo in pgList:
                        if int(pageNo) <= int(number_of_pages):
                            page=doc.loadPage(int(pageNo)-1)
                            pix=page.getPixmap(matrix = mat)
                        else:
                            continue
                        cnvrtpg+=1
                        if cnvrtpg % 5 == 0:
                            await downloadMessage.edit(
                                text=f"`O'zgartirildi: {cnvrtpg}/{len(totalPgList)} ta sahifalar.. 🤞`",
                                reply_markup=cancel
                            )
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                await downloadMessage.edit(
                                    text=f"`Bekor qilindi {cnvrtpg}/{len(totalPgList)}ta sahifalar.. 🙄`",
                                    reply_markup=canceled
                                )
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        with open(
                            f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg','wb'
                        ):
                            pix.writePNG(f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg')
                    try:
                        await downloadMessage.edit(
                            text=f"`Albom tayyorlanmoqda..` 🤹",
                            reply_markup=cancel
                        )
                    except Exception:
                        pass
                    directory=f'{callbackQuery.message.message_id}/pgs'
                    imag=[os.path.join(directory, file) for file in os.listdir(directory)]
                    imag.sort(key=os.path.getctime)
                    if data=="IS":
                        media[callbackQuery.message.chat.id]=[]
                    else:
                        mediaDoc[callbackQuery.message.chat.id]=[]
                    for file in imag:
                        qualityRate=95
                        for i in range(200):
                            if os.path.getsize(file) >= 1000000:
                                picture=Image.open(file)
                                picture.save(
                                    file, "JPEG",
                                    optimize=True,
                                    quality=qualityRate
                                )
                                qualityRate-=5
                            else:
                                if data=="IS":
                                    media[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaPhoto(media=file)
                                    )
                                else:
                                    mediaDoc[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaDocument(media=file)
                                    )
                                break
                    await downloadMessage.edit(
                        text=f"`Yuborilmoqda: {cnvrtpg}/{len(totalPgList)}ta sahifalar.. 🐬`",
                        reply_markup=cancel
                    )
                    if data == "IS":
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_photo")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                media[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del media[callbackQuery.message.chat.id]
                    if data == "DS":
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_document")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                mediaDoc[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del mediaDoc[callbackQuery.message.chat.id]
                    shutil.rmtree(f'{callbackQuery.message.message_id}/pgs')
                PROCESS.remove(callbackQuery.message.chat.id)
                doc.close()
                await downloadMessage.edit(
                    text=f'`Yuborish tugallandi.. `🏌️',
                    callback_data=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton("Tugallandi 😎", callback_data="completed")
                        ]]
                    )
                )
                shutil.rmtree(f'{callbackQuery.message.message_id}')
    except Exception as e:
        try:
            print("image: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f'{callbackQuery.message.message_id}')
        except Exception:
            pass


# Extract pgNo (with known pdf page number)
@ILovePDF.on_callback_query(KEXTRACT)
async def _KEXTRACT(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        data=callbackQuery.data[:3]
        _, number_of_pages=callbackQuery.data.split("|")
        PROCESS.append(callbackQuery.message.chat.id)
        if data in ["KIA", "KDA"]:
            nabilanavab=False
        elif data in ["KIR", "KDR"]:
            nabilanavab=True; i=0
            while(nabilanavab):
                if i >= 5:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`5 marta urinish.. Jarayon bekor qilindi..`😏"
                    )
                    break
                i+=1
                needPages=await bot.ask(
                    text="__PDFni rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /exit ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                if needPages.text=="/exit":
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Jarayon bekor qilindi..` 😏"
                    )
                    break
                pageStartAndEnd=list(needPages.text.replace('-',':').split(':'))
                if len(pageStartAndEnd) > 2:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.`🚶"
                    )
                elif len(pageStartAndEnd)==2:
                    start=pageStartAndEnd[0]
                    end=pageStartAndEnd[1]
                    if start.isdigit() and end.isdigit():
                        if (1 <= int(pageStartAndEnd[0])):
                            if int(pageStartAndEnd[0]) < int(pageStartAndEnd[1]) and int(pageStartAndEnd[1]) <= int(number_of_pages):
                                nabilanavab=False
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
                            "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.` 🧠"
                        )
                else:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Sintaksis Xato!!! \n\nXATOLIK: Boshlanish va oxirigi sahifa raqamini kiriting. \nMasalan: 5:9\n Bunda Pdfingizdan 5imchidan 9inchigacga sahifalarni olib beradi.` 🚶"
                    )
        elif data in ["KIS", "KDS"]:
            newList=[]
            nabilanavab=True; i=0
            while(nabilanavab):
                if i >= 5:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`5 marta urinish.. Jarayon bekor qilindi`😏"
                    )
                    break
                i+=1
                needPages=await bot.ask(
                    text="__PDFni Rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /exit ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                singlePages=list(needPages.text.replace(',',':').split(':'))
                if needPages.text=="/exit":
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`Jarayon bekor qilindi..` 😏"
                    )
                    break
                elif 1 <= len(singlePages) <= 100:
                    for i in singlePages:
                        if i.isdigit() and int(i) <= int(number_of_pages):
                            newList.append(i)
                    if newList != []:
                        nabilanavab=False
                        break
                    elif newList==[]:
                        await bot.send_message(
                            callbackQuery.message.chat.id,
                            "`hech qanday raqam topilmadi..`😏"
                        )
                        continue
                else:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "`100 sahifa yetarli..`😅"
                    )
        if nabilanavab==True:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        if nabilanavab==False:
            downloadMessage=await callbackQuery.message.reply_text(
                text="`PDFingiz yuklab olinmoqda..` ⏳", quote=True
            )
            file_id=callbackQuery.message.reply_to_message.document.file_id
            fileSize=callbackQuery.message.reply_to_message.document.file_size
            # DOWNLOAD PROGRESS
            c_time=time.time()
            downloadLoc=await bot.download_media(
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
            checked = await checkPdf(
                f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery
            )
            if not(checked=="pass"):
                await downloadMessage.delete()
                return
            doc=fitz.open(f'{callbackQuery.message.message_id}/pdf.pdf')
            number_of_pages=doc.pageCount
            if data in ["KIA", "KDA"]:
                pageStartAndEnd=[1, int(number_of_pages)]
            if data in ["KIR", "KDR"]:
                if not(int(pageStartAndEnd[1]) <= int(number_of_pages)):
                    await downloadMessage.edit(
                        text=f"`PDFingizda faqat {number_of_pages}ta sahifa mavjud`"
                    )
                    PROCESS.remove(callbackQuery.message.chat.id)
                    shutil.rmtree(f"{callbackQuery.message.message_id}")
                    return
            zoom=2
            mat=fitz.Matrix(zoom, zoom)
            if data in ["KIA", "KDA", "KIR", "KDR"]:
                if int(int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])) >= 11:
                    await bot.pin_chat_message(
                        chat_id=callbackQuery.message.chat.id,
                        message_id=downloadMessage.message_id,
                        disable_notification=True,
                        both_sides=True
                    )
                await downloadMessage.edit(
                    text=f"`Umumiy sahifalar: {int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])}ta..⏳`",
                    reply_markup=cancel
                )
                totalPgList=range(int(pageStartAndEnd[0]), int(pageStartAndEnd[1])+1)
                cnvrtpg=0
                for i in range(0, len(totalPgList), 10):
                    pgList=totalPgList[i:i+10]
                    os.mkdir(f'{callbackQuery.message.message_id}/pgs')
                    for pageNo in pgList:
                        page=doc.loadPage(pageNo-1)
                        pix=page.getPixmap(matrix = mat)
                        cnvrtpg+=1
                        if cnvrtpg % 5 == 0:
                            await downloadMessage.edit(
                                text=f"`O'zgartirildi: {cnvrtpg}/{int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])}ta sahifalar.. 🤞`",
                                reply_markup=cancel
                            )
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                await downloadMessage.edit(
                                    text=f"`Bekor qilindi {cnvrtpg}/{int(int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0]))}ta sahifalar.. 🙄`",
                                    reply_markup=canceled
                                )
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        with open(
                            f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg','wb'
                        ):
                            pix.writePNG(f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg')
                    try:
                        await downloadMessage.edit(
                            text=f"`Albom tayyorlanmoqda..` 🤹",
                            reply_markup=cancel
                        )
                    except Exception:
                        pass
                    directory=f'{callbackQuery.message.message_id}/pgs'
                    imag=[os.path.join(directory, file) for file in os.listdir(directory)]
                    imag.sort(key=os.path.getctime)
                    if data in ["KIA", "KIR"]:
                        media[callbackQuery.message.chat.id]=[]
                    else:
                        mediaDoc[callbackQuery.message.chat.id]=[]
                    for file in imag:
                        qualityRate=95
                        for i in range(200):
                            if os.path.getsize(file) >= 1000000:
                                picture=Image.open(file)
                                picture.save(
                                    file, "JPEG",
                                    optimize=True,
                                    quality=qualityRate
                                )
                                qualityRate-=5
                            else:
                                if data in ["KIA", "KIR"]:
                                    media[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaPhoto(media=file)
                                    )
                                else:
                                    mediaDoc[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaDocument(media=file)
                                    )
                                break
                    await downloadMessage.edit(
                        text=f"`Yuborilmoqda: {cnvrtpg}/{int(pageStartAndEnd[1])+1 - int(pageStartAndEnd[0])}ta sahifalar.. 🐬`",
                        reply_markup=cancel
                    )
                    if data in ["KIA", "KIR"]:
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_photo")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                media[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del media[callbackQuery.message.chat.id]
                    if data in ["KDA", "KDR"]:
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_document")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                mediaDoc[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del mediaDoc[callbackQuery.message.chat.id]
                    shutil.rmtree(f'{callbackQuery.message.message_id}/pgs')
                PROCESS.remove(callbackQuery.message.chat.id)
                doc.close()
                await downloadMessage.edit(
                    text=f'`Yuborish tugallandi.. `🏌️',
                    reply_markup=completed
                )
                shutil.rmtree(f'{callbackQuery.message.message_id}')
            if data in ["KIS", "KDS"]:
                if int(len(newList)) >= 11:
                    await bot.pin_chat_message(
                        chat_id=callbackQuery.message.chat.id,
                        message_id=downloadMessage.message_id,
                        disable_notification=True,
                        both_sides=True
                    )
                totalPgList=[]
                for i in newList:
                    if 1 <= int(i) <= number_of_pages:
                        totalPgList.append(i)
                if len(totalPgList) < 1:
                    await downloadMessage.edit(
                        text=f"`PDFingizda faqat {number_of_pages}ta sahifa mavjud`😏"
                    )
                    PROCESS.remove(callbackQuery.message.chat.id)
                    shutil.rmtree(f'{callbackQuery.message.message_id}')
                    doc.close()
                    return
                await downloadMessage.edit(
                    text=f"`Umumiy sahifalar: {len(totalPgList)}ta..⏳`",
                    reply_markup=cancel
                )
                cnvrtpg = 0
                for i in range(0, len(totalPgList), 10):
                    pgList = totalPgList[i:i+10]
                    os.mkdir(f'{callbackQuery.message.message_id}/pgs')
                    for pageNo in pgList:
                        if int(pageNo) <= int(number_of_pages):
                            page=doc.loadPage(int(pageNo)-1)
                            pix=page.getPixmap(matrix = mat)
                        else:
                            continue
                        cnvrtpg+=1
                        if cnvrtpg % 5 == 0:
                            await downloadMessage.edit(
                                text=f"`O'zgartirildi: {cnvrtpg}/{len(totalPgList)}ta sahifalar.. 🤞`",
                                reply_markup=cancel
                            )
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                await downloadMessage.edit(
                                    text=f"`Bekor qilindi {cnvrtpg}/{len(totalPgList)}ta sahifalar.. 🙄`",
                                    reply_markup=canceled
                                )
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        with open(
                            f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg','wb'
                        ):
                            pix.writePNG(f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg')
                    try:
                        await downloadMessage.edit(
                            text=f"`Albom tayyorlanmoqda..` 🤹",
                            reply_markup=cancel
                        )
                    except Exception:
                        pass
                    directory=f'{callbackQuery.message.message_id}/pgs'
                    imag=[os.path.join(directory, file) for file in os.listdir(directory)]
                    imag.sort(key=os.path.getctime)
                    if data=="KIS":
                        media[callbackQuery.message.chat.id]=[]
                    else:
                        mediaDoc[callbackQuery.message.chat.id]=[]
                    for file in imag:
                        qualityRate=95
                        for i in range(200):
                            if os.path.getsize(file) >= 1000000:
                                picture=Image.open(file)
                                picture.save(
                                    file, "JPEG",
                                    optimize=True,
                                    quality=qualityRate
                                )
                                qualityRate-=5
                            else:
                                if data=="KIS":
                                    media[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaPhoto(media=file)
                                    )
                                else:
                                    mediaDoc[
                                        callbackQuery.message.chat.id
                                    ].append(
                                        InputMediaDocument(media=file)
                                    )
                                break
                    await downloadMessage.edit(
                        text=f"`Yuborilmoqda: {cnvrtpg}/{len(totalPgList)}ta sahifalar.. 🐬`",
                        reply_markup=cancel
                    )
                    if data=="KIS":
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_photo")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                media[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del media[callbackQuery.message.chat.id]
                    if data=="KDS":
                        if callbackQuery.message.chat.id not in PROCESS:
                            try:
                                shutil.rmtree(f'{callbackQuery.message.message_id}')
                                doc.close()
                                return
                            except Exception:
                                return
                        await callbackQuery.message.reply_chat_action("upload_document")
                        try:
                            await bot.send_media_group(
                                callbackQuery.message.chat.id,
                                mediaDoc[callbackQuery.message.chat.id]
                            )
                        except Exception:
                            del mediaDoc[callbackQuery.message.chat.id]
                    shutil.rmtree(f'{callbackQuery.message.message_id}/pgs')
                PROCESS.remove(callbackQuery.message.chat.id)
                doc.close()
                await downloadMessage.edit(
                    text=f'`Yuborish tugallandi.. `🏌️',
                    reply_markup=completed
                )
                shutil.rmtree(f'{callbackQuery.message.message_id}')
    except Exception as e:
        try:
            print("Rasm: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f'{callbackQuery.message.message_id}')
        except Exception:
            pass

#                                                                                  Telegram: @nabilanavab
