# fileName : plugins/dm/document.py
# copyright ÂŠī¸ 2021 nabilanavab

import os
import fitz
import shutil
import convertapi
from pdf import PDF
from PIL import Image
from time import sleep
from pdf import invite_link
from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as ILovePDF
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> convertAPI instance
#------------------->

if Config.CONVERT_API is not None:
    convertapi.api_secret = Config.CONVERT_API

#--------------->
#--------> MAXIMUM FILE SIZE (IF IN config var.)
#------------------->

if Config.MAX_FILE_SIZE:
    MAX_FILE_SIZE=int(os.getenv("MAX_FILE_SIZE"))
    MAX_FILE_SIZE_IN_kiB=MAX_FILE_SIZE * (10 **6 )
else:
    MAX_FILE_SIZE=False


PDF_THUMBNAIL=Config.PDF_THUMBNAIL

#--------------->
#--------> FILES TO PDF SUPPORTED CODECS
#------------------->

suprtedFile = [
    ".jpg", ".jpeg", ".png"
]                                       # Img to pdf file support

suprtedPdfFile = [
    ".epub", ".xps", ".oxps",
    ".cbz", ".fb2"
]                                      # files to pdf (zero limits)

suprtedPdfFile2 = [
    ".csv", ".doc", ".docx", ".dot",
    ".dotx", ".log", ".mpp", ".mpt",
    ".odt", ".pot", ".potx", ".pps",
    ".ppsx", ".ppt", ".pptx", ".pub",
    ".rtf", ".txt", ".vdx", ".vsd",
    ".vsdx", ".vst", ".vstx", ".wpd",
    ".wps", ".wri", ".xls", ".xlsb",
    ".xlsx", ".xlt", ".xltx", ".xml"
]                                       # file to pdf (ConvertAPI limit)

#--------------->
#--------> LOCAL VARIABLES
#------------------->

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz đ"

pdfReplyMsg = """`Ushbu faylni nima qilishni xohlaysiz.?`

Fayl Nomi : `{}`
Fayl Hajmi : `{}`"""

bigFileUnSupport = """Haddan tashqari yuk tufayli Administrator botga pdf yuklash limiti {}mb deb belgiladi đ

`Iltimos menga {}mbdan kichkina pdflar yuboring` đ"""

imageAdded = """`Sizning Pdf faylingizga {}ta fayl qo'shildi..`đ¤

Pdf yaratish uchun /generate komandasini yuboringđ¤"""

errorEditMsg = """Nimadir xato ketdi..đ

XATO: `{}`

Qo'llab quvvatlash guruhi @azik_projects_support """

feedbackMsg = "[Men haqimda taklif va shikoyatlaringizni yozishingiz mumkin đ](https://t.me/azik_projects_support)"

forceSubMsg = """To'xtang [{}](tg://user?id={})..!!

Katta yuzaga keladigan yuk tufayli bu botdan faqat kanal a'zolari foydalanishi mumkin đļ

Bu mendan foydalanish uchun quyida ko'rsatilgan kanalga qo'shilishingiz kerakligini bildiradi!

qo'shilgandan keyin "Qayta urinishâģī¸" tugmasini bosing.. đ"""

button=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Administratorđ§âđģ",
                    url="https://t.me/azik_developer"
                )
            ]
       ]
    )

#--------------->
#--------> PDF REPLY BUTTON
#------------------->

