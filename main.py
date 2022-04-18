import os
import traceback
import logging
import shutil
import time, math
import fitz
import config

from pdf import PDF
from fpdf import FPDF
from pdf import PROCESS
from pdf import invite_link
from time import sleep
from PIL import Image
from time import sleep

from pyrogram import filters
from pyrogram.types import InputMediaPhoto
from pyrogram import Client, idle
from pyrogram import StopPropagation, filters
from pyrogram.types import Message
from pyrogram.types import Message
from pyrogram import Client as ILovePDF
from pyrogram.types import ForceReply
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


from plugins.fileSize import get_size_format as gSF
from plugins.toKnown import toKnown
from plugins.progress import progress
from plugins.checkPdf import checkPdf
from PDFNetPython3.PDFNetPython import PDFDoc, Optimizer, SDFDoc, PDFNet
from PyPDF2 import PdfFileMerger, PdfFileWriter, PdfFileReader


from pyromod import listen
from Configs.dm import Config

from handlers.broadcast import broadcast
from handlers.check_user import handle_user_status
from handlers.database import Database




# Logging info
logging.basicConfig(
    level = logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

LOG_CHANNEL = config.LOG_CHANNEL
AUTH_USERS = config.AUTH_USERS
DB_URL = config.DB_URL
DB_NAME = config.DB_NAME

db = Database(DB_URL, DB_NAME)

PDF = {}            # save images for generating pdf
PROCESS = []        # to check current process
invite_link = None

# PLUGIN DIRECTORY
plugin = dict(
    root = "plugins"
)

bot = Client(
    "ILovePDF",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    parse_mode = "markdown",
    api_hash=config.API_HASH,
)


# fileName : plugins/dm/start.py
# copyright ©️ 2021 nabilanavab


#--------------->
#--------> LOCAL VARIABLES
#------------------->

welcomeMsg = """Salom!! Men bilan siz PDF fayllarni ko'p funksiyalarni amalga oshirishingiz mumkin  🥳\n
Asosiy xususiyatlardan ba'zilari:
◍ `Rasmlarni PDF ga o'tkazish`
◍ `PDFni rasmlarga o'tkazish`
◍ `Botni o'zida matnni PDF qilish`
◍ `PDFlarni himoylash, birlashtirish, oldindan ko'rish, aylantirish, pechat qo'yish va boshqalar`

Proyektlar kanali: @azik_projects 💎
"""

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"

forceSubMsg = """To'xtang [{}](tg://user?id={})..!!
Katta yuzaga keladigan yuk tufayli bu botdan faqat kanal a'zolari foydalanishi mumkin 🚶
Bu mendan foydalanish uchun quyida ko'rsatilgan kanalga qo'shilishingiz kerakligini bildiradi!
qo'shilgandan keyin "Qayta urinish♻️" tugmasini bosing.. 😅"""

aboutDev = """@azik_developer tomonidan yaratilgan
Proyektlar kanali: @azik_projects
Bizning boshqa proyektlarimizga ham tashrif buyuring👇
[Fayl Yuklash📥](https://t.me/azik_faylyuklabot)
[Kino Kanal🎞](https://t.me/azik_cinema)"""

exploreBotEdit = """
Bot @azik_projects mahsuloti😎
Asosiy xususiyatlar:
◍ `Rasmlarni PDF ga o'tkazish`
◍ `PDFni rasmlarga o'tkazish`
◍ `Faylni PDFga o'tkazish`
◍ `Botni o'zida matnni PDF qilish`
◍ `PDFlarni himoylash, birlashtirish, oldindan ko'rish, aylantirish, pechat qo'yish va boshqalar`
Taklif va shikoyatlaringizni qo'llab quvvatlash guruhiga yo'llashingiz mumkin @azik_projects_support 👈
"""

foolRefresh = "Wait a minute who are you 😐"

#--------------->
#--------> config vars
#------------------->

UPDATE_CHANNEL=Config.UPDATE_CHANNEL
BANNED_USERS=Config.BANNED_USERS
ADMIN_ONLY=Config.ADMIN_ONLY
ADMINS=Config.ADMINS

#--------------->
#--------> /start (START MESSAGE)
#------------------->

@bot.on_message(filters.private & ~filters.edited & filters.command(["start2"]))
async def start(bot, message):
        global invite_link
        await message.reply_chat_action("typing")
        # CHECK IF USER BANNED, ADMIN ONLY..
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse, quote=True
            )
            return
        # CHECK USER IN CHANNEL (IF UPDATE_CHANNEL ADDED)
        if UPDATE_CHANNEL:
            try:
                await bot.get_chat_member(
                    str(UPDATE_CHANNEL), message.chat.id
                )
            except Exception:
                if invite_link == None:
                    invite_link = await bot.create_chat_invite_link(
                        int(UPDATE_CHANNEL)
                    )
                await message.reply_text(
                    forceSubMsg.format(
                        message.from_user.first_name, message.chat.id
                    ),
                    joinButton1 = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🌟 Proyektlar kanali 🌟",
                                    url = invite_link.invite_link
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Qayta urinish ♻️",
                                    callback_data = "refresh"
                                )
                            ]
                        ]
                    )
                )
                await message.delete()
                return
        
        await message.reply_text(
            welcomeMsg.format(
                message.from_user.first_name,
                message.chat.id
            ),
            disable_web_page_preview=True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌟 AziK ProJecTs 🌟",
                            callback_data="strtDevEdt"
                        ),
                        InlineKeyboardButton(
                            "Bot bilan tanishish 🎊",
                            callback_data="exploreBot"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Yopish ⛔️",
                            callback_data="close"
                        )
                    ]
                ]
            )
        )
        # DELETES /start MESSAGE
        await message.delete()

#--------------->
#--------> START CALLBACKS
#------------------->

strtDevEdt = filters.create(lambda _, __, query: query.data == "strtDevEdt")
exploreBot = filters.create(lambda _, __, query: query.data == "exploreBot")
refresh = filters.create(lambda _, __, query: query.data == "refresh")
close = filters.create(lambda _, __, query: query.data == "close")
back = filters.create(lambda _, __, query: query.data == "back")

@bot.on_callback_query(strtDevEdt)
async def _strtDevEdt(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            aboutDev,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Fayl Yuklash📥",
                            url = "https://t.me/azik_faylyuklabot"
                        ),
                        InlineKeyboardButton(
                            "AziK ProJecTs🦾",
                            url = "https://t.me/azik_projects"
                        ),
                            InlineKeyboardButton(
                            "Kino Kanal🎞",
                            url = "https://t.me/azik_cinema"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Uy sahifa 🏡",
                            callback_data = "back"
                        ),
                         InlineKeyboardButton(
                            "Yopish ⛔️",
                            callback_data = "close"
                        )
                    ]
                ]
            )
        )
        return
    except Exception as e:
        print(e)

@bot.on_callback_query(exploreBot)
async def _exploreBot(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            exploreBotEdit,
            reply_markup = InlineKeyboardMarkup(
              [
                    [
                        InlineKeyboardButton(
                            "AziK ProJecTs🦾",
                            url = "https://t.me/azik_projects"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Uy sahifa 🏡",
                            callback_data = "back"
                        ),
                         InlineKeyboardButton(
                            "Yopish ⛔️",
                            callback_data = "close"
                        )
                    ]
                ]
            )
        )
        return
    except Exception as e:
        print(e)

@bot.on_callback_query(back)
async def _back(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            welcomeMsg.format(
                callbackQuery.from_user.first_name,
                callbackQuery.message.chat.id
            ),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌟 AziK ProJecTs 🌟",
                            callback_data = "strtDevEdt"
                        ),
                        InlineKeyboardButton(
                            "Bot bilan tanishish 🎊",
                            callback_data = "exploreBot"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Yopish ⛔️",
                            callback_data = "close"
                        )
                    ]
                ]
            )
        )
        return
    except Exception as e:
        print(e)

@bot.on_callback_query(refresh)
async def _refresh(bot, callbackQuery):
    try:
        # CHECK USER IN CHANNEL (REFRESH CALLBACK)
        await bot.get_chat_member(
            str(UPDATE_CHANNEL),
            callbackQuery.message.chat.id
        )
        # IF USER NOT MEMBER (ERROR FROM TG, EXECUTE EXCEPTION)
        await callbackQuery.edit_message_text(
            welcomeMsg.format(
                callbackQuery.from_user.first_name,
                callbackQuery.message.chat.id
            ),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌟 AziK ProJecTs🌟",
                            callback_data = "strtDevEdt"
                        ),
                        InlineKeyboardButton(
                            "Bot bilan tanishish 🎊",
                            callback_data = "exploreBot"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Yopish ⛔️",
                            callback_data = "close"
                        )
                    ]
                ]
            )
        )
    except Exception:
        try:
            # IF NOT USER ALERT MESSAGE (AFTER CALLBACK)
            await bot.answer_callback_query(
                callbackQuery.id,
                text = foolRefresh,
                show_alert = True,
                cache_time = 0
            )
        except Exception as e:
            print(e)

@bot.on_callback_query(close)
async def _close(bot, callbackQuery):
    try:
        await bot.delete_messages(
            chat_id = callbackQuery.message.chat.id,
            message_ids = callbackQuery.message.message_id
        )
        return
    except Exception as e:
        print(e)

#                                                                                  Telegram: @nabilanavab

encryptedMsg = """`Fayl himoyalangan` 🔐
Fayl Nomi: `{}`
Fayl Hajmi: `{}`
`Sahifalar soni: {}`ta✌"""

codecMsg = """__Men bu turdagi fayl bilan hech narsa bajarmayman!!!__
🐉  `KODEK XATOLIGI`  🐉"""

#--------------->
#--------> CHECKS PDF CODEC, IS ENCRYPTED OR NOT
#------------------->

async def checkPdf(file_path, callbackQuery):
    try:
        chat_id=callbackQuery.message.chat.id
        message_id=callbackQuery.message.message_id
        
        fileName=callbackQuery.message.reply_to_message.document.file_name
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        
        with fitz.open(file_path) as doc:
            
            isEncrypted=doc.is_encrypted
            number_of_pages=doc.pageCount
            
            if isEncrypted:
                await callbackQuery.edit_message_text(
                    encryptedMsg.format(
                        fileName, await gSF(fileSize), number_of_pages
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Himoyalash 🔓",
                                    callback_data = "Kdecrypt"
                                )
                            ]
                        ]
                    )
                )
                if callbackQuery.data not in ["decrypt", "Kdecrypt"]:
                    PROCESS.remove(chat_id)
                    # try Coz(at the time of merge there is no such dir but checking)
                    try:
                        shutil.rmtree(f'{message_id}')
                    except Exception:
                        pass
                return "encrypted"
            
            else:
                await toKnown(callbackQuery, number_of_pages)
                return "pass"
            
    except Exception:
        await callbackQuery.edit_message_text(
            text=codecMsg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "KODEKDA XATO ❌",
                            callback_data="error"
                        )
                    ]
                ]
            )
        )
        PROCESS.remove(chat_id)
        # try Coz(at the time of merge there is no such dir but checking)
        try:
            shutil.rmtree(f'{message_id}')
        except Exception:
            pass
        return "notPdf"


UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"

imageAdded = """`{} ta sahifa sizning pdfingizga qo'shildi..`🤓\n
PDF yaratish uchun /pdfyaratish komandasini yuboring 🤞"""

forceSubMsg = """To'xtang [{}](tg://user?id={})..!!
Katta yuzaga keladigan yuk tufayli bu botdan faqat kanal a'zolari foydalanishi mumkin 🚶
Bu mendan foydalanish uchun quyida ko'rsatilgan kanalga qo'shilishingiz kerakligini bildiradi!
qo'shilgandan keyin "Qayta urinish♻️" tugmasini bosing.. 😅"""

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
#--------> REPLY TO IMAGES
#------------------->

@bot.on_message(filters.private & ~filters.edited & filters.photo)
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
                                    "🌟 Proyektlar kanali 🌟",
                                    url=invite_link.invite_link
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Qayta urinish ♻️",
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
            "`Rasmingiz yuklab olinmoqda..⏳`", quote=True
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

@bot.on_message(filters.private & filters.command(["pdfyaratish"]) & ~filters.edited)
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
        newName = str(message.text.replace("/pdfyaratish", ""))
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

#------------------->


async def progress(current, t, total, message, start):
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🚫Bekor qilish", callback_data = "closeme")
            ]
        ]
    )
    now = time.time()
    diff = now - start
    
    if round(diff % 10) in [0, 8] or current == total:
        # if round(current / total * 100, 0) % 10 == 0:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress = "[{0}{1}] \n".format(
            ''.join(["●" for _ in range(math.floor(percentage / 5))]),
            ''.join(["○" for _ in range(20 - math.floor(percentage / 5))])
        )
        tmp = progress + "**\nTugallandi ✅ : **{0}/{1}\n**Tezligi 🚀:** {2}/s\n**Qolgan vaqt ⏳:** {3}".format(
            await gSF(current),
            await gSF(total),
            await gSF(speed),
            TimeFormatter(time_to_completion)
        )
        
        await message.edit_text(
            text="Yuklab olinmoqda..🌡️\n{}".format(
                tmp
            ),
            reply_markup=reply_markup
        )


#--------------->
#--------> TIME FORMATTER
#------------------->

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " kun, ") if days else "") + \
        ((str(hours) + " soat, ") if hours else "") + \
        ((str(minutes) + " minut, ") if minutes else "") + \
        ((str(seconds) + " sekund, ") if seconds else "") + \
        ((str(milliseconds) + " millisekund, ") if milliseconds else "")
    return tmp[:-2]

#                                                                                  Telegram: 

#------------------->

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"

imageAdded = """`{} ta sahifa sizning pdfingizga qo'shildi..`🤓
PDF yaratish uchun /generate komandasini yuboring 🤞"""

forceSubMsg = """To'xtang [{}](tg://user?id={})..!!
Katta yuzaga keladigan yuk tufayli bu botdan faqat kanal a'zolari foydalanishi mumkin 🚶
Bu mendan foydalanish uchun quyida ko'rsatilgan kanalga qo'shilishingiz kerakligini bildiradi!
qo'shilgandan keyin "Qayta urinish♻️" tugmasini bosing.. 😅"""

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
#--------> REPLY TO IMAGES
#------------------->

@bot.on_message(filters.private & ~filters.edited & filters.photo)
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
                                    "🌟 Proyektlar kanali 🌟",
                                    url=invite_link.invite_link
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Qayta urinish ♻️",
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
            "`Rasmingiz yuklab olinmoqda..⏳`", quote=True
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


#                                                                                  Telegr


#------------------->

pdfReply = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Ma'lumot ⭐", callback_data="pdfInfo"),
                InlineKeyboardButton("Ko'rib chiqish 🗳️", callback_data="preview")
            ],[
                InlineKeyboardButton("Rasmga o'tkazish 🖼️", callback_data="toImage"),
                InlineKeyboardButton("Matnga o'tkazish ✏️", callback_data="toText")
            ],[
                InlineKeyboardButton("Himoyalash 🔐", callback_data="encrypt"),
                InlineKeyboardButton("Himoyadan ochish 🔓",callback_data="decrypt")
            ],[
                InlineKeyboardButton("Siqish 🗜️", callback_data="compress"),
                InlineKeyboardButton("Aylantirish 🤸", callback_data="rotate")
            ],[
                InlineKeyboardButton("Kesish ✂️", callback_data="split"),
                InlineKeyboardButton("Birlashtirish 🧬", callback_data="merge")
            ],[
                InlineKeyboardButton("Pechat qo'yish ™️", callback_data="stamp"),
                InlineKeyboardButton("Qayta nomlash ✏️", callback_data="rename")
            ],[
                InlineKeyboardButton("Yopish 🚫", callback_data="closeALL")
            ]
        ]
    )

BTPMcb = """`Ushbu fayl bilan nima qilishni xohlaysiz.?`
Fayl Nomi: `{}`
Fayl hajmi: `{}`"""

KBTPMcb = """`Ushbu fayl bilan nima qilishni xohlaysiz.?`
Fayl Nomi: `{}`
Fayl hajmi: `{}`
`Pdfda: {}`ta sahifa mavjud✌️"""

#--------------->
#--------> LOCAL VARIABLES
#------------------->

"""
______BUYRUQLAR______
I : rasm holatida
D : fayl holatida
K : pgNo known
A : Hammasini chiqarish
R : Sahifalar soni bilan chiqarish
S : Bitta sahifani chiqarish
BTPM : Pdf xabariga qaytish
KBTPM : Pdf xabariga qaytish (ma'lum sahifalar)
"""

#--------------->
#--------> PDF TO IMAGES (CB/BUTTON)
#------------------->


BTPM = filters.create(lambda _, __, query: query.data == "BTPM")
toImage = filters.create(lambda _, __, query: query.data == "toImage")
KBTPM = filters.create(lambda _, __, query: query.data.startswith("KBTPM|"))
KtoImage = filters.create(lambda _, __, query: query.data.startswith("KtoImage|"))

I = filters.create(lambda _, __, query: query.data == "I")
D = filters.create(lambda _, __, query: query.data == "D")
KI = filters.create(lambda _, __, query: query.data.startswith("KI|"))
KD = filters.create(lambda _, __, query: query.data.startswith("KD|"))


# Extract pgNo (with unknown pdf page number)
@bot.on_callback_query(I)
async def _I(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__Pdfni Rasmga (rasm formatida) o'tkazish \nUmumiy safifalar: Noma'lum😐__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hamma betlarni chiqarish 🙂", callback_data="IA")
                    ],[
                        InlineKeyboardButton("Sahifalar soni bilan chiqarish 🙂", callback_data="IR")
                    ],[
                        InlineKeyboardButton("Bitta sahifani chiqarish 🌝", callback_data="IS")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data="toImage")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Extract pgNo (with unknown pdf page number)
@bot.on_callback_query(D)
async def _D(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__Pdfni Rasmga (fayl formatida) o'tkazish \nUmumiy sahifalar: Noma'lum😐__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hamma betlarni chiqarish 🙂", callback_data="DA")
                    ],[
                        InlineKeyboardButton("Sahifalar soni bilan chiqarish 🙂", callback_data="DR")
                    ],[
                        InlineKeyboardButton("Bitta sahifani chiqarish 🌝", callback_data="DS")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data="toImage")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Extract pgNo (with known pdf page number)
@bot.on_callback_query(KI)
async def _KI(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Pdfni Rasmga (rasm formatida) o'tkazish   \nUmumiy sahifalar: {number_of_pages}ta__ 🌟",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hamma betlarni chiqarish 🙂", callback_data=f"KIA|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Sahifalar soni bilan chiqarish 🙂", callback_data=f"KIR|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Bitta sahifani chiqarish 🌝", callback_data=f"KIS|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"KtoImage|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Extract pgNo (with known pdf page number)
@bot.on_callback_query(KD)
async def _KD(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Pdf ni Rasmga (fayl formatida) o'tkazish \nUmumiy sahifalar: {number_of_pages}ta__ 🌟",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hamma betlarni chiqarish 🙂", callback_data=f"KDA|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Sahifalar soni bilan chiqarish 🙂", callback_data=f"KDR|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Bitta sahifani chiqarish 🌝", callback_data=f"KDS|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"KtoImage|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

# pdf to images (with unknown pdf page number)
@bot.on_callback_query(toImage)
async def _toImage(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__Pdfni Rasm sifatida yuborish     \nUmumiy sahifalar: Noma'lum__ 😐",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Rasm formatda 🖼️", callback_data="I")
                    ],[
                        InlineKeyboardButton("Fayl formatda 📂", callback_data="D")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data="BTPM")
                    ]
                ]
            )
        )
    except Exception:
        pass

# pdf to images (with known page Number)
@bot.on_callback_query(KtoImage)
async def _KtoImage(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Pdfni Rasm sifatida yuborish  \nUmumiy sahifalar: {number_of_pages}ta__ 😐",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Rasm formatda🖼️", callback_data=f"KI|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Fayl formatda 📂", callback_data=f"KD|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"KBTPM|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

# back to pdf message (unknown page number)
@bot.on_callback_query(BTPM)
async def _BTPM(bot, callbackQuery):
    try:
        fileName=callbackQuery.message.reply_to_message.document.file_name
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        
        await callbackQuery.edit_message_text(
            BTPMcb.format(
                fileName, await gSF(fileSize)
            ),
            reply_markup = pdfReply
        )
    except Exception:
        pass

# back to pdf message (with known page Number)
@bot.on_callback_query(KBTPM)
async def _KBTPM(bot, callbackQuery):
    try:
        fileName = callbackQuery.message.reply_to_message.document.file_name
        fileSize = callbackQuery.message.reply_to_message.document.file_size
        
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            KBTPMcb.format(
                fileName, await gSF(fileSize), number_of_pages
            ),
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Ma'lumot ⭐", callback_data=f"KpdfInfo|{number_of_pages}"),
                        InlineKeyboardButton("Ko'rib chiqish 🗳️", callback_data="Kpreview")
                    ],[
                        InlineKeyboardButton("Rasmga o'tkazish 🖼️", callback_data=f"KtoImage|{number_of_pages}"),
                        InlineKeyboardButton("Matnga o'tkazish ✏️", callback_data=f"KtoText|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Himoyalash 🔐", callback_data=f"Kencrypt|{number_of_pages}"),
                        InlineKeyboardButton("Himoyadan ochish 🔓", callback_data=f"notEncrypted")
                    ],[
                        InlineKeyboardButton("Siqish 🗜️", callback_data=f"Kcompress"),
                        InlineKeyboardButton("Aylantirish 🤸", callback_data=f"Krotate|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Kesish ✂️", callback_data=f"Ksplit|{number_of_pages}"),
                        InlineKeyboardButton("Birlashtirish 🧬",callback_data="merge")
                    ],[
                        InlineKeyboardButton("Pechat qo'yish ™️",callback_data=f"Kstamp|{number_of_pages}"),
                        InlineKeyboardButton("Qayta nomlash ✏️",callback_data="rename")
                    ],[
                        InlineKeyboardButton("Yopish 🚫", callback_data="closeALL")
                    ]
                ]
            )
        )
    except Exception:
        pass

