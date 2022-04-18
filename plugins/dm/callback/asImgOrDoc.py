# fileName : plugins/dm/callBack/asImgOrDoc.py
# copyright ©️ 2021 nabilanavab

from pyrogram import filters
from pyrogram import Client as ILovePDF
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
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
@ILovePDF.on_callback_query(I)
async def _I(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__Pdfni Rasmga (rasm formatida) o'tkazish \nUmumiy safifalar: Noma'lum😐__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hammasini chiqarish 🙄", callback_data="IA")
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
@ILovePDF.on_callback_query(D)
async def _D(bot, callbackQuery):
    try:
        await callbackQuery.edit_message_text(
            "__Pdfni Rasmga (fayl formatida) o'tkazish \nUmumiy sahifalar: Noma'lum😐__",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hammasini chiqarish 🙄", callback_data="DA")
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
@ILovePDF.on_callback_query(KI)
async def _KI(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Pdfni Rasmga (rasm formatida) o'tkazish   \nUmumiy sahifalar: {number_of_pages}ta__ 🌟",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hammasini chiqarish 🙄", callback_data=f"KIA|{number_of_pages}")
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
@ILovePDF.on_callback_query(KD)
async def _KD(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await callbackQuery.edit_message_text(
            f"__Pdf ni Rasmga (fayl formatida) o'tkazish \nUmumiy sahifalar: {number_of_pages}ta__ 🌟",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Hammasini chiqarish 🙄", callback_data=f"KDA|{number_of_pages}")
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
@ILovePDF.on_callback_query(toImage)
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
@ILovePDF.on_callback_query(KtoImage)
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
@ILovePDF.on_callback_query(BTPM)
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
@ILovePDF.on_callback_query(KBTPM)
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

#                                                                                             Telegram: @nabilanavab
