# Crawl the posts and the corresponding replies

This crawler crawl the posts and coressponding replies on [iT邦幫忙](https://ithelp.ithome.com.tw/). Then storing all items it got into MongoDB.

1. Change the directory to /ithome-2019/ithome-crawler, first.

2. Please make sure that you have installed the package ```scrapy``` and ```pymongo```
 
  ```console=
  python -m pip install scrapy pymongo
  ```

3. Conduct the following commnad to run the crawler. The third parameter is the crawler name you set. 
  ```console=
  scrapy crawl ithome
  ```
