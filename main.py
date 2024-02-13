from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio
from telebot.asyncio_helper import ApiTelegramException
import logging
from telebot import asyncio_helper

from credentials import BOT_TOKEN, answerer_id, local_server

if local_server != None:
    asyncio_helper.API_URL = local_server + "/bot{0}/{1}"
    asyncio_helper.FILE_URL = local_server

bot = AsyncTeleBot(BOT_TOKEN)

rapid_answers = [
    {
        "text": "📢 Para poder darte una respuesta ajustada a tu duda conviene que, al formularla, nos ofrezcas contexto y, en su caso, información sobre lo que se quiere expresar.",
        "title": "Contexto",
    },
    {
        "text": "📚 Recuerda que esta duda puedes resolverla si consultas el «Diccionario de la lengua española» mediante el bot @dlebot.",
        "title": "Diccionario",
    },
    {
        "text": "❌ Lo sentimos, pero solo atendemos dudas sobre el uso correcto del español actual. Su consulta queda fuera de los límites establecidos para este servicio. Esperamos serte de utilidad en otra ocasión.",
        "title": "Duda",
    },
    {
        "text": "❌ Lo sentimos, pero no atendemos dudas sobre sinónimos y antónimos. Esperamos serte de utilidad en otra ocasión.",
        "title": "Sinonimia Y Antonimia",
    },
    {
        "text": "❌ Lo sentimos, pero no atendemos dudas sobre cuestiones teóricas, terminológicas o de análisis gramatical. Esperamos serte de utilidad en otra ocasión. ",
        "title": "Teoría",
    },
    {
        "text": "❌ Lo sentimos, pero no atendemos dudas sobre curiosidades lingüísticas o de otra índole carentes de problemas normativos. Esperamos serte de utilidad en otra ocasión.",
        "title": "Curiosidades",
    },
    {
        "text": "❌ Lo sentimos, pero no atendemos dudas sobre la búsqueda del significante adecuado para un objeto o concepto determinado. Esperamos serte de utilidad en otra ocasión.",
        "title": "Significado",
    },
]

COMMANDS_TEXT = {
    "duda": "👨‍🏫 Si tienes una duda lingüística, plantéanosla en un solo mensaje. Al formularla, recuerda ofrecernos contexto y escribir la etiqueta #duda.",
    "sugerencia": "📝 Envíanos sugerencias para mejorar nuestro trabajo. Siempre serán bien recibidas. Redáctala en un solo mensaje y recuerda incluir la etiqueta #sugerencia.\n\n✍️ Puedes hacernos propuestas de temas para que nuestros panelistas de «Escriba y lea» los descrifren.",
    "ayuda": '📕 Este es nuestro <a href="https://telegra.ph/Vademécum-10-15">vademécum</a>, un libro de poco volumen y fácil manejo para conocer mejor qué es el proyecto @Buen_Idioma.',
    "podcast": "🎧 En nuestra página podrás escuchar todas las emisiones del pódcast «Píldoras Buen Idioma».",
    "blog": "💻 En nuestro blog podrás encontrar recomendaciones lingüísticas sobre el uso correcto del español actual.",
}

USER_FEEDBACK = {
    "duda": "👌 Gracias por formularnos esta consulta. Te responderemos lo antes posible.",
    "sugerencia": "👌 Gracias por hacernos esta sugerencia. La valoraremos y tendremos en cuenta. Saludos.",
}

COMMANDS_MARKUP = {
    "duda": None,
    "sugerencia": None,
    "ayuda": None,
    "podcast": types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    "🎧 Escuchar en buenidioma.com",
                    url="https://buenidioma.com/podcast/",
                )
            ]
        ]
    ),
    "blog": types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    "👨🏻‍💻 Visitar el blog",
                    url="https://buenidioma.com",
                )
            ]
        ]
    ),
}

