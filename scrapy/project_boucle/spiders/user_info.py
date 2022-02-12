import scrapy


class UserInfoSpider(scrapy.Spider):
    name = 'user_info'
    allowed_domains = ['https://www.jeuxvideo.com']
    start_urls = ['http://https://www.jeuxvideo.com/']

    def parse(self, response):
        pass
