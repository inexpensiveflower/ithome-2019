# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import ithome_crawler.items as items

# 想對爬到的資料做操作可以透過 XXXXXCrawlerPipeline class 來完成
class IthomeCrawlerPipeline:
    def process_item(self, item, spider):
    	if type(item) is items.IthomeArticleItem:
    		if item['view_count'] < 150:
    			raise DropItem(f'[{item["title"]}] 瀏覽數小於 150')
    	return item

import pymongo

class AbstractMongoPipeline(object):
	collection_name = 'None'

	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]
		self.collection = self.db[self.collection_name]

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			mongo_uri = crawler.settings.get('MONGO_URI'),
			mongo_db = crawler.settings.get('MONGO_DATABASE')
		)

	def close_spider(self, spider):
		self.client.close()


class IthomeArticlePipeline(AbstractMongoPipeline):
	
	collection_name = 'article'

	def process_item(self, item, spider):
		if type(item) is items.IthomeArticleItem:
			document = self.collection.find_one({'url': item['url']})

			if not document:
				insert_result = self.collection.insert_one(dict(item))
				item['_id'] = insert_result.inserted_id
			else:
				self.collection.update_one(
					{'_id': document['_id']},
					{'$set': dict(item)},
					upsert=True
				)

				item['_id'] = document['_id']
		return item

class IthomeReplyPipeline(AbstractMongoPipeline):

	collection_name = 'response'

	def process_item(self, item, spider):
		if type(item) is items.IthomeReplyItem:
			document = self.collection.find_one({'_id':item['_id']})

			if not document:
				self.collection.insert_one(dict(item))
			else:
				del item['_id']
				self.collection.update_one(
					{'_id':document['_id']},
					{'$set':dict(item)},
					upsert = True
				)
		return item