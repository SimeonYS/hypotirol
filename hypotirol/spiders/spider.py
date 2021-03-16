import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import HypotirolItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class HypotirolSpider(scrapy.Spider):
	name = 'hypotirol'
	start_urls = ['https://www.hypotirol.com/blog/seite/1?type=1984']
	page = 2
	def parse(self, response):
		post_links = response.xpath('//div[@class="blog-entry-hypo blog-entry-icon blog-grid-item col-md-3"]//div[@class="col-6"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://www.hypotirol.com/blog/seite/{self.page}?type=1984'
		if response.xpath('//div[@class="shadow"]'):
			self.page += 1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//span[@class="blogDate d-block pb-4"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="teaser-text"]//text()|//div[@class="teaser-text"]/following-sibling::*//text() | //div[@class="blogBody p-5 pb-0"]//following-sibling::p/text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=HypotirolItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