#                                                                                             T


#------------------->

error = filters.create(lambda _, __, query: query.data == "error")
closeme = filters.create(lambda _, __, query: query.data == "closeme")
closeALL = filters.create(lambda _, __, query: query.data == "closeALL")
underDev = filters.create(lambda _, __, query: query.data == "underDev")
canceled = filters.create(lambda _, __, query: query.data == "canceled")
completed = filters.create(lambda _, __, query: query.data == "completed")
cancelP2I = filters.create(lambda _, __, query: query.data == "cancelP2I")
notEncrypted = filters.create(lambda _, __, query: query.data == "notEncrypted")


@bot.on_callback_query(underDev)
async def _underDev(bot, callbackQuery):
    try:
        await callbackQuery.answer(
            "Bu xususiyat ishlab chiqilmoqda ⛷️"
        )
    except Exception:
        pass


@bot.on_callback_query(error)
async def _error(bot, callbackQuery):
    try:
        await callbackQuery.answer(
            "Xatolik.. 😏"
        )
    except Exception:
        pass


@bot.on_callback_query(closeme)
async def _closeme(bot, callbackQuery):
    try:
        try:
            await callbackQuery.message.delete()
        except Exception:
            pass
        await callbackQuery.answer(
            "Jarayon bekor qilindi.. 😏"
        )
        PROCESS.remove(callbackQuery.message.chat.id)
    except Exception:
        pass


@bot.on_callback_query(notEncrypted)
async def _notEncrypted(bot, callbackQuery):
    try:
        await callbackQuery.answer(
            "Fayl himoyalanmagan.. 👀"
        )
    except Exception:
        pass


@bot.on_callback_query(closeALL)
async def _closeALL(bot, callbackQuery):
    try:
        await callbackQuery.message.delete()
        await callbackQuery.message.reply_to_message.delete()
    except Exception as e:
        print(e)


@bot.on_callback_query(cancelP2I)
async def _cancelP2I(bot, callbackQuery):
    try:
        await callbackQuery.message.edit_reply_markup(
            InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("Bekor qilinmoqda.. 💤", callback_data="n")
                ]]
            )
        )
        PROCESS.remove(callbackQuery.message.chat.id)
    except Exception:
        pass


@bot.on_callback_query(canceled)
async def _canceled(bot, callbackQuery):
    try:
        await callbackQuery.answer(
            "Bu haqda hech qanday narsa yo'q.. 😅"
        )
    except Exception:
        pass


@bot.on_callback_query(completed)
async def _completed(bot, callbackQuery):
    try:
        await callbackQuery.answer(
            "Tamomlandi..🎉"
        )
    except Exception:
        pass

#------------------->

compressedCaption = """`Haqiqiy Hajmi : {}
Siqilgan hajmi : {}
Siqildi : {:.2f} %`\nESLATMA!! Siqish katta fayllarda yaxshi ishlaydi!\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"""

PDF_THUMBNAIL=Config.PDF_THUMBNAIL

#--------------->
#--------> PDF COMPRESSION
#------------------->

compress = filters.create(lambda _, __, query: query.data in ["compress", "Kcompress"])

