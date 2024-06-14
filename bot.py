import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters
from config import BOT_TOKEN, conn, c

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

FIRST_NAME, LAST_NAME, AGE, ADDRESS, PROFICIENCY, PHONE_NUMBER, CONFIRM = range(7)

async def start(update: Update, context):
    await update.message.reply_text(
        "Assalomu Aleykum 👋! Aketa bo'tga hush kelibsiz! Anketa to'ldirsh uchun quyidagi tugmani bosing 👇",
        reply_markup=ReplyKeyboardMarkup([["Anketa to'ldirish ✍️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return FIRST_NAME

async def start_application(update: Update, context):
    await update.message.reply_text(
        'Ismingiz nima?',
        reply_markup=ReplyKeyboardRemove()
    )
    return FIRST_NAME

async def first_name(update: Update, context):
    context.user_data['first_name'] = update.message.text
    context.user_data['last_state'] = FIRST_NAME
    await update.message.reply_text(
        'Familiyangiz nima?',
        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return LAST_NAME

async def last_name(update: Update, context):
    if update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)
    elif update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)

    context.user_data['last_name'] = update.message.text
    context.user_data['last_state'] = LAST_NAME
    await update.message.reply_text(
        'Yoshingiz nechida?',
        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return AGE

async def age(update: Update, context):
    if update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)

    try:
        age = int(update.message.text)
        if age <= 0 or age >= 150:
            raise ValueError
        context.user_data['age'] = age
        context.user_data['last_state'] = AGE
        await update.message.reply_text(
            'Manzilingizni kiriting?',
            reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
        )
        return ADDRESS
    except ValueError:
        await update.message.reply_text(
            'Yoshni to\'g\'ri kiriting yoki "Bekor Qilish" deb yozing.',
            reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
        )
        return AGE

async def address(update: Update, context):
    if update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)

    context.user_data['address'] = update.message.text
    context.user_data['last_state'] = ADDRESS
    await update.message.reply_text(
        'Qanday darajadasiz (masalan, Boshlang\'ich, O\'rta, Yaxshi)?',
        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return PROFICIENCY

async def proficiency(update: Update, context):
    if update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)

    context.user_data['proficiency'] = update.message.text
    context.user_data['last_state'] = PROFICIENCY
    await update.message.reply_text(
        'Quyidagi tugmani bosish orqali telefon raqamingizni kiriting:',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton('Telefon raqamimni yuborish', request_contact=True)], ['Orqaga 👈', 'Bekor Qilish ❌']],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return PHONE_NUMBER

async def phone_number(update: Update, context):
    if update.message.contact:
        context.user_data['phone_number'] = update.message.contact.phone_number
    else:
        text = update.message.text.lower()
        if text == 'bekor qilish ❌'.lower():
            return await cancel(update, context)
        elif text == 'orqaga 👈'.lower():
            return await back(update, context)
        else:
            context.user_data['phone_number'] = update.message.text

    context.user_data['last_state'] = PHONE_NUMBER
    await update.message.reply_text(
        'Rahmat! Mana bu yerda taqdim etgan ma\'lumotlaringiz:\n'
        f"Ism: {context.user_data['first_name']}\n"
        f"Familiya: {context.user_data['last_name']}\n"
        f"Yosh: {context.user_data['age']}\n"
        f"Manzil: {context.user_data['address']}\n"
        f"Daraja: {context.user_data['proficiency']}\n"
        f"Telefon raqami: {context.user_data['phone_number']}\n"
        'Bu to\'g\'rimi? (Ha/Yo\'q)',
        reply_markup=ReplyKeyboardMarkup([['Ha', 'Yo\'q'], ['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return CONFIRM

async def confirm(update: Update, context):
    response = update.message.text.lower()
    if response == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif response == 'orqaga 👈'.lower():
        return await back(update, context)

    if response == 'ha':
        first_name = context.user_data['first_name']
        last_name = context.user_data['last_name']
        age = context.user_data['age']
        address = context.user_data['address']
        proficiency = context.user_data['proficiency']
        phone_number = context.user_data['phone_number']

        c.execute(
            "INSERT INTO user_data (first_name, last_name, age, address, proficiency, phone_number) VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, age, address, proficiency, phone_number))
        conn.commit()

        await update.message.reply_text('Ma\'lumotlaringiz saqlandi. Rahmat!',
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif response == 'yo\'q':
        await update.message.reply_text('OK, qaytadan boshlaymiz.',
                                        reply_markup=ReplyKeyboardRemove())
        return start_application(update, context)
    else:
        await update.message.reply_text('Iltimos, Ha yoki Yo\'q deb javob bering.',
                                        reply_markup=ReplyKeyboardMarkup([['Ha', 'Yo\'q'], ['Orqaga 👈', 'Bekor Qilish ❌']],
                                                                         resize_keyboard=True, one_time_keyboard=True))
        return CONFIRM

async def back(update: Update, context):
    current_state = context.user_data.get('last_state', None)
    previous_state = {
        LAST_NAME: FIRST_NAME,
        AGE: LAST_NAME,
        ADDRESS: AGE,
        PROFICIENCY: ADDRESS,
        PHONE_NUMBER: PROFICIENCY,
        CONFIRM: PHONE_NUMBER
    }.get(current_state, FIRST_NAME)

    context.user_data['last_state'] = previous_state

    if previous_state == FIRST_NAME:
        return await start_application(update, context)
    elif previous_state == LAST_NAME:
        await update.message.reply_text('Familiyangiz nima?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return LAST_NAME
    elif previous_state == AGE:
        await update.message.reply_text('Yoshingiz nechida?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return AGE
    elif previous_state == ADDRESS:
        await update.message.reply_text('Manzilingizni kiriting?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return ADDRESS
    elif previous_state == PROFICIENCY:
        await update.message.reply_text('Qanday darajadasiz (masalan, Boshlang\'ich, O\'rta, Yaxshi)?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return PROFICIENCY
    elif previous_state == PHONE_NUMBER:
        await update.message.reply_text('Quyidagi tugmani bosish orqali telefon raqamingizni kiriting:',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [[KeyboardButton('Telefon raqamimni yuborish', request_contact=True)], ['Orqaga 👈', 'Bekor Qilish ❌']],
                                            resize_keyboard=True, one_time_keyboard=True))
        return PHONE_NUMBER
    else:
        await update.message.reply_text('Boshlanishiga qaytdi...',
                                        reply_markup=ReplyKeyboardRemove())
        return start_application(update, context)

async def cancel(update: Update, context):
    await update.message.reply_text(
        'Ariza bekor qilindi. Qaytadan boshlash uchun quyidagi tugmani bosing.',
        reply_markup=ReplyKeyboardMarkup([["Anketa to'ldirish ✍️"]], resize_keyboard=True, one_time_keyboard=True))
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("Anketa to'ldirish ✍️"), start_application)
        ],
        states={
            FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, first_name),
            ],
            LAST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, last_name),
            ],
            AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, age),
            ],
            ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, address),

            ],
            PROFICIENCY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, proficiency),
            ],
            PHONE_NUMBER: [
                MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, phone_number),
            ],
            CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex('^Bekor Qilish ❌$'), cancel),
            MessageHandler(filters.Regex('^Orqaga 👈$'), back)
        ]
    )

    application.add_handler(conv_handler)
    logger.info('Bot is starting...')
    application.run_polling()

