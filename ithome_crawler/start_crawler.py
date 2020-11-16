# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings

# '''
# get_project_settings() 方法會取得爬蟲專案中的 settings.py 檔案設定
# 啟動爬蟲前要提供這些設定給 Scrapy Engine
# '''
# process = CrawlerProcess(get_project_settings())

# process.crawl('ithome')
# process.start()

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

'''
get_project_settings() 方法會取得爬蟲專案中的 settings.py 檔案設定
啟動爬蟲前要提供這些設定給 Scrapy Engine
'''
runner = CrawlerRunner(get_project_settings())

d = runner.crawl('ithome')
d.addBoth(lambda _: reactor.stop())
reactor.run()