@bot.on_callback_query(compress)
async def _compress(bot, callbackQuery):
    try:
        # CHECKS IF BOT DOING ANY WORK
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # CALLBACK DATA
        data = callbackQuery.data
        # DOWNLOAD MESSSAGE
        downloadMessage = await callbackQuery.message.reply_text(
            "`Pdfingiz yuklab olinmoqda..` ⏳", quote=True
        )
        input_file=f"{callbackQuery.message.message_id}/inCompress.pdf"
        output_file = f"{callbackQuery.message.message_id}/compressed.pdf"
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        fileNm=callbackQuery.message.reply_to_message.document.file_name
        fileNm, fileExt=os.path.splitext(fileNm)        # seperates name & extension
        
        # STARTED DOWNLOADING
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
        # CHECKS PDF DOWNLOADED OR NOT
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Siqish boshlandi..` 🗜️"
        )
        # CHECK PDF OR NOT(HERE compressed, SO PG UNKNOWN)
        if data == "compress":
            checked=await checkPdf(input_file, callbackQuery)
            if not(checked=="pass"):
                await downloadMessage.delete()
                return
        # Initialize the library
        PDFNet.Initialize()
        doc = PDFDoc(input_file)
        # Optimize PDF with the default settings
        doc.InitSecurityHandler()
        # Reduce PDF size by removing redundant information and
        # compressing data streams
        Optimizer.Optimize(doc)
        doc.Save(
            output_file, SDFDoc.e_linearized
        )
        doc.Close()
        
        # FILE SIZE COMPARISON (RATIO)
        initialSize=os.path.getsize(input_file)
        compressedSize=os.path.getsize(output_file)
        ratio=(1 - (compressedSize/initialSize)) * 100
        await bot.send_chat_action(
            callbackQuery.message.chat.id, "upload_document"
        )
        await downloadMessage.edit(
            "`Sizga yuborilmoqda..` 🏋️"
        )
        await callbackQuery.message.reply_document(
            file_name=f"@azik_pdfbot.pdf", quote=True, #{fileNm} via 
            document=open(output_file, "rb"),
            thumb=PDF_THUMBNAIL,
            caption=compressedCaption.format(
                await gSF(initialSize), await gSF(compressedSize), ratio
            )
        )
        await downloadMessage.delete()
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f"{callbackQuery.message.message_id}")
    except Exception as e:
        try:
            print("Siqish: " , e)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
            PROCESS.remove(callbackQuery.message.chat.id)
        except Exception:
            pass

#                                                                                  Tel    
    
 #------------------->

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> PDF DECRYPTION
#------------------->

decrypts = ["decrypt", "Kdecrypt"]
decrypt = filters.create(lambda _, __, query: query.data.startswith(tuple(decrypts)))

@bot.on_callback_query(decrypt)
async def _decrypt(bot, callbackQuery):
    try:
        # CHECKS IF BOT DOING ANY WORK
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇",
            )
            return
        # CALLBACK DATA
        data = callbackQuery.data
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # PYROMOD ADD-ON (ASK'S PASSWORD)
        password=await bot.ask(
            chat_id=callbackQuery.message.chat.id,
            reply_to_message_id=callbackQuery.message.message_id,
            text="__PDFni himoyasini ochish »\nEndi Pdfingiz parolini kiriting :__\n\nBekor qilish uchun /bekorqilish ni bosing.",
            filters=filters.text,
            reply_markup=ForceReply(True)
        )
        # CANCEL DECRYPTION PROCESS IF MESSAGE == /exit
        if password.text == "/bekorqilish":
            await password.reply(
                "`Jarayon bekor qilindi.. 😪`"
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        # DOWNLOAD MESSAGE
        downloadMessage=await callbackQuery.message.reply_text(
            "`Pdfingiz yuklab olinmoqda..` ⏳", quote=True
        )
        input_file=f"{callbackQuery.message.message_id}/pdf.pdf"
        output_pdf=f"{callbackQuery.message.message_id}/Decrypted.pdf"
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        fileNm=callbackQuery.message.reply_to_message.document.file_name
        fileNm, fileExt=os.path.splitext(fileNm)        # seperates name & extension
        # STARTED DOWNLOADING
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
        # CHECKS PDF DOWNLOAD OR NOT
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Paroldan ochish boshlandi.. 🔐`"
        )
        if data[0] != "K":
            checked = await checkPdf(f"{callbackQuery.message.message_id}/pdf.pdf", callbackQuery)
            if not(checked=="encrypted"):
                await downloadMessage.edit(
                    "Fayl himoyalanmagan..🙏🏻"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                shutil.rmtree(f"{callbackQuery.message.message_id}")
                return
        try:
            with fitz.open(input_file) as encrptPdf:
                encrptPdf.authenticate(f"{password.text}")
                encrptPdf.save(
                    output_pdf
                )
        except Exception:
            await downloadMessage.edit(
                f"Faylni ushbu `{password.text}` parol bilan shifrlab bo'lmadi! 🕸️"
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
            return
        # CHECH IF PROCESS CANCELLED
        if callbackQuery.message.chat.id not in PROCESS:
            shutil.rmtree(f'{callbackQuery.message.message_id}')
            return
        await downloadMessage.edit(
            "`Sizga yuborilmoqda..`🏋️"
        )
        await bot.send_chat_action(
            callbackQuery.message.chat.id, "upload_document"
        )
        await callbackQuery.message.reply_document(
            file_name=f"@azik_pdfbot.pdf", #{fileNm} via 
            document=open(output_pdf, "rb"),
            thumb=PDF_THUMBNAIL,
            caption="__Himoyalangan PDF\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊",
            quote=True
        )
        await downloadMessage.delete()
        shutil.rmtree(f"{callbackQuery.message.message_id}")
        PROCESS.remove(callbackQuery.message.chat.id)
    except Exception as e:
        try:
            print("decrypt: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

#                                                                                  Tele

#------------------->

encryptedFileCaption = "Sahifalar soni: {}ta\nParol 🔐 : ||{}||\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"

pdfInfoMsg = """`Ushbu fayl bilan nima qilishni xohlaysiz.?`
Fayl Nomi: `{}`
Fayl Jajmi: `{}`
`Sahifalar soni: {}`✌️
"""

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> PDF ENCRYPTION
#------------------->

encrypts = ["encrypt", "Kencrypt|"]
encrypt = filters.create(lambda _, __, query: query.data.startswith(tuple(encrypts)))

@bot.on_callback_query(encrypt)
async def _encrypt(bot, callbackQuery):
    try:
        # CHECKS IF BOT DOING ANY WORK
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇",
            )
            return
        # CALLBACK DATA
        data = callbackQuery.data
        # IF PDF PAGE MORE THAN 5000 (PROCESS CANCEL)
        if data[0] == "K":
            _, number_of_pages = callbackQuery.data.split("|")
            if int(number_of_pages) >= 5000:
                await bot.answer_callback_query(
                    callbackQuery.id,
                    text="`Iltimos, 5000 sahifadan kam bo'lgan pdf faylni yuboring` 🙄",
                    show_alert=True,
                    cache_time=0
                )
                return
        # ADDED TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # PYROMOD (PASSWORD REQUEST)
        password=await bot.ask(
            chat_id=callbackQuery.message.chat.id,
            reply_to_message_id = callbackQuery.message.message_id,
            text="__PDFni himoyalash »\nEndi PDFingizga qo'yadigan parolni kiriting :__\n\nBekor qilish uchun /v ni bosing.",
            filters=filters.text,
            reply_markup=ForceReply(True)
        )
        # CANCEL DECRYPTION PROCESS IF MESSAGE == /exit
        if password.text == "/bekorqilish":
            await password.reply(
                "`Jarayon bekor qilindi.. `😏"
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        # DOWNLOAD MESSAGE
        downloadMessage=await callbackQuery.message.reply_text(
            "`Pdfingiz yuklab olinmoqda..` ⏳", quote=True
        )
        file_id=callbackQuery.message.reply_to_message.document.file_id
        input_file=f"{callbackQuery.message.message_id}/pdf.pdf"
        output_pdf=f"{callbackQuery.message.message_id}/Encrypted.pdf"
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        fileNm=callbackQuery.message.reply_to_message.document.file_name
        fileNm, fileExt=os.path.splitext(fileNm)        # seperates name & extension
        # STARTED DOWNLOADING
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
        # CHECKS PDF DOWNLOAD OR NOT
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`Himoyalash boshlandi.. 🔐\nBu biroz vaqt olishi mumkin..💤`",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🚫Bekor qilish",
                            callback_data="closeme"
                        )
                    ]
                ]
            )
        )
        if data[0] != "K":
            checked = await checkPdf(input_file, callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
        # ENCRYPTION USING STRONG ALGORITHM (fitz/pymuPdf)
        with fitz.open(input_file) as encrptPdf:
            number_of_pages=encrptPdf.pageCount
            if int(number_of_pages) <= 5000:
                encrptPdf.save(
                    output_pdf,
                    encryption=fitz.PDF_ENCRYPT_AES_256,
                    owner_pw="nabil",
                    user_pw=f"{password.text}",
                    permissions=int(
                        fitz.PDF_PERM_ACCESSIBILITY |
                        fitz.PDF_PERM_PRINT |
                        fitz.PDF_PERM_COPY |
                        fitz.PDF_PERM_ANNOTATE
                    )
                )
            else:
                downloadMessage.edit(
                    "__Himoyalsh xatosi:\nIltimos, 5000 sahifadan kam bo'lgan pdf faylni yuboring__ 🥱"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                shutil.rmtree(f"{callbackQuery.message.message_id}")
                return
        if callbackQuery.message.chat.id not in PROCESS:
            shutil.rmtree(f'{callbackQuery.message.message_id}')
            return
        await downloadMessage.edit(
            "`Sizga yuborilmoqda..`🏋️"
        )
        await bot.send_chat_action(
            callbackQuery.message.chat.id, "upload_document"
        )
        # SEND ENCRYPTED PDF (AS REPLY)
        await callbackQuery.message.reply_document(
            file_name=f"@azik_pdfbot.pdf", #{fileNm} via 
            document=open(output_pdf, "rb"),
            thumb=PDF_THUMBNAIL,
            caption=encryptedFileCaption.format(
                number_of_pages, password.text
            ),
            quote=True
        )
        await downloadMessage.delete()
        shutil.rmtree(f"{callbackQuery.message.message_id}")
        PROCESS.remove(callbackQuery.message.chat.id)
    except Exception as e:
        try:
            print("Himoya: ",e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

#                                                                                  Tele

  
    #------------------->

MERGE = {}; MERGEsize = {}

if Config.MAX_FILE_SIZE:
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))
    MAX_FILE_SIZE_IN_kiB = MAX_FILE_SIZE * (10**6)
else:
    MAX_FILE_SIZE = False

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> MERGE PDFS
#------------------->

merge = filters.create(lambda _, __, query: query.data == "merge")

@bot.on_callback_query(merge)
async def _merge(bot, callbackQuery):
    try:
        # CHECK IF BOT DOING ANY WORK
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda..🙇"
            )
            return
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        fileId=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        fileNm=callbackQuery.message.reply_to_message.document.file_name
        fileNm, fileExt=os.path.splitext(fileNm)        # seperates name & extension
        # ADDING FILE ID & SIZE TO MERGE, MERGEsize LIST (FOR FUTURE USE)
        MERGE[callbackQuery.message.chat.id]=[fileId]
        MERGEsize[callbackQuery.message.chat.id]=[fileSize]
        # REQUEST FOR OTHER PDFS FOR MERGING
        nabilanavab=True; size=0
        while(nabilanavab):
            if len(MERGE[callbackQuery.message.chat.id]) >= 5:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "__Haddan tashqari yuk tufayli siz bir vaqtning o'zida faqat 5ta pdf faylni birlashtira olasiz__"
                )
                nabilanavab=False
                break
            askPDF=await bot.ask(
                text="__PDFlarni birlashtirish » Navbatdagi jami PDF fayllar: {}__\n\nBekor qilish uchun /bekorqilish ni bosing\nBirlashtirish uchun /birlashtirish ni bosing".format(
                    len(MERGE[callbackQuery.message.chat.id])
                ),
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=None
            )
            if askPDF.text == "/bekorqilish":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Jarayon bekor qilindi..` 😏"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                del MERGE[callbackQuery.message.chat.id]
                del MERGEsize[callbackQuery.message.chat.id]
                break
            if askPDF.text == "/birlashtirish":
                nabilanavab = False
                break
            # IS SEND MESSAGE A DOCUMENT
            if askPDF.document:
                file_id=askPDF.document.file_id
                file_size=askPDF.document.file_size
                # CHECKING FILE EXTENSION .pdf OR NOT
                if fileExt==".pdf":
                    # CHECKING TOTAL SIZE OF MERGED PDF
                    for _ in MERGEsize[callbackQuery.message.chat.id]:
                        size = int(_) + size
                    # CHECKS MAXIMUM FILE SIZE (IF ADDED) ELSE 1.8 GB LIMIT
                    if (MAX_FILE_SIZE and MAX_FILE_SIZE_IN_kiB <= int(size)) or int(size) >= 1800000000:
                        await bot.send_message(
                            callbackQuery.message.chat.id,
                            f"`Haddan tashqari ko'p yuk tufayli faqat %sMb PDFlarni qo'llab quvvatlaydi..`😐"%(MAX_FILE_SIZE if MAX_FILE_SIZE else "1.8Gb")
                        )
                        nabilanavab=False
                        break
                    # ADDING NEWLY ADDED PDF FILE ID & SIZE TO LIST
                    MERGE[callbackQuery.message.chat.id].append(file_id)
                    MERGEsize[callbackQuery.message.chat.id].append(file_size)
        # nabilanavab=True ONLY IF PROCESS CANCELLED
        if nabilanavab == True:
            PROCESS.remove(callbackQuery.message.chat.id)
        # GET /merge, REACHES MAX FILE SIZE OR MAX NO OF PDF
        if nabilanavab == False:
            # DISPLAY TOTAL PDFS FOR MERGING
            downloadMessage = await callbackQuery.message.reply_text(
                f"`Umumiy PDFlar : {len(MERGE[callbackQuery.message.chat.id])}`.. 💡",
                quote=True
            )
            sleep(.5)
            i=0
            # ITERATIONS THROUGH FILE ID'S AND DOWNLOAD
            for iD in MERGE[callbackQuery.message.chat.id]:
                await downloadMessage.edit(
                    f"__Pdf yuklab olish boshlandi :{i+1}__"
                )
                # START DOWNLOAD
                c_time=time.time()
                downloadLoc=await bot.download_media(
                    message=iD,
                    file_name=f"merge{callbackQuery.message.chat.id}/{i}.pdf",
                    progress=progress,
                    progress_args=(
                        MERGEsize[callbackQuery.message.chat.id][i],
                        downloadMessage,
                        c_time
                    )
                )
                # CHECKS IF DOWNLOAD COMPLETE/PROCESS CANCELLED
                if downloadLoc is None:
                    PROCESS.remove(callbackQuery.message.chat.id)
                    await callbackQuery.message.reply_text(
                        "`Birlashtirish jarayoni bekor qilindi.. 😏`", quote=True
                    )
                    shutil.rmtree(f"merge{callbackQuery.message.chat.id}")
                    return
                # CHECKS PDF CODEC, ENCRYPTION..
                checked = await checkPdf(
                    f"merge{callbackQuery.message.chat.id}/{i}.pdf",
                    callbackQuery
                )
                # REMOVE FILE FROM DIRECTORY IF FILE NOT ENCRYPTED OR CODECERROR
                if not(checked == "pass"):
                    os.remove(f"merge{callbackQuery.message.chat.id}/{i}.pdf")
                i += 1
            directory=f'merge{callbackQuery.message.chat.id}'
            pdfList=[os.path.join(directory, file) for file in os.listdir(directory)]
            # SORT DIRECTORY PATH BY ITS MODIFIED TIME
            pdfList.sort(key=os.path.getctime)
            numbPdf=len(pdfList)
            # MERGING STARTED
            await downloadMessage.edit(
                "__Birlashtirish boshlandi.. __ 🪄"
            )
            output_pdf=f"merge{callbackQuery.message.chat.id}/merge.pdf"
            #PyPDF 2
            merger=PdfFileMerger()
            for i in pdfList:
                merger.append(i)
            merger.write(output_pdf)
            # STARTED UPLOADING
            await downloadMessage.edit(
                "`Sizga yuborilmoqda..`🏋️"
            )
            await bot.send_chat_action(
                callbackQuery.message.chat.id, "upload_document"
            )
            # SEND DOCUMENT
            await bot.send_document(
                file_name=f"@azik_pdfbot .pdf", #{fileNm} via 
                chat_id=callbackQuery.message.chat.id,
                document=open(output_pdf, "rb"),
                thumb=PDF_THUMBNAIL, caption="__Birlashtirilgan pdf \n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊__"
            )
            await downloadMessage.delete()
            shutil.rmtree(f"merge{callbackQuery.message.chat.id}")
            PROCESS.remove(callbackQuery.message.chat.id)
    except Exception as e:
        try:
            print("plugins/dms/cllba/merge: ", e)
            shutil.rmtree(f"merge{callbackQuery.message.chat.id}")
            PROCESS.remove(callbackQuery.message.chat.id)
        except Exception:
            pass

#                                                                                  Tele
 
    
    #------------------->

pdfInfoMsg = """`Ushbu fayl bilan nima qilishni xohlaysiz.?`
Fayl Nomi: `{}`
Fayl Hajmi: `{}`
`Sahifalar soni: {}`✌️"""

encryptedMsg = """`Fayl Himoyalangan` 🔐
Fayl Nomi: `{}`
Fayl Hajmi: `{}`
`Sahifalar soni: {}`✌️"""

#--------------->
#--------> PDF META DATA
#------------------->

pdfInfo = filters.create(lambda _, __, query: query.data == "pdfInfo")
KpdfInfo = filters.create(lambda _, __, query: query.data.startswith("KpdfInfo"))

@bot.on_callback_query(pdfInfo)
async def _pdfInfo(bot, callbackQuery):
    try:
        # CHECKS PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        # CB MESSAGE DELETES IF USER DELETED PDF
        try:
            fileExist=callbackQuery.message.reply_to_message.document.file_id
        except Exception:
            await bot.delete_messages(
                chat_id=callbackQuery.message.chat.id,
                message_ids=callbackQuery.message.message_id
            )
            return
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # DOWNLOADING STARTED
        downloadMessage=await callbackQuery.edit_message_text(
            "`PDFingiz yuklab olinmoqda..`⏳",
        )
        pdf_path=f"{callbackQuery.message.message_id}/pdfInfo.pdf"
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        # DOWNLOAD PROGRESS
        c_time=time.time()
        downloadLoc=await bot.download_media(
            message=file_id,
            file_name=pdf_path,
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        # CHECKS IS DOWNLOADING COMPLETED OR PROCESS CANCELED
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        # OPEN FILE WITH FITZ
        with fitz.open(pdf_path) as pdf:
            isPdf=pdf.is_pdf
            metaData=pdf.metadata
            isEncrypted=pdf.is_encrypted
            number_of_pages=pdf.pageCount
            # CHECKS IF FILE ENCRYPTED
            if isPdf and isEncrypted:
                pdfMetaData=f"\nFayl Himoyalangan 🔐\n"
            if isPdf and not(isEncrypted):
                pdfMetaData="\n"
            # ADD META DATA TO pdfMetaData STRING
            if metaData != None:
                for i in metaData:
                    if metaData[i] != "":
                        pdfMetaData += f"`{i}: {metaData[i]}`\n"
            fileName = callbackQuery.message.reply_to_message.document.file_name
            fileSize = callbackQuery.message.reply_to_message.document.file_size
            if isPdf and not(isEncrypted):
                editedPdfReplyCb=InlineKeyboardMarkup(
                    [
                      [
                           InlineKeyboardButton("Ma'lumot ⭐", callback_data=f"KpdfInfo|{number_of_pages}"),
                           InlineKeyboardButton("Ko'rib chiqish 🗳️", callback_data="Kpreview")
                       ],[
                           InlineKeyboardButton("Rasmga o'tkazish 🖼️", callback_data=f"KtoImage|{number_of_pages}"),
                           InlineKeyboardButton("Matnga o'tkazish ✏️", callback_data=f"KtoText|{number_of_pages}")
                       ],[
                           InlineKeyboardButton("Himoyalash 🔐", callback_data=f"Kencrypt|{number_of_pages}"),
                           InlineKeyboardButton("Himoyadan ochish 🔓", callback_data=f"notEncrypted")
                       ],[
                           InlineKeyboardButton("Siqish 🗜️", callback_data=f"Kcompress"),
                           InlineKeyboardButton("Aylantirish 🤸", callback_data=f"Krotate|{number_of_pages}")
                       ],[
                           InlineKeyboardButton("Kesish ✂️", callback_data=f"Ksplit|{number_of_pages}"),
                           InlineKeyboardButton("Birlashtirish 🧬",callback_data="merge")
                       ],[
                           InlineKeyboardButton("Pechat qo'yish ™️",callback_data=f"Kstamp|{number_of_pages}"),
                           InlineKeyboardButton("Qayta nomlash ✏️",callback_data="rename")
                       ],[
                            InlineKeyboardButton("Yopish 🚫", callback_data="closeALL")
                      ]
                    ]
                )
                await callbackQuery.edit_message_text(
                    pdfInfoMsg.format(
                        fileName, await gSF(fileSize), number_of_pages
                    ) + pdfMetaData,
                    reply_markup=editedPdfReplyCb
                )
            elif isPdf and isEncrypted:
                await callbackQuery.edit_message_text(
                    encryptedMsg.format(
                        fileName, await gSF(fileSize), number_of_pages
                    ) + pdfMetaData,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("Himoyadan ochish 🔓", callback_data="decrypt")
                            ],[
                                InlineKeyboardButton("Yopish 🚫", callback_data="closeALL")
                            ]
                        ]
                    )
                )
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
    # EXCEPTION DURING FILE OPENING
    except Exception as e:
        try:
            await callbackQuery.edit_message_text(
                f"Nimadir xato ketdi.. 🐉\n\nXATOLIK: {e}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Faylda xatolik ❌", callback_data = f"error")
                        ],[
                            InlineKeyboardButton("Yopish 🚫", callback_data="closeALL")
                        ]
                    ]
                )
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

@bot.on_callback_query(KpdfInfo)
async def _KpdfInfo(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await bot.answer_callback_query(
            callbackQuery.id,
            text = f"Umumiy {number_of_pages}ta sahifalar 😉",
            show_alert = True,
            cache_time = 0
        )
    except Exception:
        pass

#                                                                                              Telegra

#------------------->

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

media = {}

#--------------->
#--------> PDF TO IMAGES
#------------------->

preview = filters.create(lambda _, __, query: query.data in ["Kpreview", "preview"])

# Extract pgNo (with unknown pdf page number)
@bot.on_callback_query(preview)
async def _preview(bot, callbackQuery):
    try:
        # CALLBACK DATA
        data=callbackQuery.data
        # CHECK USER PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        await callbackQuery.answer(
            "Faqat boshlang'ich, o'rta va yakuniy sahifalarni yuboradi (agar mavjud bo'lsa)",
            cache_time=10
        )
        # ADD USER TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # DOWNLOAD MESSAGE
        downloadMessage = await callbackQuery.message.reply_text(
            "`PDFingiz yuklab olinmoqda..` ⏳", quote=True
        )
        file_id = callbackQuery.message.reply_to_message.document.file_id
        fileSize = callbackQuery.message.reply_to_message.document.file_size
        # DOWNLOAD PROGRESS
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
        # CHECK DOWNLOAD COMPLETED/CANCELLED
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        # CHECK PDF CODEC, ENCRYPTION..
        if data!="Kpreview":
            checked=await checkPdf(
                f'{callbackQuery.message.message_id}/pdf.pdf', callbackQuery
            )
            if not(checked=="pass"):
                await downloadMessage.delete()
                return
        # OPEN PDF WITH FITZ
        doc = fitz.open(f'{callbackQuery.message.message_id}/pdf.pdf')
        number_of_pages = doc.pageCount
        if number_of_pages == 1:
            totalPgList=[1]
            caption="PDF Rasmlarini oldindan ko'rish:\n__Birinchi sahifa: 1__"
        elif number_of_pages == 2:
            totalPgList = [1, 2]
            caption="PDF Rasmlarini oldindan ko'rish:\n__Birinchi sahifa: 1__\n__Oxirgi sahifa: 2__\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
        elif number_of_pages == 3:
            totalPgList = [1, 2, 3]
            caption="PDF Rasmlarini oldindan ko'rish:\n__Birinchi sahifa: 1__\n__O'rtadagi sahifa: 2__\n__Oxirgi sahifa: 3__\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
        else:
            totalPgList = [1, number_of_pages//2, number_of_pages]
            caption=f"PDF Rasmlarini oldindan ko'rish:\n__Birinchi sahifa: 1__\n__O'rtadagi sahifa: {number_of_pages//2}____\nOxirgi sahifa: {number_of_pages}__\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
        await downloadMessage.edit(
            f"`Umumiy sahifalar: {len(totalPgList)}ta..⏳`"
        )
        zoom=2
        mat = fitz.Matrix(zoom, zoom)
        os.mkdir(f'{callbackQuery.message.message_id}/pgs')
        for pageNo in totalPgList:
            page=doc.loadPage(int(pageNo)-1)
            pix=page.getPixmap(matrix = mat)
            # SAVING PREVIEW IMAGE
            with open(
                f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg','wb'
            ):
                pix.writePNG(f'{callbackQuery.message.message_id}/pgs/{pageNo}.jpg')
        try:
            await downloadMessage.edit(
                f"`Albom tayyorlanmoqda..` 🤹"
            )
        except Exception:
            pass
        directory=f'{callbackQuery.message.message_id}/pgs'
        # RELATIVE PATH TO ABS. PATH
        imag=[os.path.join(directory, file) for file in os.listdir(directory)]
        # SORT FILES BY MODIFIED TIME
        imag.sort(key=os.path.getctime)
        # LIST TO SAVE GROUP IMAGE OBJ.
        media[callbackQuery.message.chat.id] = []
        for file in imag:
            # COMPRESSION QUALITY
            qualityRate=95
            # JUST AN INFINITE LOOP
            for i in range(200):
                # print("size: ",file, " ",os.path.getsize(file)) LOG MESSAGE
                # FILES WITH 10MB+ SIZE SHOWS AN ERROR FROM TELEGRAM 
                # SO COMPRESS UNTIL IT COMES LESS THAN 10MB.. :(
                if os.path.getsize(file) >= 1000000:
                    picture=Image.open(file)
                    picture.save(
                        file, "JPEG",
                        optimize=True,
                        quality=qualityRate
                    )
                    qualityRate-=5
                # ADDING TO GROUP MEDIA IF POSSIBLE
                else:
                    if len(media[callbackQuery.message.chat.id]) == 1:
                        media[
                            callbackQuery.message.chat.id
                        ].append(
                            InputMediaPhoto(media=file, caption=caption)
                        )
                    else:
                        media[
                            callbackQuery.message.chat.id
                        ].append(
                            InputMediaPhoto(media=file)
                        )
                    break
        await downloadMessage.edit(
            f"`Sahifalarni oldindan ko'rish: rasmlar sizga yuborilmoqda.. 🐬`"
        )
        await callbackQuery.message.reply_chat_action("upload_photo")
        await bot.send_media_group(
            chat_id=callbackQuery.message.chat.id,
            reply_to_message_id=callbackQuery.message.reply_to_message.message_id,
            media=media[callbackQuery.message.chat.id]
        )
        await downloadMessage.delete()
        doc.close
        del media[callbackQuery.message.chat.id]
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f'{callbackQuery.message.message_id}')
    
    except Exception as e:
        try:
            PROCESS.remove(callbackQuery.message.chat.id)
            await downloadMessage.edit(f"Nimadir xato ketdi\n\nXATOLIK: {e}")
            shutil.rmtree(f'{callbackQuery.message.message_id}')
        except Exception:
            pass

