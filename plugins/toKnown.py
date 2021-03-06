# fileName : plugins/toKnown.py
# copyright ÂŠī¸ 2021 nabilanavab

from pyrogram.types import Message
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
#------------------->

pdfInfoMsg = """`Ushbu faylni nima qilishni xohlaysiz?`

Fayl Nomi : `{}`
Fayl Hajmi : `{}`

`Sahifalar soni: {}`ta"""

#--------------->
#--------> EDIT CHECKPDF MESSAGE (IF PDF & NOT ENCRYPTED)
#------------------->

# convert unknown to known page number msgs
async def toKnown(callbackQuery, number_of_pages):
    try:
        fileName = callbackQuery.message.reply_to_message.document.file_name
        fileSize = callbackQuery.message.reply_to_message.document.file_size
        
        await callbackQuery.edit_message_text(
            pdfInfoMsg.format(
                fileName, await gSF(fileSize), number_of_pages
            ),
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Ma'lumot â­", callback_data=f"KpdfInfo|{number_of_pages}"),
                        InlineKeyboardButton("Ko'rib chiqish đŗī¸", callback_data="Kpreview")
                    ],[
                        InlineKeyboardButton("Rasmga o'tkazish đŧī¸", callback_data=f"KtoImage|{number_of_pages}"),
                        InlineKeyboardButton("Matnga o'tkazish âī¸", callback_data=f"KtoText|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Himoyalash đ", callback_data=f"Kencrypt|{number_of_pages}"),
                        InlineKeyboardButton("Himoyadan ochish đ", callback_data=f"notEncrypted")
                    ],[
                        InlineKeyboardButton("Siqish đī¸", callback_data=f"Kcompress"),
                        InlineKeyboardButton("Aylantirish đ¤¸", callback_data=f"Krotate|{number_of_pages}")
                    ],[
                        InlineKeyboardButton("Kesish âī¸", callback_data=f"Ksplit|{number_of_pages}"),
                        InlineKeyboardButton("Birlashtirish đ§Ŧ",callback_data="merge")
                    ],[
                        InlineKeyboardButton("Pechat qo'yish âĸī¸",callback_data=f"Kstamp|{number_of_pages}"),
                        InlineKeyboardButton("Qayta nomlash âī¸",callback_data="rename")
                    ],[
                        InlineKeyboardButton("Yopish đĢ", callback_data="closeALL")
                    ]
                ]
            )
        )
    except Exception as e:
        print(f"plugins/toKnown: {e}")

#                                                                                  Telegram: @nabilanavab
