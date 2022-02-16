import base64
import scrapy
from pymongo import MongoClient
from urllib.parse import urljoin


class TopicsSpider(scrapy.Spider):
    name = 'topics'
    allowed_domains = ['www.jeuxvideo.com']
    start_urls = ['https://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm']

    def __init__(self):
        self.conn = MongoClient('localhost', 27017)
        self.conn = self.conn["boucled"]
        if self.conn.posts.find({"post_hash":"test"}).count() != 0:
            self.conn.posts.remove({"post_hash":"test"})
        self.db = MongoClient('localhost', 27017)
        self.db = self.db["boucled"]

    #//TODO jarter les topics épinglés de la réponse
    def parse(self, response):
        link_list = []
        topics_list = response.xpath("//li[@class='']")
        for t in topics_list:
            title = t.xpath(".//a[@class='lien-jv topic-title']/@title").extract()[0]
            title_hash = title.encode()
            title_hash = base64.b64encode(title_hash)
            title_hash = title_hash.decode()
            
            t_link = t.xpath(".//a[@class='lien-jv topic-title']/@href").extract()[0]
            t_link = urljoin("https://www.jeuxvideo.com",t_link)
            author = t.xpath(".//span[@target='_blank']/text()").extract()[0].strip("\n").strip()
            
            topic_dict = {
                    "title":title,
                    "title_hash":title_hash,
                    "link":t_link,
                    "author":author}
            self.db.topics.insert(topic_dict)

            link_list.append(t_link)
        
        for url in link_list:
            yield scrapy.Request(url=url, callback=self.parse_posts)
            
    def parse_posts(self, response):
        posts = response.xpath("//div[@class='inner-head-content']")
        curr_page  = int(response.xpath("//span[@class='page-active']/text()").extract()[0])
        page_links = response.xpath("//div[@class='bloc-liste-num-page']")
        page_links = page_links.xpath(".//a[@class='lien-jv']")

        for elem in page_links:
            try:
                num_page  = elem.xpath("./text()").extract()[0]
            except:
                continue
            try:
                next_link = elem.xpath("./@href").extract()[0]
            except:
                continue
            try:
                if int(num_page) == int(curr_page) + 1:
                    next_page = urljoin("https://www.jeuxvideo.com",next_link)
                    break
            except:
                continue

        for idx, p in enumerate(posts):
            try:
                bloc_header = p.xpath(".//div[@class='bloc-header']")
                bloc_date_msg = bloc_header.xpath(".//div[@class='bloc-date-msg']")
                bloc_contenu  = p.xpath(".//div[@class='bloc-contenu']")

                texte_post = bloc_contenu.xpath(".//div[@class='txt-msg  text-enrichi-forum ']")
                texte_post = " ".join([p.extract() for p in texte_post.xpath(".//p")])

                texte_hash = texte_post.encode()
                texte_hash = base64.b64encode(texte_hash)
                texte_hash = texte_hash.decode()

                timestamp = bloc_date_msg.xpath(".//span[@target='_blank']/text()").extract()[0]
                author = bloc_header.xpath(".//span[@target='_blank']/text()").extract()[0].strip("\n").strip()

                post_dict = {
                        "page":curr_page,
                        "author": author,
                        "timestamp": timestamp,
                        "texte_post": texte_post,
                        "texte_hash":texte_hash}
                if self.db.posts.find({"texte_hash":texte_hash}).count() == 0:
                    self.db.posts.insert(post_dict)
                if (idx == 0) & (curr_page == 1):
                    self.db.topics.update({"t_link":response.request.url},{"timestamp":timestamp})

            except:
                continue
        if 'next_page' in locals():
            return scrapy.Request(url=next_page, callback=self.parse_posts)

            