#                                                                                  Telegram
    
#------------------->

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> RENAME PDF
#------------------->

rename = filters.create(lambda _, __, query: query.data.startswith("rename"))

@bot.on_callback_query(rename)
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
            text="__PDFni qayta nomlash »\nEndi PDFni yangi yonimi kiriting:__\n\nBekor qilish uchun /bekorqilish ni bosing",
            filters=filters.text,
            reply_markup=ForceReply(True)
        )
        # /exit CANCELS
        if newName.text == "/bekorqilish":
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

#                                                                                  Telegra

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
@bot.on_callback_query(rotate)
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
@bot.on_callback_query(Krotate)
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

@bot.on_callback_query(rot)
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

@bot.on_callback_query(rot360)
async def _rot360(bot, callbackQuery):
    try:
        await callbackQuery.answer(
            "Sizda katta muammo bor..🙂"
        )
    except Exception:
        pass

#                                                                                  Tel

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
@bot.on_callback_query(split)
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
@bot.on_callback_query(Ksplit)
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
@bot.on_callback_query(splitR)
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
                text="PDFni kesish. Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /bekorqilish ni bosing.__",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            # IF /exit PROCESS CANCEL
            if needPages.text == "/bekorqilish":
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
@bot.on_callback_query(splitS)
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
                text="PDFni kesish. Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini  bilan kiriting.\nMasalan 3 yoki 7\n\nBekor qilish uchun /bekorqilish ni bosing.",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            singlePages = list(needPages.text.replace(',',':').split(':'))
            if needPages.text == "/bekorqilish":
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
@bot.on_callback_query(KsplitR)
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
                text=f"PDFni kesish » Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4\nUmumiy sahifalar: __`{number_of_pages}`ta\n\nBekor qilish uchun /bekorqilish ni bosing.__",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            if needPages.text == "/bekorqilish":
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
@bot.on_callback_query(KsplitS)
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
                text=f"PDFni kesish » Sahifalar soni bilan\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4\nUmumiy sahifalar: __`{number_of_pages}`ta\n\nBekor qilish uchun /bekorqilish ni bosing.__",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=filters.text, reply_markup=ForceReply(True)
            )
            singlePages = list(needPages.text.replace(',',':').split(':'))
            if needPages.text == "/bekorqilish":
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