if __name__ == '__main__':
    main()
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters
from config import BOT_TOKEN, conn, c

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

FIRST_NAME, LAST_NAME, AGE, ADDRESS, PROFICIENCY, PHONE_NUMBER, CONFIRM = range(7)

async def start(update: Update, context):
    await update.message.reply_text(
        "Assalomu Aleykum 👋! Aketa bo'tga hush kelibsiz! Anketa to'ldirsh uchun quyidagi tugmani bosing 👇",
        reply_markup=ReplyKeyboardMarkup([["Anketa to'ldirish ✍️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return FIRST_NAME

async def start_application(update: Update, context):
    await update.message.reply_text(
        'Ismingiz nima?',
        reply_markup=ReplyKeyboardRemove()
    )
    return FIRST_NAME

async def first_name(update: Update, context):
    context.user_data['first_name'] = update.message.text
    context.user_data['last_state'] = FIRST_NAME
    await update.message.reply_text(
        'Familiyangiz nima?',
        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return LAST_NAME

async def last_name(update: Update, context):
    if update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)
    elif update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)

    context.user_data['last_name'] = update.message.text
    context.user_data['last_state'] = LAST_NAME
    await update.message.reply_text(
        'Yoshingiz nechida?',
        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return AGE

async def age(update: Update, context):
    if update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)

    try:
        age = int(update.message.text)
        if age <= 0 or age >= 150:
            raise ValueError
        context.user_data['age'] = age
        context.user_data['last_state'] = AGE
        await update.message.reply_text(
            'Manzilingizni kiriting?',
            reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
        )
        return ADDRESS
    except ValueError:
        await update.message.reply_text(
            'Yoshni to\'g\'ri kiriting yoki "Bekor Qilish" deb yozing.',
            reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
        )
        return AGE

async def address(update: Update, context):
    if update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)

    context.user_data['address'] = update.message.text
    context.user_data['last_state'] = ADDRESS
    await update.message.reply_text(
        'Qanday darajadasiz (masalan, Boshlang\'ich, O\'rta, Yaxshi)?',
        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return PROFICIENCY

async def proficiency(update: Update, context):
    if update.message.text.lower() == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif update.message.text.lower() == 'orqaga 👈'.lower():
        return await back(update, context)

    context.user_data['proficiency'] = update.message.text
    context.user_data['last_state'] = PROFICIENCY
    await update.message.reply_text(
        'Quyidagi tugmani bosish orqali telefon raqamingizni kiriting:',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton('Telefon raqamimni yuborish', request_contact=True)], ['Orqaga 👈', 'Bekor Qilish ❌']],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return PHONE_NUMBER

async def phone_number(update: Update, context):
    if update.message.contact:
        context.user_data['phone_number'] = update.message.contact.phone_number
    else:
        text = update.message.text.lower()
        if text == 'bekor qilish ❌'.lower():
            return await cancel(update, context)
        elif text == 'orqaga 👈'.lower():
            return await back(update, context)
        else:
            context.user_data['phone_number'] = update.message.text

    context.user_data['last_state'] = PHONE_NUMBER
    await update.message.reply_text(
        'Rahmat! Mana bu yerda taqdim etgan ma\'lumotlaringiz:\n'
        f"Ism: {context.user_data['first_name']}\n"
        f"Familiya: {context.user_data['last_name']}\n"
        f"Yosh: {context.user_data['age']}\n"
        f"Manzil: {context.user_data['address']}\n"
        f"Daraja: {context.user_data['proficiency']}\n"
        f"Telefon raqami: {context.user_data['phone_number']}\n"
        'Bu to\'g\'rimi? (Ha/Yo\'q)',
        reply_markup=ReplyKeyboardMarkup([['Ha', 'Yo\'q'], ['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return CONFIRM

async def confirm(update: Update, context):
    response = update.message.text.lower()
    if response == 'bekor qilish ❌'.lower():
        return await cancel(update, context)
    elif response == 'orqaga 👈'.lower():
        return await back(update, context)

    if response == 'ha':
        first_name = context.user_data['first_name']
        last_name = context.user_data['last_name']
        age = context.user_data['age']
        address = context.user_data['address']
        proficiency = context.user_data['proficiency']
        phone_number = context.user_data['phone_number']

        c.execute(
            "INSERT INTO user_data (first_name, last_name, age, address, proficiency, phone_number) VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, age, address, proficiency, phone_number))
        conn.commit()

        await update.message.reply_text('Ma\'lumotlaringiz saqlandi. Rahmat!',
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif response == 'yo\'q':
        await update.message.reply_text('OK, qaytadan boshlaymiz.',
                                        reply_markup=ReplyKeyboardRemove())
        return start_application(update, context)
    else:
        await update.message.reply_text('Iltimos, Ha yoki Yo\'q deb javob bering.',
                                        reply_markup=ReplyKeyboardMarkup([['Ha', 'Yo\'q'], ['Orqaga 👈', 'Bekor Qilish ❌']],
                                                                         resize_keyboard=True, one_time_keyboard=True))
        return CONFIRM

async def back(update: Update, context):
    current_state = context.user_data.get('last_state', None)
    previous_state = {
        LAST_NAME: FIRST_NAME,
        AGE: LAST_NAME,
        ADDRESS: AGE,
        PROFICIENCY: ADDRESS,
        PHONE_NUMBER: PROFICIENCY,
        CONFIRM: PHONE_NUMBER
    }.get(current_state, FIRST_NAME)

    context.user_data['last_state'] = previous_state

    if previous_state == FIRST_NAME:
        return await start_application(update, context)
    elif previous_state == LAST_NAME:
        await update.message.reply_text('Familiyangiz nima?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return LAST_NAME
    elif previous_state == AGE:
        await update.message.reply_text('Yoshingiz nechida?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return AGE
    elif previous_state == ADDRESS:
        await update.message.reply_text('Manzilingizni kiriting?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return ADDRESS
    elif previous_state == PROFICIENCY:
        await update.message.reply_text('Qanday darajadasiz (masalan, Boshlang\'ich, O\'rta, Yaxshi)?',
                                        reply_markup=ReplyKeyboardMarkup([['Orqaga 👈', 'Bekor Qilish ❌']], resize_keyboard=True, one_time_keyboard=True))
        return PROFICIENCY
    elif previous_state == PHONE_NUMBER:
        await update.message.reply_text('Quyidagi tugmani bosish orqali telefon raqamingizni kiriting:',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [[KeyboardButton('Telefon raqamimni yuborish', request_contact=True)], ['Orqaga 👈', 'Bekor Qilish ❌']],
                                            resize_keyboard=True, one_time_keyboard=True))
        return PHONE_NUMBER
    else:
        await update.message.reply_text('Boshlanishiga qaytdi...',
                                        reply_markup=ReplyKeyboardRemove())
        return start_application(update, context)

async def cancel(update: Update, context):
    await update.message.reply_text(
        'Ariza bekor qilindi. Qaytadan boshlash uchun quyidagi tugmani bosing.',
        reply_markup=ReplyKeyboardMarkup([["Anketa to'ldirish ✍️"]], resize_keyboard=True, one_time_keyboard=True))
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("Anketa to'ldirish ✍️"), start_application)
        ],
        states={
            FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, first_name),
            ],
            LAST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, last_name),
            ],
            AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, age),
            ],
            ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, address),

            ],
            PROFICIENCY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, proficiency),
            ],
            PHONE_NUMBER: [
                MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, phone_number),
            ],
            CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex('^Bekor Qilish ❌$'), cancel),
            MessageHandler(filters.Regex('^Orqaga 👈$'), back)
        ]
    )

    application.add_handler(conv_handler)
    logger.info('Bot is starting...')
    application.run_polling()

if __name__ == '__main__':
    main()