START_TEXT = "<b>¡Hola, {}! 👋 Este es el bot oficial del canal @BuenIdioma.</b>\n\n📢 Para comunicarte con nosotros presiona uno de los comandos del «Menú».\n\n⚠️ Aquí atendemos dudas sobre el uso correcto del español actual y recibimos sugerencia para mejorar nuestro trabajo. \n\n📍 También puedes unirte al grupo @DudasBuenIdioma y cuando quieras nos planteas tus dudas por allá. No olvides la etiqueta #duda.\n\n<b>🤖 Las consultas son atendidas por personas, así que espera con calma. Te responderemos lo antes posible. Muchas gracias.</b>"

DEAD_END_MESSAGE = "#️⃣ Para poder responderte, debes incluir la etiqueta #duda o #sugerencia según el caso. Recuerda también escribirlo todo en un solo mensaje. Disculpa las molestias ocasionadas."

rapid_answers_inline_results = []


@bot.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    await bot.send_message(
        message.chat.id,
        START_TEXT.format(message.from_user.first_name),
        parse_mode="HTML",
    )


async def send_duda(message: types.Message, text: str, command: str):
    inline_kb = types.InlineKeyboardMarkup()
    inline_kb.row(
        types.InlineKeyboardButton(
            "⤷ 0", callback_data=f"fwd_{message.chat.id}_{message.id}"
        ),
        types.InlineKeyboardButton("❔☑️", callback_data=f"check"),
    )
    inline_kb.row(
        types.InlineKeyboardButton(
            "Respuesta Rápida", switch_inline_query_current_chat=""
        )
    )

    ans_text = f'<a href="tg://user?id={message.from_user.id}" >{message.from_user.first_name}</a> | #{command}\n\n{text}'
    await bot.send_message(
        answerer_id, ans_text, reply_markup=inline_kb, parse_mode="HTML"
    )
    await bot.send_message(message.from_user.id, USER_FEEDBACK[command])


@bot.message_handler(commands=[x for x in COMMANDS_TEXT])
async def handle_commands(message: types.Message):
    splitted = message.html_text[1:].split(" ", 1)
    command = splitted[0]
    if command in ["duda", "sugerencia"] and len(splitted) > 1:
        await send_duda(message, splitted[1], command)
    else:
        await bot.send_message(
            message.chat.id,
            COMMANDS_TEXT[command],
            parse_mode="HTML",
            reply_markup=COMMANDS_MARKUP[command],
        )


@bot.message_handler(chat_types=["private"])
async def handle_messages(message: types.Message):
    if message.from_user.id != answerer_id:
        # User asks #duda or sends #sugerencia
        for hashtag in ["duda", "sugerencia"]:
            if f"#{hashtag}" in message.text:
                await send_duda(message, message.html_text, hashtag)
                return
        await bot.send_message(message.chat.id, DEAD_END_MESSAGE)

    elif message.reply_to_message:
        # Answerer responds )

        original = message.reply_to_message

        # Look for data to send reply inside the inlineKeyboard
        if original.reply_markup:
            inline_kb = original.reply_markup.keyboard

            for row in inline_kb:
                for button in row:
                    if (
                        button.callback_data
                        and button.callback_data == "check"
                        or button.callback_data == "uncheck"
                    ):
                        check_uncheck = button.callback_data

            for row in inline_kb:
                for button in row:
                    if button.callback_data and button.callback_data.startswith(
                        "fwd"
                    ):  # counter and data holder
                        splitted = button.callback_data.split("_")
                        chat_id = splitted[1]
                        message_id = splitted[2]
                        count = int(button.text[1:])
                        button.text = f"⤷ {count + 1}"

                        # Sends response
                        feedback_button = types.InlineKeyboardMarkup(
                            [
                                [
                                    types.InlineKeyboardButton(
                                        "🕹 ¡Gracias!, duda resuelta.",
                                        callback_data=f"solved_{original.chat.id}_{original.id}_{count + 1}_{check_uncheck}_{chat_id}_{message_id}",
                                    )
                                ]
                            ]
                        )
                        try:
                            await bot.send_message(
                                chat_id,
                                message.html_text,
                                reply_to_message_id=message_id,
                                reply_markup=(
                                    feedback_button
                                    if "#BuenIdiomaResponde" in message.text
                                    else None
                                ),
                                parse_mode="HTML",
                            )
                        except ApiTelegramException as e:
                            await bot.send_message(
                                message.chat.id, "😢 El usuario bloqueó el bot."
                            )
                            button.text = f"❌ {count}"
                            # Edit answerer message to increment counter
                            await bot.edit_message_reply_markup(
                                original.chat.id,
                                original.id,
                                reply_markup=types.InlineKeyboardMarkup(inline_kb),
                            )
                            raise e

            await bot.edit_message_reply_markup(
                original.chat.id,
                original.id,
                reply_markup=types.InlineKeyboardMarkup(inline_kb),
            )