#                                                                                                                                    Telegram: @n


#------------------->

"""
____VARIABLES____
stmp = Stamp CB
STAMP ANNOTATIONS: [pymuPdf/fituz](annot)
0 : STAMP_Tasdiqlangan
1 : STAMP_AsIs
2 : STAMP_Maxfiy
3 : STAMP_Idoraviy
4 : STAMP_Experimental
5 : STAMP_Expired
6 : STAMP_Oxirgi
7 : STAMP_ForComment
8 : STAMP_ForPublicRelease
9 : STAMP_Tasdiqlanmagan
10: STAMP_NotForPublicRelease
11: STAMP_Sold
12: STAMP_TopSecret
13: STAMP_Draft
COLOR: [RGB]
r = red, g = green, b = blue
"""


PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> PDF COMPRESSION
#------------------->

# pdfMessage to stamp --> "stamp"(stampselect)
stamp = filters.create(lambda _, __, query: query.data == "stamp")
Kstamp = filters.create(lambda _, __, query: query.data.startswith("Kstamp"))

# stampSelect to color --> "stmp"(stampcolor)
stmp = filters.create(lambda _, __, query: query.data.startswith("stmp"))
Kstmp = filters.create(lambda _, __, query: query.data.startswith("Kstmp"))

# color --> stamping process
colors = ["color", "Kcolor"]
color = filters.create(lambda _, __, query: query.data.startswith(tuple(colors)))

# stamp selet message(with unknown pdf page number)
@bot.on_callback_query(stamp)
async def _stamp(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__Pechat qo'yish » Pechat uchun yozuvni tanlang:         \nUmumiy sahifalar: Noma'lum__ 😐\n\nESLATMA!!! Faqat pastdagi so'zlarni qo'ya olasiz!",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Not For Public Release 🤧", callback_data="stmp|10")
                    ],[
                        InlineKeyboardButton("For Public Release 🥱", callback_data="stmp|8")
                    ],[
                        InlineKeyboardButton("Confidential 🤫", callback_data="stmp|2"),
                        InlineKeyboardButton("Departmental 🤝", callback_data="stmp|3")
                    ],[
                        InlineKeyboardButton("Experimental 🔬", callback_data="stmp|4"),
                        InlineKeyboardButton("Expired 🐀",callback_data="stmp|5")
                    ],[
                        InlineKeyboardButton("Final 🔧", callback_data="stmp|6"),
                        InlineKeyboardButton("For Comment 🗯️",callback_data="stmp|7")
                    ],[
                        InlineKeyboardButton("Tasdiqlanmagan 😒",callback_data="stmp|9"),
                        InlineKeyboardButton("Tasdiqlangan 🥳", callback_data="stmp|0")
                    ],[
                        InlineKeyboardButton("Sold ✊",callback_data="stmp|11"),
                        InlineKeyboardButton("Top Secret 😷", callback_data="stmp|12"),
                    ],[
                        InlineKeyboardButton("Draft 👀",callback_data="stmp|13"),
                        InlineKeyboardButton("AsIs 🤏", callback_data="stmp|1")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data="BTPM")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Stamp select message (with known pdf page number)
@bot.on_callback_query(Kstamp)
async def _Kstamp(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Pechat qo'yish » Pechat uchun yozuvni tanlang:         \nUmumiy sahifalar: {number_of_pages}ta__ \n\nESLATMA!!! Faqat pastdagi so'zlarni qo'ya olasiz!",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Not For Public Release 🤧", callback_data=f"Kstmp|{number_of_pages}|10")
                    ],[
                        InlineKeyboardButton("For Public Release 🥱", callback_data=f"Kstmp|{number_of_pages}|8")
                    ],[
                        InlineKeyboardButton("Confidential 🤫", callback_data=f"Kstmp|{number_of_pages}|2"),
                        InlineKeyboardButton("Departmental 🤝", callback_data=f"Kstmp|{number_of_pages}|3")
                    ],[
                        InlineKeyboardButton("Experimental 🔬", callback_data=f"Kstmp|{number_of_pages}|4"),
                        InlineKeyboardButton("Expired 🐀",callback_data=f"Kstmp|{number_of_pages}|5")
                    ],[
                        InlineKeyboardButton("Final 🔧", callback_data=f"Kstmp|{number_of_pages}|6"),
                        InlineKeyboardButton("For Comment 🗯️",callback_data=f"Kstmp|{number_of_pages}|7")
                    ],[
                        InlineKeyboardButton("Not Approved 😒",callback_data=f"Kstmp|{number_of_pages}|9"),
                        InlineKeyboardButton("Approved 🥳", callback_data=f"Kstmp|{number_of_pages}|0")
                    ],[
                        InlineKeyboardButton("Sold ✊",callback_data=f"Kstmp|{number_of_pages}|11"),
                        InlineKeyboardButton("Top Secret 😷", callback_data=f"Kstmp|{number_of_pages}|12"),
                    ],[
                        InlineKeyboardButton("Draft 👀",callback_data=f"Kstmp|{number_of_pages}|13"),
                        InlineKeyboardButton("AsIs 🤏", callback_data=f"Kstmp|{number_of_pages}|1")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"KBTPM|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Stamp color message (with unknown pdf page number)
@bot.on_callback_query(stmp)
async def _stmp(bot, callbackQuery):
    try:
        _, annot = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            "__Pechat qo'yish » Pechat uchun rangni tanlang:         \nUmumiy sahifalar: Noma'lum__ 😐",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Qizil ❤️", callback_data=f"color|{annot}|r"),
                        InlineKeyboardButton("Ko'k 💙", callback_data=f"color|{annot}|b")
                    ],[
                        InlineKeyboardButton("Yashil 💚", callback_data=f"color|{annot}|g"),
                        InlineKeyboardButton("Sariq 💛", callback_data=f"color|{annot}|c1")
                    ],[
                        InlineKeyboardButton("Pushti 💜", callback_data=f"color|{annot}|c2"),
                        InlineKeyboardButton("Havorang 💚", callback_data=f"color|{annot}|c3")
                    ],[
                        InlineKeyboardButton("Oq 🤍", callback_data=f"color|{annot}|c4"),
                        InlineKeyboardButton("Qora 🖤", callback_data=f"color|{annot}|c5")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"stamp")
                    ]
                ]
            )
        )
    except Exception:
        pass

# Stamp color message (with known pdf page number)
@bot.on_callback_query(Kstmp)
async def _Kstmp(bot, callbackQuery):
    try:
        _, number_of_pages, annot = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Pechat qoyish » Pechat uchun rangni tanlang:         \nUmumiy sahifalar: {number_of_pages}ta__",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Qizil ❤️", callback_data=f"Kcolor|{annot}|r"),
                        InlineKeyboardButton("Ko'k 💙", callback_data=f"Kcolor|{annot}|b")
                    ],[
                        InlineKeyboardButton("Yashil 💚", callback_data=f"Kcolor|{annot}|g"),
                        InlineKeyboardButton("Sariq 💛", callback_data=f"Kcolor|{annot}|c1")
                    ],[
                        InlineKeyboardButton("Pushti 💜", callback_data=f"Kcolor|{annot}|c2"),
                        InlineKeyboardButton("Havorang 💚", callback_data=f"Kcolor|{annot}|c3")
                    ],[
                        InlineKeyboardButton("Oq 🤍", callback_data=f"Kcolor|{annot}|c4"),
                        InlineKeyboardButton("Qora 🖤", callback_data=f"Kcolor|{annot}|c5")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"Kstamp|{number_of_pages}")
                    ]
                ]
            )
        )
    except Exception:
        pass

@bot.on_callback_query(color)
async def _color(bot, callbackQuery):
    try:
        # CHECK IF USER IN PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        
        _, annot, colr = callbackQuery.data.split("|")
        # ADD USER TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        data = callbackQuery.data
        # STARTED DOWNLOADING
        downloadMessage=await callbackQuery.message.reply_text(
            "`PDFingiz yuklab olinmoqda..` ⏳", quote=True
        )
        input_file=f"{callbackQuery.message.message_id}/pdf.pdf"
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        fileNm = callbackQuery.message.reply_to_message.document.file_name
        fileNm, fileExt = os.path.splitext(fileNm)        # seperates name & extension
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
        
        # COLOR CODE
        if colr == "r":
            color = (1, 0, 0)
        elif colr == "b":
            color = (0, 0, 1)
        elif colr == "g":
            color = (0, 1, 0)
        elif colr == "c1":
            color = (1, 1, 0)
        elif colr == "c2":
            color = (1, 0, 1)
        elif colr == "c3":
            color = (0, 1, 1)
        elif colr == "c4":
            color = (1, 1, 1)
        elif colr == "c5":
            color = (0, 0, 0)
        
        # CHECK DOWNLOAD COMPLETED OR CANCELED
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        #STAMPING STARTED
        await downloadMessage.edit(
            "`Pechat qo'yish boshlandi..` 💠"
        )
        if data.startswith("color"):
            checked = await checkPdf(input_file, callbackQuery)
            if not(checked == "pass"):
                await downloadMessage.delete()
                return
        output_file=f"{callbackQuery.message.message_id}/stamped.pdf"
        r = fitz.Rect(72, 72, 440, 200)
        with fitz.open(input_file) as doc:
            page=doc.load_page(0)
            annot=page.add_stamp_annot(r, stamp=int(f"{annot}"))
            annot.set_colors(stroke=color)
            annot.set_opacity(0.5)
            annot.update()
            doc.save(output_file)
        # STARTED UPLOADING
        await bot.send_chat_action(
            callbackQuery.message.chat.id,
            "upload_document"
        )
        await downloadMessage.edit(
            "`Sizga yuborilmoqda..` 🏋️"
        )
        # SEND DOCUMENT
        await callbackQuery.message.reply_document(
            file_name=f"@azik_pdfbot.pdf", #{fileNm} via 
            document=open(output_file, "rb"),
            thumb=PDF_THUMBNAIL, quote=True,
            caption="Pechatlangan pdf\n\n@azik_pdfbot ishingizni yengillatgan bo'lsa biz bundan xursandmiz😊"
        )
        # DELETE DOWNLOAD MESSAGE
        await downloadMessage.delete()
        PROCESS.remove(callbackQuery.message.chat.id)
        shutil.rmtree(f"{callbackQuery.message.message_id}")
    
    except Exception as e:
        try:
            print("Pechatlangan: ",e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
            await downloadMessage.delete()
        except Exception:
            pass

#                                                                                  Tele

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
@bot.on_callback_query(toText)
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
@bot.on_callback_query(KtoText)
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
@bot.on_callback_query(T)
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
@bot.on_callback_query(M)
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
@bot.on_callback_query(H)
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
@bot.on_callback_query(J)
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

#                                                                                  Tele

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
@bot.on_callback_query(EXTRACT)
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
                    text="__PDFni Rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /bekorqilish ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                # EXIT PROCESS
                if needPages.text=="/bekorqilish":
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
                    text="__PDFni rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /bekorqilish ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                # SPLIT PAGE NUMBERS (,)
                singlePages=list(needPages.text.replace(',',':').split(':'))
                # PROCESS CANCEL
                if needPages.text=="/bekorqilish":
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
@bot.on_callback_query(KEXTRACT)
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
                    text="__PDFni rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /bekorqilish ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                if needPages.text=="/bekorqilish":
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
                    text="__PDFni Rasmga o'tkazish.\nEndi kesadigan sahifalaringiz sonini kiriting (boshlang'ich sahifa raqami:oxirgi sahifa raqami)\nMasalan: 2:8 yoki 1:4 \n\nBekor qilish uchun /bekorqilish ni bosing.__",
                    chat_id=callbackQuery.message.chat.id,
                    reply_to_message_id=callbackQuery.message.message_id,
                    filters=filters.text,
                    reply_markup=ForceReply(True)
                )
                singlePages=list(needPages.text.replace(',',':').split(':'))
                if needPages.text=="/bekorqilish":
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

