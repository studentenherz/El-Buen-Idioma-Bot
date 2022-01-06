from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio

from credentials import BOT_TOKEN, answerer_id

bot = AsyncTeleBot(BOT_TOKEN)

rapid_answers = [{'text' : '👋 Hola. Gracias por comunicarte con el bot oficial del canal @Buen_Idioma. ¿Tienes una duda lingüística? Plantéanosla.', 
'title' : 'Saludo'}, 
{'text' : '📢 Para poder darte una respuesta ajustada a tu duda conviene que, al formularla, nos ofrezcas contexto y, en su caso, información sobre lo que se quiere expresar.', 
'title' : 'Contexto'}, 
{'text' : '📚 Recuerda que esta duda puedes resolverla si consultas el «Diccionario de la lengua española» mediante el bot @dleraebot.', 
'title' : 'Diccionario'}, 
{'text' : '❌ Lo sentimos, pero solo atendemos dudas sobre el uso correcto del español actual. Su consulta queda fuera de los límites establecidos para este servicio. Esperamos serte de utilidad en otra ocasión.', 
'title' : 'Duda'}, 
{'text' : '❌ Lo sentimos, pero no atendemos dudas sobre sinónimos y antónimos. Esperamos serte de utilidad en otra ocasión.', 
'title' : 'Sinonimia Y Antonimia'}, 
{'text' : '❌ Lo sentimos, pero no atendemos dudas sobre cuestiones teóricas, terminológicas o de análisis gramatical. Esperamos serte de utilidad en otra ocasión. ', 
'title' : 'Teoría'}, 
{'text' : '❌ Lo sentimos, pero no atendemos dudas sobre curiosidades lingüísticas o de otra índole carentes de problemas normativos. Esperamos serte de utilidad en otra ocasión.', 
'title' : 'Curiosidades'}, 
{'text' : '❌ Lo sentimos, pero no atendemos dudas sobre la búsqueda del significante adecuado para un objeto o concepto determinado. Esperamos serte de utilidad en otra ocasión.', 
'title' : 'Significado'}
]

COMMANDS_TEXT = {
	'duda' : '👨‍🏫 Si tienes una duda lingüística, plantéanosla. Al formularla, recuerda ofrecernos contexto y escribir al inicio la etiqueta #duda.',
	'participar': '🔷 Si deseas ser concursante de «Pasapalabra», envíanos tu nombre de usuario para inscribirte en la «Silla Azul». 🔠 Una vez se acerque la fecha de esta dinámica, te avisaremos.',
	'sugerencias': '📝 Envíanos sugerencias para mejorar nuestro trabajo. Siempre serán bien recibidas. Recuerda usar la etiqueta #sugerencias en tu mensaje.\n\n✍️ Puedes hacernos propuestas de temas para que nuestros panelistas de «Escriba y lea» los descrifren.',
	'ayuda' : '📕 Este es nuestro <a href="https://telegra.ph/Vademécum-10-15">vademécum</a>, un libro de poco volumen y fácil manejo para conocer mejor qué es el proyecto @Buen_Idioma.',
	'podcast' : '🎧 En Anchor podrás escuchar todas las emisiones del pódcast «Píldoras Buen Idioma».',
	'blog' : '💻 En nuestro blog podrás encontrar recomendaciones lingüísticas sobre el uso correcto del español actual.'
}

USER_FEEDBACK = {
	'duda': '👌 Gracias por formularnos esta consulta. Te responderemos lo antes posible.',
	'sugerencias': '👌 Gracias por hacernos esta sugerencia. La valoraremos y tendremos en cuenta. Saludos.'
}

COMMANDS_MARKUP = {
	'duda' :  None,
	'participar' : None,
	'sugerencias' : None,
	'ayuda' : None,
	'podcast' : types.InlineKeyboardMarkup([[types.InlineKeyboardButton('🎧 Escuchar en Anchor', url='https://anchor.fm/buenidioma')]]),
	'blog' : types.InlineKeyboardMarkup([[types.InlineKeyboardButton('👨🏻‍💻 Visitar el blog', url='https://blogbuenidioma.blogspot.com/?m=1')]])
}

