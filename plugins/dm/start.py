# fileName : plugins/dm/start.py
# copyright ©️ 2021 nabilanavab

from pdf import invite_link
from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as ILovePDF
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
#------------------->

welcomeMsg = """Salom [{}](tg://user?id={})..!!
Men bilan siz PDF fayllarni ko'p funksiyalarni amalga oshirishingiz mumkin  🥳

Asosiy xususiyatlardan ba'zilari:
◍ `Rasmlarni PDF ga o'tkazish`
◍ `PDFni rasmlarga o'tkazish`
◍ `Faylni PDFga o'tkazish`
◍ `Botni o'zida matnni PDF qilish`
◍ `PDFlarni himoylash, birlashtirish, oldindan ko'rish, aylantirish, pechat qo'yish va boshqalar`

Proyektlar kanali: @azik_projects 💎

[Administrator 🧑‍💻](https://t.me/azik_developer)
[Taklif va shikoyat yozish 📋](https://t.me/azik_projects_support)"""

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

@bot.on_message(filters.private & ~filters.edited & filters.command(["start"]))
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
                    reply_markup = InlineKeyboardMarkup(
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