pdfReply=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Ma'lumot â­", callback_data="pdfInfo"),
                InlineKeyboardButton("Ko'rib chiqish đŗī¸", callback_data="preview")
            ],[
                InlineKeyboardButton("Rasmga o'tkazish đŧī¸", callback_data="toImage"),
                InlineKeyboardButton("Matnga o'tkazish âī¸", callback_data="toText")
            ],[
                InlineKeyboardButton("Himoyalash đ", callback_data="encrypt"),
                InlineKeyboardButton("Himoyadan ochish đ",callback_data="decrypt")
            ],[
                InlineKeyboardButton("Siqish đī¸", callback_data="compress"),
                InlineKeyboardButton("Aylantirish đ¤¸", callback_data="rotate")
            ],[
                InlineKeyboardButton("Kesish âī¸", callback_data="split"),
                InlineKeyboardButton("Birlashtirish đ§Ŧ", callback_data="merge")
            ],[
                InlineKeyboardButton("Pechat qo'yish âĸī¸", callback_data="stamp"),
                InlineKeyboardButton("Qayta nomlash âī¸", callback_data="rename")
            ],[
                InlineKeyboardButton("Yopish đĢ", callback_data="closeALL")
            ]
        ]
    )

#--------------->
#--------> Config var.
#------------------->

UPDATE_CHANNEL=Config.UPDATE_CHANNEL
BANNED_USERS=Config.BANNED_USERS
ADMIN_ONLY=Config.ADMIN_ONLY
ADMINS=Config.ADMINS

#--------------->
#--------> REPLY TO DOCUMENTS/FILES
#------------------->

