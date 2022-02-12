import scrapy


class PostsSpider(scrapy.Spider):
    name = 'posts'
    allowed_domains = ['https://www.jeuxvideo.com']
    start_urls = ['http://https://www.jeuxvideo.com/']

    def parse(self, response):
        pass
