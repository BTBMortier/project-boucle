import re
import json
import base64
import scrapy



class PostsSpider(scrapy.Spider):
    name = 'posts'
    allowed_domains = ['www.jeuxvideo.com']
    f = open("topics.jl","r")
    start_urls = [json.loads(url)["topic"] for url in f]
    f.close()
    

    def parse(self, response):
        posts = response.xpath("//div[@class='bloc-message-forum mx-2 mx-lg-0 ']")
        curr_page   = int(response.xpath("//span[@class='page-active']/text()").extract()[0])
        page_links  = response.xpath("//div[@class='bloc-liste-num-page']")[0]
        page_links  = page_links.xpath(".//a[@class='lien-jv']")


    def parse_next_page(self, page_links,curr_page):
        for p in page_links:
            num_page = int(p.xpath("./text()").extract()[0])
            if num_page == curr_page + 1:
                next_page = p.xpath("./@href")
                next_page = urljoin("https://www.jeuxvideo.com",next_page)
                return next_page