@bot.callback_query_handler(lambda q: q.data.startswith("fwd"))
async def handle_fwd_callback(q: types.CallbackQuery):
    await bot.answer_callback_query(
        q.id, "To answer this query reply to the message.", cache_time=300
    )


@bot.callback_query_handler(lambda q: q.data == "check" or q.data == "uncheck")
async def handle_check_uncheck_callback(q: types.CallbackQuery):
    inline_kb = q.message.reply_markup.keyboard
    # Search for the check button
    for row in inline_kb:
        for button in row:
            if button.callback_data == "check" or button.callback_data == "uncheck":
                button.text = button.text[0] + (
                    "✅" if button.callback_data == "check" else "☑️"
                )
                button.callback_data = (
                    "uncheck" if button.callback_data == "check" else "check"
                )
    await bot.edit_message_reply_markup(
        q.message.chat.id,
        q.message.id,
        reply_markup=types.InlineKeyboardMarkup(inline_kb),
    )


@bot.callback_query_handler(lambda q: q.data.startswith("solved"))
async def handle_check_uncheck_callback(q: types.CallbackQuery):
    await bot.edit_message_text(
        q.message.html_text + "\n\n#DudaResuelta",
        q.message.chat.id,
        q.message.id,
        reply_markup=None,
        parse_mode="HTML",
    )

    splitted = q.data.split("_")
    chat_id = int(splitted[1])
    message_id = int(splitted[2])
    count = splitted[3]
    check_uncheck = splitted[4]
    callback_chat = splitted[5]
    callback_message = splitted[6]

    inline_kb = types.InlineKeyboardMarkup()
    inline_kb.row(
        types.InlineKeyboardButton(
            f"⤷ {count}", callback_data=f"fwd_{callback_chat}_{callback_message}"
        ),
        types.InlineKeyboardButton(
            "✔️" + ("☑️" if check_uncheck == "check" else "✅"),
            callback_data=check_uncheck,
        ),
    )
    inline_kb.row(
        types.InlineKeyboardButton(
            "Respuesta Rápida", switch_inline_query_current_chat=""
        )
    )

    await bot.answer_callback_query(q.id, "¡Gracias por la retroalimentación!")
    await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=inline_kb)


@bot.inline_handler(lambda q: True)
async def hanlde_inline(q: types.InlineQuery):
    if q.from_user.id == answerer_id:
        await bot.answer_inline_query(
            q.id, rapid_answers_inline_results, is_personal=True
        )
    else:
        await bot.answer_inline_query(
            q.id,
            [],
            switch_pm_parameter="_",
            switch_pm_text="Preguntar a través del bot.",
            is_personal=True,
        )


if __name__ == "__main__":
    for i, answer in enumerate(rapid_answers):
        rapid_answers_inline_results.append(
            types.InlineQueryResultArticle(
                f"{i}",
                answer["title"],
                input_message_content=types.InputTextMessageContent(answer["text"]),
                description=answer["text"],
            )
        )

    asyncio.run(bot.infinity_polling(logger_level=logging.WARNING))