START_TEXT = '<b>¡Hola, {}! 👋 Este es el bot oficial del canal @Buen_Idioma.</b>\n\n📢 Para comunicarte con nosotros presiona uno de los comandos del «Menú».\n\n⚠️ Aquí atendemos dudas sobre el uso correcto del español actual y recibimos sugerencias para mejorar nuestro trabajo. \n\n📍 Únete al grupo @DudasBuenIdioma y plantéanos tus dudas por allá cuando quieras. No olvides la etiqueta #duda.\n\n<b>👌 Te responderemos lo antes posible. Muchas gracias.</b>'

rapid_answers_inline_results = []

@bot.message_handler(commands=['start'])
async def handle_start(message: types.Message):
	await bot.send_message(message.chat.id, START_TEXT.format(message.from_user.first_name), parse_mode='HTML')

async def send_duda(message: types.Message, text: str, command: str):
	inline_kb = types.InlineKeyboardMarkup()
	inline_kb.row(types.InlineKeyboardButton('⤷ 0', callback_data=f'fwd_{message.chat.id}_{message.id}'), types.InlineKeyboardButton('☑️', callback_data=f'check'))
	inline_kb.row(types.InlineKeyboardButton('Respuesta Rápida', switch_inline_query_current_chat=''))
	ans_text = f'<a href="tg://user?id={message.from_user.id}" >{message.from_user.first_name}</a> | #{command}\n\n{text}'
	await bot.send_message(answerer_id, ans_text, reply_markup=inline_kb, parse_mode='HTML')
	await bot.send_message(message.from_user.id, USER_FEEDBACK[command])

@bot.message_handler(commands=[x for x in COMMANDS_TEXT])
async def handle_commands(message: types.Message):
	splitted = message.text[1:].split(' ', 1)
	command = splitted[0]
	if command in ['duda', 'sugerencias'] and len(splitted) > 1:
		await send_duda(message, splitted[1], command)
	else:
		await bot.send_message(message.chat.id, COMMANDS_TEXT[command], parse_mode='HTML', reply_markup=COMMANDS_MARKUP[command])

@bot.message_handler(chat_types=['private'])
async def handle_messages(message : types.Message):
	if message.from_user.id != answerer_id:
		for hashtag in ['duda', 'sugerencias']:
			if f'#{hashtag}' in message.text:
				await send_duda(message, message.text, hashtag)
	elif message.reply_to_message:
		original = message.reply_to_message
		if original.reply_markup:
			inline_kb = original.reply_markup.keyboard
			for row in inline_kb:
				for button in row:
					if button.callback_data and button.callback_data.startswith('fwd'):
						splitted = button.callback_data.split('_')
						chat_id = splitted[1]
						message_id = splitted[2]
						await bot.send_message(chat_id, message.text, reply_to_message_id=message_id)
						count = int(button.text[1:])
						button.text = f'⤷ {count + 1}'
			await bot.edit_message_reply_markup(original.chat.id, original.id, reply_markup=types.InlineKeyboardMarkup(inline_kb))

@bot.callback_query_handler(lambda q: q.data.startswith('fwd'))
async def handle_fwd_callback(q : types.CallbackQuery):
	await bot.answer_callback_query(q.id, 'To answer this query reply to the message.', cache_time=300)

@bot.callback_query_handler(lambda q: q.data == 'check' or q.data == 'uncheck')
async def handle_check_uncheck_callback(q : types.CallbackQuery):
	inline_kb = q.message.reply_markup.keyboard
	for row in inline_kb:
				for button in row:
					if button.callback_data == 'check' or button.callback_data == 'uncheck':
						button.text = '✅' if button.callback_data == 'check' else '☑️'
						button.callback_data = 'uncheck' if button.callback_data == 'check' else 'check'

	await bot.edit_message_reply_markup(q.message.chat.id, q.message.id, reply_markup=types.InlineKeyboardMarkup(inline_kb))

@bot.inline_handler(lambda q: True)
async def hanlde_inline(q: types.InlineQuery):
	if (q.from_user.id == answerer_id):
		await bot.answer_inline_query(q.id, rapid_answers_inline_results, cache_time=0, is_personal=True)
	else:
		await bot.answer_inline_query(q.id, [], switch_pm_parameter='_', switch_pm_text='Preguntar a través del bot.')

if __name__ == '__main__':
	for i, answer in enumerate(rapid_answers):
		rapid_answers_inline_results.append(types.InlineQueryResultArticle(f'{i}', answer['title'], input_message_content=types.InputTextMessageContent(answer['text']), description=answer['text']))
	
	asyncio.run(bot.infinity_polling())