#                                                                                  Teleg

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


@bot.on_message(filters.private & ~filters.edited & filters.command(["cancel"]))
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

#                                                                                  Tel

#------------------->

@bot.on_message(filters.command(["tozalash"]))
async def _cancelI2P(bot, message):
    try:
        await message.reply_chat_action("typing")
        del PDF[message.chat.id]
        await message.reply_text("`Navbat muvaffaqiyatli oʻchirildi..`🤧", quote=True)
        shutil.rmtree(f"{message.chat.id}")
    except Exception:
        await message.reply_text("`Navbat topilmadi..`😲", quote=True)

#                                                                                  Te

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

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"

pdfReplyMsg = """`Ushbu faylni nima qilishni xohlaysiz.?`
Fayl Nomi : `{}`
Fayl Hajmi : `{}`"""

bigFileUnSupport = """Haddan tashqari yuk tufayli Administrator botga pdf yuklash limiti {}mb deb belgiladi 🙇
`Iltimos menga {}mbdan kichkina pdflar yuboring` 🙃"""

imageAdded = """`Sizning Pdf faylingizga {}ta fayl qo'shildi..`🤓
Pdf yaratish uchun /generate komandasini yuboring🤞"""

errorEditMsg = """Nimadir xato ketdi..😐
XATO: `{}`
Qo'llab quvvatlash guruhi @azik_projects_support """

feedbackMsg = "[Men haqimda taklif va shikoyatlaringizni yozishingiz mumkin 📋](https://t.me/azik_projects_support)"

forceSubMsg = """To'xtang [{}](tg://user?id={})..!!
Katta yuzaga keladigan yuk tufayli bu botdan faqat kanal a'zolari foydalanishi mumkin 🚶
Bu mendan foydalanish uchun quyida ko'rsatilgan kanalga qo'shilishingiz kerakligini bildiradi!
qo'shilgandan keyin "Qayta urinish♻️" tugmasini bosing.. 😅"""

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
#--------> PDF REPLY BUTTON
#------------------->

pdfReply=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Ma'lumot ⭐", callback_data="pdfInfo"),
                InlineKeyboardButton("Ko'rib chiqish 🗳️", callback_data="preview")
            ],[
                InlineKeyboardButton("Rasmga o'tkazish 🖼️", callback_data="toImage"),
                InlineKeyboardButton("Matnga o'tkazish ✏️", callback_data="toText")
            ],[
                InlineKeyboardButton("Himoyalash 🔐", callback_data="encrypt"),
                InlineKeyboardButton("Himoyadan ochish 🔓",callback_data="decrypt")
            ],[
                InlineKeyboardButton("Siqish 🗜️", callback_data="compress"),
                InlineKeyboardButton("Aylantirish 🤸", callback_data="rotate")
            ],[
                InlineKeyboardButton("Kesish ✂️", callback_data="split"),
                InlineKeyboardButton("Birlashtirish 🧬", callback_data="merge")
            ],[
                InlineKeyboardButton("Pechat qo'yish ™️", callback_data="stamp"),
                InlineKeyboardButton("Qayta nomlash ✏️", callback_data="rename")
            ],[
                InlineKeyboardButton("Yopish 🚫", callback_data="closeALL")
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

@bot.on_message(filters.private & filters.document & ~filters.edited)
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
                                InlineKeyboardButton("🌟 Proyektlar kanaliga ulanish 🌟", url=invite_link.invite_link)
                            ],[
                                InlineKeyboardButton("Qayta urinish ♻️", callback_data="refresh")
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
                                "💎 Proyektlar kanali 💎",
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
                    "`Rasmingiz yuklab olinmoqda..⏳`", quote=True
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
                    "Qayta ishlanmoqda..🚶", quote=True
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
                    "`Faylingiz yuklab olinmqoda..⏳`", quote=True
                )
                await message.download(
                    f"{message.message_id}/{isPdfOrImg}"
                )
                await pdfMsgId.edit(
                    "`PDF yaratilmoqda..`💛"
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
                    "`Sizga pdf yuborilmoqda..`🏋️"
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
                    "`Adminstrator bilan bog'laning 😒`",
                    quote=True
                )
                return
            else:
                try:
                    pdfMsgId = await message.reply_text(
                        "`Faylingiz yuklab olinmoqda..⏳`", quote=True
                    )
                    await message.download(
                        f"{message.message_id}/{isPdfOrImg}"
                    )
                    await pdfMsgId.edit(
                        "`PDF yaratilmoqda..`💛"
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
                    "`Qo'llab-quvvatlanmaydigan fayl..🙄`", quote=True
                )
            except Exception:
                pass
    
    except Exception as e:
        print("plugins/dm/document : ", e)

#                                                                                  Te

#------------------->

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"

feedbackMsg = "[Taklif va shikoyat yozishingiz mumkin 📋](https://t.me/azik_projects_support)"

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
#--------> REPLY TO /feedback
#------------------->

@bot.on_message(filters.private & filters.command(["taklif"]) & ~filters.edited)
async def feedback(bot, message):
    try:
        await message.reply_chat_action("typing")
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse, reply_markup=button, quote=True
            )
            return
        await message.reply_text(
            feedbackMsg, disable_web_page_preview = True
        )
    except Exception:
        pass

#                                                                                  Telegr

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
#--------> GET USER ID (/id)
#------------------->

@bot.on_message(filters.private & ~filters.edited & filters.command(["id"]))
async def userId(bot, message):
    try:
        await message.reply_chat_action("typing")
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(UCantUse, reply_markup=button)
            return
        await message.reply_text(
            f'Sizning IDyingiz: `{message.chat.id}`', quote=True
        )
    except Exception:
        pass

#                                                                                  Tel
#------------------->

#------------------->

UCantUse = "Ba'zi sabablarga ko'ra siz ushbu botdan foydalana olmaysiz 🛑"

imageAdded = """`{} ta sahifa sizning pdfingizga qo'shildi..`🤓
PDF yaratish uchun /pdfyaratish komandasini yuboring 🤞"""

forceSubMsg = """To'xtang [{}](tg://user?id={})..!!
Katta yuzaga keladigan yuk tufayli bu botdan faqat kanal a'zolari foydalanishi mumkin 🚶
Bu mendan foydalanish uchun quyida ko'rsatilgan kanalga qo'shilishingiz kerakligini bildiradi!
qo'shilgandan keyin "Qayta urinish♻️" tugmasini bosing.. 😅"""

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
#--------> REPLY TO IMAGES
#------------------->

@bot.on_message(filters.private & ~filters.edited & filters.photo)
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
                                    "🌟 Proyektlar kanali 🌟",
                                    url=invite_link.invite_link
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Qayta urinish ♻️",
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
            "`Rasmingiz yuklab olinmoqda..⏳`", quote=True
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


#                                                                                  Te

#------------------->

PDF_THUMBNAIL=Config.PDF_THUMBNAIL
BANNED_USERS=Config.BANNED_USERS
ADMIN_ONLY=Config.ADMIN_ONLY
ADMINS=Config.ADMINS

#--------------->
#--------> LOCAL VARIABLES
#------------------->

TXT = {}

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
#--------> REPLY TO /txt2pdf
#------------------->

@bot.on_message(filters.private & filters.command(["matnnipdfqilish"]) & ~filters.edited)
async def feedback(bot, message):
    try:
        await message.reply_chat_action("typing")
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse, reply_markup=button, quote=True
            )
            return
        await message.reply_text(
            text="__Endi, Shriftni tanlang »__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Times", callback_data="font|t"),
                        InlineKeyboardButton("Courier", callback_data="font|c")
                    ],[
                        InlineKeyboardButton("Helvetica (Default)", callback_data="font|h")
                    ],[
                        InlineKeyboardButton("Symbol", callback_data="font|s"),
                        InlineKeyboardButton("Zapfdingbats", callback_data="font|z")
                    ],[
                        InlineKeyboardButton("🚫 Yopish ", callback_data="closeme")
                    ]
                ]
            )
        )
        await message.delete()
    except Exception as e:
        print(e)

txt2pdf = filters.create(lambda _, __, query: query.data.startswith("font"))

@bot.on_callback_query(txt2pdf)
async def _txt2pdf(bot, callbackQuery):
    try:
        _, font = callbackQuery.data.split("|")
        await callbackQuery.message.edit(
            text=f"Matnni Pdfga aylantirish. \nEndi qog'oz ko'rinishi belgilang »",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Portret", callback_data=f"pgSize|{font}|p")
                    ],[
                        InlineKeyboardButton("Yonbosh", callback_data=f"pgSize|{font}|l")
                    ],[
                        InlineKeyboardButton("Orqaga", callback_data=f"txt2pdfBack")
                    ]
                ]
            )
        )
    except Exception as e:
        print(e)

txt2pdfBack = filters.create(lambda _, __, query: query.data == "txt2pdfBack")

