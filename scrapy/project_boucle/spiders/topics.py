import re
import base64
import scrapy
import logging
from pymongo import MongoClient
from urllib.parse import urljoin


#//TODO Appels BDD posts                
#//TODO update entree bdd topic avec timestamp op
#//TODO update entree bdd topic avec lsp 
#//TODO reprise scraping lsp
#//TODO scraping multipage

class TopicsSpider(scrapy.Spider):
    name = 'topics'
    allowed_domains = ['www.jeuxvideo.com']
    start_urls = ["https://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm"]

    def __init__(self):
        self.db = MongoClient('localhost', 27017)
        self.db = self.db["boucled"]
    
    def parse(self, response):
        topics   = response.xpath("//li[@class='']")
        grn_pin = "icon-topic-pin topic-pin-on topic-img"
        red_pin = "icon-topic-pin topic-pin-off topic-img"
        for t in topics:
            icon = t.xpath(".//i/@class").extract()[0]
            if (icon != red_pin) and (icon != grn_pin):
                try:
                    author   = t.xpath(".//span[@target='_blank']/text()").extract()[0].strip("\n").strip()
                    topic_id = t.xpath("./@data-id").extract()[0]
                    title = t.xpath(".//a[@class='lien-jv topic-title']/@title").extract()[0]
                    topic_dict = {
                            "topic_id":topic_id,
                            "author":author,
                            "title":title,
                            "mod_title":"0"}
                except:
                    continue
                url = t.xpath(".//a[@class='lien-jv topic-title']/@href").extract()[0]
                url = urljoin("https://www.jeuxvideo.com",url)
                id_matches = int(self.db.topics.find({"topic_id":topic_id}).count())
                title_matches = int(self.db.topics.find({"title":title}).count())
                mod_title_matches = int(self.db.topics.find({"new_title": { "$in":[title]}}).count())
                if id_matches == 0:
                    self.db.topics.insert(topic_dict)
                elif title_matches == 0 :
                    self.db.topics.update({"topic_id":topic_id},{"$set":{"new_title":title}})
                    self.db.topics.update({"topic_id":topic_id},{"$set":{"mod_title":"1"}})
                yield {"topic":url}







    


            

