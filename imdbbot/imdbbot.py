from pyrogram import Client,filters
from pyrogram.types import (InlineQueryResultArticle, 
                            InputTextMessageContent,
			    InlineKeyboardMarkup, 
                            InlineKeyboardButton
)
import pyrogram
import sys
import imdbsearch


token = "api_token"

app = Client("ImdbBot",
		bot_token=token,
)


genre_emoji = {
	'Animation':'🐵',
	'Adventure':'🏂',
	'Comedy':'😹',
	'Music': '🎵',
	'Family':'👨‍👩‍👦',
	'Sci-Fi':'🤖',
	'Horror':'👻',
	'Romance':'🥰',
	'Action':'🦾',
	'Drama':'🎭',
	'Fantasy':'✨',
	'Crime':'🔪'
}

@app.on_message(filters.command(["start"]))
async def start(client, message):
	await message.reply_text(f"Hello {message.from_user.mention}🤘, search any movie title from IMDB\n\n write for @J04oPaulo",
		reply_to_message_id=message.message_id,
		reply_markup=InlineKeyboardMarkup(
					[
						[InlineKeyboardButton(
							f"lets go search",
							switch_inline_query_current_chat=' '
						)]
					]
		)
	)

IMDB = imdbsearch.IMDB()

@app.on_callback_query(filters.regex('INFO-|.+'))
async def play_video_callback(client, callback_query):
	data = callback_query.data
	url = data.replace("INFO-|","https://www.imdb.com")
	info = IMDB.info(url)
	
	await callback_query.answer('wait...',
		cache_time=3
	)
	date = f"({info.date.year})" if info.date else ""
	rating = f"⭐️ {info.rating.value}" if info.rating.value else ''
	await client.edit_inline_text(callback_query.inline_message_id,
				f"<a href='{info.image}'> </a><b>{info.name+date}</b> {rating} <a href='{url}'>IMDB</a>\n\n"+
				f"<b>Actors</b>: {', '.join([actor['name']for actor in info.actor])}\n\n"
				f"<b>Genre</b>:</a> {', '.join([genre_emoji.get(genre,'')+genre for genre in info.genre])}"+'\n'
				f"{info.description}"+'\n',
				reply_markup=InlineKeyboardMarkup(
					[
						[InlineKeyboardButton(
							f"▶️ Trailer" if info.trailer else f"{info.name}",
							url="https://www.imdb.com"+info.trailer['embedUrl'] if info.trailer else url
						)]
					]
				)
	)

@app.on_chosen_inline_result()
def on_chosen_inline_result(client, on_chosen):
	print(on_chosen)
	pass


@app.on_inline_query()
async def inlinequery_play(client, inline_query):
	res_imdb = IMDB.search(inline_query.query)
	
	if inline_query.offset == '':
		range_ = range(0, 50)
		next_offset = '50'
	else:
		offset_atual = int(inline_query.offset)
		range_ = range(offset_atual, offset_atual+50)
		next_offset = f'{((offset_atual+50))}'

	results = []
	
	for todo in range_:
		try:
			movie = res_imdb[todo]
		except IndexError:
			next_offset = ''
			break

		results.append(
			InlineQueryResultArticle(
				title=movie.title,
				input_message_content=InputTextMessageContent(
					f"<a href='{movie.url}'>{movie.title.title()}</a>"
				),
				description=f"click here fo see {movie.title}",
				thumb_url="https://i.imgur.com/JyxrStE.png",
				reply_markup=InlineKeyboardMarkup(
					[
						[InlineKeyboardButton(
							f"{movie.title} click here",
							callback_data=f"INFO-|{movie.url}"
						)]
					]
				)
			)
		)
		
	
	r = await inline_query.answer(
		results,
		next_offset=next_offset,
		cache_time=1,
		switch_pm_text='help',
		switch_pm_parameter='help'
	)
	
app.run()
