import httpx
from bs4 import BeautifulSoup
import json
import re
import httpx
import asyncio
from collections import namedtuple
from datetime import date



class GetDataIMDB:
	def __init__(self, urls):
		self.urls = urls

	async def get_async(self,url):
	    async with httpx.AsyncClient() as client:
	        return await client.get(url)


	async def launch(self):
	    resps = await asyncio.gather(*map(self.get_async, self.urls))
	    data = [resp.text for resp in resps]

classTitle = namedtuple('Title', ['title','url'])
url = 'https://www.imdb.com'
class IMDB(object):
	

	def __init__(self):
		self.word = None
		self.url = 'https://www.imdb.com'
	
	def search(self, word=None):
		# https://www.imdb.com/find?q=loki&s=tt&ref_=fn_al_tt_mr

		payload = {
				'q':word,
				's':'tt',
				'ref_':'fn_al_tt_mr',
				'view':'advanced'
		}
		resp = httpx.get(f"{self.url}/find",
			params=payload
		)
		soup = BeautifulSoup(resp.text, "html.parser")
		
		"""<div class="findSection">
		<h3 class="findSectionHeader"><a name="nm"></a>Names</h3>
		<table class="findList">
		"""
		r = []
		findsection = soup.find_all('div',{'class':'findSection'})
		
		for x in findsection:
			findlist = x.find('table',{'class':'findList'})
			name, url = findlist.find('a').text,findlist.find('a').get('href')
			# print(findlist)
		
			if name:
				r.append(classTitle(name, self.url+url))
			else:

				names = findlist.find_all('a') 
				for z in names:
					
					if z.text:
						name,url = z.text, z.get('href')
						r.append(classTitle(name, url))

		return r
	
	def info(self, url="https://www.imdb.com/title/tt9140560/?ref_=fn_tt_tt_3"):
		resp = httpx.get(url)
		soup = BeautifulSoup(resp.text, "html.parser")
		data = soup.find('script', type='application/ld+json')
		data = json.loads(data.string)

		todo = namedtuple('IMDB', ['url', 
									'name', 
									'image', 
									'description', 
									'review', 
									'rating', 
									'contentRating', 
									'genre', 
									'date', 
									'keywords', 
									'actor', 
									'creator', 
									'trailer']
		)

		AggregateRating = namedtuple('Rating', 
									['count', 
									'best',
									'wors',
									'value']
		)

		rating = data.get('aggregateRating')
		
		if rating:
			rating = AggregateRating(count=rating.get('ratingCount'),
									best=rating.get('bestRating'),
									wors=rating.get('worstRating'),
									value=rating.get('ratingValue')
			)  

		return todo(url=data.get('url'),
					name=data.get('name'),
					image=data.get('image'),
					description=data.get('description'), 
					review=data.get('review'),
					genre=data.get('genre'),
					keywords=data.get('keywords'),
					actor=data.get('actor'),
					creator=data.get('creator'),
					trailer=data.get('trailer'),
					rating=rating,
					contentRating=data.get('contentRating'),
					date=date.fromisoformat(data.get('datePublished')) if data.get('datePublished') else None
		)

if __name__ == '__main__':
	r = IMDB().search('wanda vision')[0]
	print(r)
	print(IMDB().info(url+r.url))

