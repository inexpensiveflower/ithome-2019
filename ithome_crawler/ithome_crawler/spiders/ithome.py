import scrapy
from datetime import datetime
import re
import time
import ithome_crawler.items as items

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_selenium import SeleniumRequest


class IthomeSpider(scrapy.Spider):
    name = 'ithome'
    allowed_domains = ['ithome.com.tw']

    def start_requests(self):
    	for page in range(1, 3):
    		yield scrapy.Request(url = f'https://ithelp.ithome.com.tw/articles?tab=tech&page={page}', callback = self.parse)
    		# time.sleep(10)
    		# yield SeleniumRequest(url=f'https://ithelp.ithome.com.tw/articles?tab=tech&page={page}', callback=self.parse)
    

    def parse(self, response):
    	# 先找到每篇文章的區塊
    	article_tags = response.css('div.qa-list')

    	# 如果有文章才繼續進行爬蟲
    	if len(article_tags) > 0:
    		for article_tag in article_tags:
    			title_tag = article_tag.css('a.qa-list__title-link')
    			article_url = title_tag.css('::attr(href)').get().strip()

    			# print('文章 url : ', article_url)

    			# 用了 response.follow() 方法來取得文章的請求
    			# 同時指定使用 parse_article(response) 發訪來處理文章的回應。
    			yield response.follow(article_url, callback = self.parse_article)

    def parse_article(self, response):

    	leftside = response.css('div.leftside')
    	post_side = leftside.css('div.qa-panel')
    	post_header = post_side.css('div.qa-header')
    	original_article = post_side.css('div.qa-markdown')
    	

    	# 標題
    	article_title = post_header.css('h2.qa-header__title::text').get().strip()
    	#print('文章標題 : ', article_title)

    	# 作者
    	post_info = post_header.css('div.qa-header__info, div.ir-article-info__content')
    	article_author = post_info.css('a.qa-header__info-person, a.ir-article-info__name').css('::text').getall()
    	article_author = (' '.join(article_author)).strip()
    	#print('作者 : ', article_author)


    	# 瀏覽人數
    	article_views = post_info.css('span.qa-header__info-view, div.ir-article-info__view').css('::text').get()
    	views_int = int(re.search('(\d+).*', article_views).group(1))
    	#print('瀏覽人數 : ', views_int)
    	

    	# 發文時間
    	article_time = post_info.css('a.qa-header__info-time, ir-article-info__time').css('::text').get()
    	#print('發文時間 : ', datetime.strptime(article_time, '%Y-%m-%d %H:%M:%S'))
    	

    	# 內容
    	article_content = ' '.join(original_article.css('div.markdown__style').css('::text').extract())
    	#print('文章內容 : ', article_content)
    	

    	# 標籤
    	article_tags = post_header.css('div.qa-header__tagGroup').css('a.qa-header__tagList').css('::text').getall()
    	#print('標籤 : ', article_tags)
    	#print('\n')

    	# 這邊會把資料 parse 給 items 物件
    	# pipelines 會判斷如果 items 物件有接收到東西就把他存進去 DB
    	article = items.IthomeArticleItem()
    	article['url'] = response.url
    	article['title'] = article_title
    	article['author'] = article_author
    	article['publish_time'] = article_time
    	article['tags'] = ''.join(article_tags)
    	article['content'] = article_content
    	article['view_count'] = views_int

    	yield article

    	# 程式執行到這邊的時候資料已經被存進去 DB 了，所以可以直接去拿 DB 裡面的資料
    	# _id 是在 DB 裡面的 id 資料欄位

    	if '_id' in article:
    		article_id = article['_id']
    		# print("文章IDDDDDDDDDDDDDD", article_id)

    	# 因為文章的回覆跟文章的內容在同一個頁面
    	# 所以不需要再送一次 requests 給瀏覽起了
    	# 直接承接著本來的 response 繼續用就好
    	# 不然本來應該是要用 yield response.follow() 才對
    	yield from self.parse_reply(response, article_id)


    def parse_reply(self, response, article_id):

    	leftside = response.css('div.leftside')
    	replies = leftside.css('div.response')

    	if len(replies) > 0:
    		for reply in replies:

	    		reply_panel = reply.css('div.qa-panel__content')
	    		reply_header = reply_panel.css('div.response-header__info')

	    		reply_item = items.IthomeReplyItem()
	    		reply_item['article_id'] = article_id

	    		# 回文者的 ID
	    		# <a name = "response-xxxxxx"></a>
	    		reply_item['_id'] = int(reply.css('a::attr(name)').get().replace('response-', ''))
	    		
	    		# 回文者的名稱
	    		reply_item['author'] = reply_header.css('a.response-header__person').css('::text').get()
	    		
	    		# 回文時間
	    		reply_time = reply_header.css('a.ans-header__time').css('::text').get().strip()
	    		reply_time = datetime.strptime(reply_time, '%Y-%m-%d %H:%M:%S')
	    		reply_item['publish_time'] = reply_time
	    		
	    		# 回文內容
	    		content_site = reply.css('div.response-markdown')
	    		reply_content = ' '.join(content_site.css('div.markdown__style').css('::text').getall())
	    		reply_item['content'] = reply_content

	    		yield reply_item

    	



    	

