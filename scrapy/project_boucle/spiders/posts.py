import re
import base64
import scrapy
from pymongo import MongoClient
from urllib.parse import urljoin


class PostsSpider(scrapy.Spider):
    name = 'posts'
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

                yield scrapy.Request(url=url, callback=self.parse_posts)

    def parse_posts(self, response):
        posts = response.xpath("//div[@class='bloc-message-forum mx-2 mx-lg-0 ']")
        curr_page   = int(response.xpath("//span[@class='page-active']/text()").extract()[0])
        page_links  = response.xpath("//div[@class='bloc-liste-num-page']")
        for p in page_links:
            try:
                page = page_links.xpath(".//a[@class='lien-jv']")
                num_page = int(page_links.xpath("./text()"))
                print(num_page)
                if num_page == curr_page + 1:
                    next_page = page.xpath("./@href")
                    next_page = urljoin("https://www.jeuxvideo.com", next_page)
                    print(next_page)
            except:
                pass
        try:
            last_page = list(page_links)[-1]
            last_page = int(last_page.xpath(".//a[@class='lien-jv']/text()").extract()[0])
        except:
            pass
        
        t_id = re.compile("forums\/42-51-(\d*)")
        topic_id = t_id.search(response.request.url).group(1)
        try:
            if curr_page == last_page:
                lsp = urljoin("https://www.jeuxvideo.com",response.request.url)
                self.db.topics.update({"topic_id":topic_id},{"lsp":lsp})
        except:
            pass
        
        for idx, p in enumerate(posts):
            try:
                bloc_header = p.xpath(".//div[@class='bloc-header']")
                bloc_date_msg = bloc_header.xpath(".//div[@class='bloc-date-msg']")
                bloc_contenu  = p.xpath(".//div[@class='bloc-contenu']")

                text_post = bloc_contenu.xpath(".//div[@class='txt-msg  text-enrichi-forum ']")
                text_post = " ".join([p.extract() for p in text_post.xpath(".//p")])

                timestamp = bloc_date_msg.xpath(".//span[@target='_blank']/text()").extract()[0]
                author  = bloc_header.xpath(".//span[@target='_blank']/text()").extract()[0].strip("\n").strip()

                
                post_id = p.xpath("./preceding-sibling::span")
                post_id = post_id.xpath("./@id").extract()[0]

                text_hash = text_post.encode()
                text_hash = base64.b64encode(text_hash)
                text_hash = text_hash.decode()
                post_dict = {
                        "author":author,
                        "topic_id":topic_id,
                        "timestamp":timestamp,
                        "post_id":post_id,
                        "text_post":text_post,
                        "text_hash":text_hash,
                        "page":curr_page}
            except:
                continue
            post_id_match = int(self.db.posts.find({"post_id":post_id}).count())
            text_hash_match = int(self.db.posts.find({"text_hash":text_hash}).count())
            if (curr_page == 1) and (idx == 0):
                try:
                    self.db.topics.update({"topic_id":topic_id},{"$set":{"timestamp":timestamp}})
                except:
                    pass
            if post_id_match == 0:
                self.db.posts.insert(post_dict)
            elif text_hash_match == 0:
                self.db.posts.update({"post_id":post_id},{"$set":{"new_text":text_post}})
                self.db.posts.update({"post_id":post_id},{"$set":{"new_text_hash":text_hash}})
            
        try:
            yield scrapy.Request(url=next_page, callback=self.parse_posts)
        except:
            pass


            
#//TODO Appels BDD posts                
#//TODO update entree bdd topic avec timestamp op
#//TODO update entree bdd topic avec lsp 
#//TODO reprise scraping lsp