@ILovePDF.on_message(filters.private & filters.document & ~filters.edited)
async def documents(bot, message):
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
                await bot.send_message(
                    message.chat.id,
                    forceSubMsg.format(
                        message.from_user.first_name, message.chat.id
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("đ Proyektlar kanaliga ulanish đ", url=invite_link.invite_link)
                            ],[
                                InlineKeyboardButton("Qayta urinish âģī¸", callback_data="refresh")
                            ]
                        ]
                    )
                )
                return
        # CHECKS IF USER BANNED/ADMIN..
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse,
                reply_markup=button
            )
            return
        
        isPdfOrImg = message.document.file_name        # file name
        fileSize = message.document.file_size          # file size
        fileNm, fileExt = os.path.splitext(isPdfOrImg) # seperate name & extension
        
        # REPLY TO LAGE FILES/DOCUMENTS
        if MAX_FILE_SIZE and fileSize >= int(MAX_FILE_SIZE_IN_kiB):
            await message.reply_text(
                bigFileUnSupport.format(MAX_FILE_SIZE, MAX_FILE_SIZE), quote=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "đ Proyektlar kanali đ",
                                url="https://t.me/azik_projects"
                            )
                        ]
                    ]
                )
            )
            return
        
        # IMAGE AS FILES (ADDS TO PDF FILE)
        elif fileExt.lower() in suprtedFile:
            try:
                imageDocReply = await message.reply_text(
                    "`Rasmingiz yuklab olinmoqda..âŗ`", quote=True
                )
                if not isinstance(PDF.get(message.chat.id), list):
                    PDF[message.chat.id]=[]
                await message.download(
                    f"{message.chat.id}/{message.chat.id}.jpg"
                )
                img = Image.open(
                    f"{message.chat.id}/{message.chat.id}.jpg"
                ).convert("RGB")
                PDF[message.chat.id].append(img)
                await imageDocReply.edit(
                    imageAdded.format(len(PDF[message.chat.id]))
                )
            except Exception as e:
                await imageDocReply.edit(
                    errorEditMsg.format(e)
                )
            
        # REPLY TO .PDF FILE EXTENSION
        elif fileExt.lower() == ".pdf":
            try:
                pdfMsgId = await message.reply_text(
                    "Qayta ishlanmoqda..đļ", quote=True
                )
                sleep(0.5)
                await pdfMsgId.edit(
                    text=pdfReplyMsg.format(
                        isPdfOrImg, await gSF(fileSize)
                    ),
                    reply_markup=pdfReply
                )
            except Exception:
                pass
        
        # FILES TO PDF (PYMUPDF/FITZ)
        elif fileExt.lower() in suprtedPdfFile:
            try:
                pdfMsgId = await message.reply_text(
                    "`Faylingiz yuklab olinmqoda..âŗ`", quote=True
                )
                await message.download(
                    f"{message.message_id}/{isPdfOrImg}"
                )
                await pdfMsgId.edit(
                    "`PDF yaratilmoqda..`đ"
                )
                Document=fitz.open(
                    f"{message.message_id}/{isPdfOrImg}"
                )
                b=Document.convert_to_pdf()
                pdf=fitz.open("pdf", b)
                pdf.save(
                    f"{message.message_id}/{fileNm}.pdf",
                    garbage=4,
                    deflate=True,
                )
                pdf.close()
                await pdfMsgId.edit(
                    "`Sizga pdf yuborilmoqda..`đī¸"
                )
                await bot.send_chat_action(
                    message.chat.id, "upload_document"
                )
                await message.reply_document(
                    file_name=f"{fileNm}.pdf",
                    document=open(f"@azik_pdfbot.pdf", "rb"), #{message.message_id}/{fileNm} via 
                    thumb=PDF_THUMBNAIL,
                    caption=f"`Yaratildi: {fileExt} orqali`",
                    quote=True
                )
                await pdfMsgId.delete()
                shutil.rmtree(f"{message.message_id}")
                sleep(5)
                await bot.send_chat_action(
                    message.chat.id, "typing"
                )
                await bot.send_message(
                    message.chat.id, feedbackMsg,
                    disable_web_page_preview = True
                )
            except Exception as e:
                try:
                    shutil.rmtree(f"{message.message_id}")
                    await pdfMsgId.edit(
                        errorEditMsg.format(e)
                    )
                except Exception:
                    pass
        
        # FILES TO PDF (CONVERTAPI)
        elif fileExt.lower() in suprtedPdfFile2:
            if Config.CONVERT_API is None:
                pdfMsgId = await message.reply_text(
                    "`Adminstrator bilan bog'laning đ`",
                    quote=True
                )
                return
            else:
                try:
                    pdfMsgId = await message.reply_text(
                        "`Faylingiz yuklab olinmoqda..âŗ`", quote=True
                    )
                    await message.download(
                        f"{message.message_id}/{isPdfOrImg}"
                    )
                    await pdfMsgId.edit(
                        "`PDF yaratilmoqda..`đ"
                    )
                    try:
                        await convertapi.convert(
                            "pdf",
                            {
                                "Fayl": f"{message.message_id}/{isPdfOrImg}"
                            },
                            from_format = fileExt[1:],
                        ).save_files(
                            f"{message.message_id}/{fileNm}.pdf"
                        )
                    except Exception:
                        try:
                            shutil.rmtree(f"{message.message_id}")
                            await pdfMsgId.edit(
                                "ConvertAPI limitlari.. Admin bilan bog'laning"
                            )
                            return
                        except Exception:
                            pass
                    await bot.send_chat_action(
                        message.chat.id, "upload_document"
                    )
                    await message.reply_document(
                        file_name=f"{fileNm}.pdf",
                        document=open(f"@azik_pdfbot.pdf", "rb"), #{message.message_id}/{fileNm} via 
                        thumb=PDF_THUMBNAIL,
                        caption=f"`Yaratildi: {fileExt} orqali`",
                        quote=True
                    )
                    await pdfMsgId.delete()
                    shutil.rmtree(f"{message.message_id}")
                    sleep(5)
                    await bot.send_chat_action(
                        message.chat.id, "typing"
                    )
                    await bot.send_message(
                        message.chat.id, feedbackMsg,
                        disable_web_page_preview=True
                    )
                except Exception:
                    pass
        
        # UNSUPPORTED FILES
        else:
            try:
                await message.reply_text(
                    "`Qo'llab-quvvatlanmaydigan fayl..đ`", quote=True
                )
            except Exception:
                pass
    
    except Exception as e:
        print("plugins/dm/document : ", e)

#                                                                                  Telegram: @nabilanavab