@bot.on_callback_query(txt2pdfBack)
async def _txt2pdfBack(bot, callbackQuery):
    try:
        await callbackQuery.message.edit(
            text="__Endi, Shrift uslubini tanlang__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Times", callback_data="font|t"),
                        InlineKeyboardButton("Courier", callback_data="font|c")
                    ],[
                        InlineKeyboardButton("Helvetica", callback_data="font|h")
                    ],[
                        InlineKeyboardButton("Symbol", callback_data="font|s"),
                        InlineKeyboardButton("Zapfdingbats", callback_data="font|z")
                    ],[
                        InlineKeyboardButton("🚫 Yopish ", callback_data="closeme")
                    ]
                ]
            ),
            disable_web_page_preview=True
        )
    except Exception as e:
        print(e)

pgSize = filters.create(lambda _, __, query: query.data.startswith("pgSize"))

@bot.on_callback_query(pgSize)
async def _pgSize(bot, callbackQuery):
    try:
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Ish davom etmoqda.. 🙇"
            )
            return
        bla, _, __ = callbackQuery.data.split("|")
        PROCESS.append(callbackQuery.message.chat.id)
        TXT[callbackQuery.message.chat.id] = []
        nabilanavab=True
        while(nabilanavab):
            # 1st value will be pdf title
            askPDF = await bot.ask(
                text="__Matnni Pdfga aylantirish.\nEndi PDFingizna nom yuboring.__\n\nBekor qilish uchun /bekorqilish ni bosing. \nO'tkazib yuborish /otkazibyuborish ni bosing. ",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=None
            )
            if askPDF.text == "/bekorqilish":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Jarayon bekor qilindi..` 😏"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                del TXT[callbackQuery.message.chat.id]
                break
            elif askPDF.text == "/otkazibyuborish":
                TXT[callbackQuery.message.chat.id].append(None)
                nabilanavab=False
            elif askPDF.text:
                TXT[callbackQuery.message.chat.id].append(f"{askPDF.text}")
                nabilanavab=False
        # nabilanavab=True ONLY IF PROCESS CANCELLED
        if nabilanavab == True:
            PROCESS.remove(callbackQuery.message.chat.id)
            TXT.remove(callbackQuery.message.chat.id)
            return
        nabilanavab=True
        while(nabilanavab):
            # other value will be pdf para
            askPDF = await bot.ask(
                text=f"__Matnni Pdfga aylantirish. \nEndi {len(TXT[callbackQuery.message.chat.id])-1}inchi qatorga qanday matn yozmoqchi bo'lmoqchi bo'lsangiz yozing__"
                      "\n\nPdfni yaratish uchun /yaratish ni bosing. \nBekor qilish uchun /bekorqilish ni bosing",
                chat_id=callbackQuery.message.chat.id,
                reply_to_message_id=callbackQuery.message.message_id,
                filters=None
            )
            if askPDF.text == "/bekorqilish":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`Jarayon bekor qilindi..` 😏"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                del TXT[callbackQuery.message.chat.id]
                break
            elif askPDF.text == "/yaratish":
                if TXT[callbackQuery.message.chat.id][0]==None and len(TXT[callbackQuery.message.chat.id])==1:
                    await bot.send_message(
                        callbackQuery.message.chat.id,
                        "Yaratishga hech nima yo'q.. 😏"
                    )
                else:
                    processMessage = await callbackQuery.message.reply_text(
                        "Matnni Pdfga aylantirish boshlandi..🎉", quote=True
                    )
                    nabilanavab=False
            elif askPDF.text:
                TXT[callbackQuery.message.chat.id].append(f"{askPDF.text}")
        # nabilanavab=True ONLY IF PROCESS CANCELLED
        if nabilanavab == True:
            PROCESS.remove(callbackQuery.message.chat.id)
            TXT.remove(callbackQuery.message.chat.id)
            return
        
        # Started Creating PDF
        if _ == "t":
            font="Times"
        elif _ == "c":
            font="Courier"
        elif _ == "h":
            font="Helvetica"
        elif _ == "s":
            font="Symbol"
        elif _ == "z":
            font="ZapfDingbats"
        
        pdf = FPDF()
        pdf.add_page(orientation=__)
        pdf.set_font(font, "B", size=20)
        if TXT[callbackQuery.message.chat.id][0] != None:
            pdf.cell(200, 20, txt=TXT[callbackQuery.message.chat.id][0], ln=1, align="C")
        pdf.set_font(font, size=15)
        for _ in TXT[callbackQuery.message.chat.id][1:]:
            pdf.multi_cell(200, 10, txt=_, border=0, align="L")
        pdf.output(f"{callbackQuery.message.message_id}.pdf")
        await callbackQuery.message.reply_chat_action("upload_document")
        await processMessage.edit(
            "`Pdfingiz sizga yuborilmoqda..` 🏋️"
        )
        await callbackQuery.message.reply_document(
            file_name="Matndan PDF yaratilgan via @azik_pdfbot.pdf", quote=True,
            document=open(f"{callbackQuery.message.message_id}.pdf", "rb"),
            thumb=PDF_THUMBNAIL
        )
        await processMessage.delete()
        PROCESS.remove(callbackQuery.message.chat.id)
        os.remove(f"{callbackQuery.message.message_id}")
        TXT.remove(callbackQuery.message.chat.id)
    except Exception as e:
        try:
            PROCESS.remove(callbackQuery.message.chat.id)
            await processMessage.edit(f"`XATO`: __{e}__")
            os.remove(f"{callbackQuery.message.message_id}.pdf")
            TXT.remove(callbackQuery.message.chat.id)
        except Exception:
            pass

#                                                                                  Tel


@bot.on_message(filters.command(["xabarid"]))
async def _cancelI2P(bot, message):
    try:
        await message.reply_chat_action("typing")
        await message.reply_text(f"Xabar IDsi: `{message.message_id}` 🎭", quote=True)
    except Exception:
        pass

#                                                                                  Telegr


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
            f"`Tushunarli!` Matnni Pdfga aylantirmoqchi bo'lsangiz /matnnipdfqilish ni bosing.", quote=True
        )
    except Exception:
        pass

#                                                          Te

@bot.on_message(filters.private)
async def _(bot, cmd):
    await handle_user_status(bot, cmd)

@bot.on_message(filters.command("start") & filters.private)
async def startprivate(client, message):
    # return
    chat_id = message.from_user.id
    if not await db.is_user_exist(chat_id):
        data = await client.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        if LOG_CHANNEL:
            await client.send_message(
                LOG_CHANNEL,
                f"#AZIKPDF: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
            )
        else:
            logging.info(f"#NewUser :- Name : {message.from_user.first_name} ID : {message.from_user.id}")
    joinButton = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌟 AziK ProJecTs 🌟",
                            callback_data="strtDevEdt"
                        ),
                        InlineKeyboardButton(
                            "Bot bilan tanishish 🎊",
                            callback_data="exploreBot"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Yopish ⛔️",
                            callback_data="close"
                        )
                    ]
                ]
            )
    
    welcomed = f"Hey <b>{message.from_user.first_name}</b>\nI'm a simple Telegram bot that can broadcast messages and media to the bot subscribers. Made by @NACBOTS.\n\n 🎚 use /settings"
    await message.reply_text(welcomeMsg, reply_markup=joinButton)
    raise StopPropagation


@bot.on_message(filters.command("settings1"))
async def opensettings(bot, cmd):
    user_id = cmd.from_user.id
    await cmd.reply_text(
        f"`Here You Can Set Your Settings:`\n\nSuccessfully setted notifications to **{await db.get_notif(user_id)}**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"NOTIFICATION  {'🔔' if ((await db.get_notif(user_id)) is True) else '🔕'}",
                        callback_data="notifon",
                    )
                ],
                [InlineKeyboardButton("❎", callback_data="closeMeh")],
            ]
        ),
    )


@bot.on_message(filters.private & filters.command("broadcast"))
async def broadcast_handler_open(_, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if m.reply_to_message is None:
        await m.delete()
    else:
        await broadcast(m, db)


@bot.on_message(filters.private & filters.command("statistika"))
async def sts(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    await m.reply_text(
        text=f"**Malumotlar bazasidagi umumiy foydalanuvchilar 📂:** `{await db.total_users_count()}`ta \n\n**Bot bildirishnomalarini yoqqan foydalanuvchilar 🔔 :** `{await db.total_notif_users_count()}`ta",
        parse_mode="Markdown",
        quote=True
    )


@bot.on_message(filters.private & filters.command("ban_user"))
async def ban(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban 🛑 any user from the bot 🤖.\n\nUsage:\n\n`/ban_user user_id ban_duration ban_reason`\n\nEg: `/ban_user 1234567 28 You misused me.`\n This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = " ".join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."

        try:
            await c.send_message(
                user_id,
                f"You are Banned 🚫 to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin 🤠**",
            )
            ban_log_text += "\n\nUser notified successfully!"
        except BaseException:
            traceback.print_exc()
            ban_log_text += (
                f"\n\n ⚠️ User notification failed! ⚠️ \n\n`{traceback.format_exc()}`"
            )
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(ban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@bot.on_message(filters.private & filters.command("unban_user"))
async def unban(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban 😃 any user.\n\nUsage:\n\n`/unban_user user_id`\n\nEg: `/unban_user 1234567`\n This will unban user with id `1234567`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user 🤪 {user_id}"

        try:
            await c.send_message(user_id, f"Your ban was lifted!")
            unban_log_text += "\n\n✅ User notified successfully! ✅"
        except BaseException:
            traceback.print_exc()
            unban_log_text += (
                f"\n\n⚠️ User notification failed! ⚠️\n\n`{traceback.format_exc()}`"
            )
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(unban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"⚠️ Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True,
        )


@bot.on_message(filters.private & filters.command("banned_users"))
async def _banned_usrs(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ""
    async for banned_user in all_banned_users:
        user_id = banned_user["id"]
        ban_duration = banned_user["ban_status"]["ban_duration"]
        banned_on = banned_user["ban_status"]["banned_on"]
        ban_reason = banned_user["ban_status"]["ban_reason"]
        banned_usr_count += 1
        text += f"> **User_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, **Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s) 🤭: `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open("banned-users.txt", "w") as f:
            f.write(reply_text)
        await m.reply_document("banned-users.txt", True)
        os.remove("banned-users.txt")
        return
    await m.reply_text(reply_text, True)


@bot.on_callback_query()
async def callback_handlers(bot: Client, cb: CallbackQuery):
    user_id = cb.from_user.id
    if cb.data == "notifon":
        notif = await db.get_notif(cb.from_user.id)
        if notif is True:
            await db.set_notif(user_id, notif=False)
        else:
            await db.set_notif(user_id, notif=True)
        await cb.message.edit(
            f"`Here You Can Set Your Settings:`\n\nSuccessfully setted notifications to **{await db.get_notif(user_id)}**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"NOTIFICATION  {'🔔' if ((await db.get_notif(user_id)) is True) else '🔕'}",
                            callback_data="notifon",
                        )
                    ],
                    [InlineKeyboardButton("❎", callback_data="closeMeh")],
                ]
            ),
        )
        await cb.answer(
            f"Successfully setted notifications to {await db.get_notif(user_id)}"
        )
    else:
        await cb.message.delete(True)


bot.run()
