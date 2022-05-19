import re
import os
import json
import base64
import scrapy
import shutil
from datetime import datetime
from urllib.parse import urljoin

#//TODO Appels BDD posts                
#//TODO update entree bdd topic avec timestamp op
#//TODO update entree bdd topic avec lsp 
#//TODO reprise scraping lsp
#//TODO scraping multipage



class PostsSpider(scrapy.Spider):
    name = 'long_posts'
    allowed_domains = ['www.jeuxvideo.com']
    start_urls = []

    f = open("long_topics.jl","r")
    for l in f:
        if json.loads(l)["topic"] not in start_urls:
            start_urls.append(json.loads(l)["topic"])
    f.close()
    custom_settings = {'CONCURRENT_REQUESTS' : 64,
                        'CONCURRENT_REQUESTS_PER_DOMAIN': 64}
    
    def __init__(self):
        now = datetime.now()
        file_timestamp = now.strftime("%d-%m-%Y_%H%M%S")
        in_path = os.path.abspath("topics.jl")
        out_path = os.path.abspath(f"out/topics/topics_{file_timestamp}.jl")
        shutil.copy(in_path, out_path)

        

    def parse(self, response):
        if response.status == 410:
            yield None

        posts = response.xpath("//div[@class='bloc-message-forum mx-2 mx-lg-0 ']")
        curr_page   = int(response.xpath("//span[@class='page-active']/text()").extract()[0])
        page_links  = response.xpath("//div[@class='bloc-liste-num-page']")[0]
        page_links  = page_links.xpath(".//a[@class='lien-jv']")
        next_page = self.parse_next_page(page_links,curr_page)
        scraped_posts = self.parse_posts(response, posts, curr_page)
        if next_page != None:
            yield scrapy.Request(url=next_page,callback=self.parse)

    def parse_posts(self, response,  posts, curr_page):
        post_list = []
        for idx, p in enumerate(posts):
            try:
                bloc_header = p.xpath(".//div[@class='bloc-header']")
                bloc_date_msg = bloc_header.xpath(".//div[@class='bloc-date-msg']")
                bloc_contenu  = p.xpath(".//div[@class='bloc-contenu']")

                text_post = bloc_contenu.xpath(".//div[@class='txt-msg  text-enrichi-forum ']")
                text_post = " ".join([p.extract() for p in text_post.xpath(".//p")])
                t_id = re.compile("forums\/42-51-(\d*)")
                topic_id = t_id.search(response.request.url).group(1)

                timestamp = bloc_date_msg.xpath(".//span[@target='_blank']/text()").extract()[0]
                author  = bloc_header.xpath(".//span[@target='_blank']/text()").extract()[0].strip("\n").strip()


                post_id = p.xpath("./@data-id").extract()[0]

                text_hash = text_post.encode()
                text_hash = base64.b64encode(text_hash)
                text_hash = text_hash.decode()
                post_dict = {
                        "author":author,
                        "topic_id":topic_id,
                        "timestamp":timestamp,
                        "post_id":post_id,
                        "post_text":text_post,
                        "text_hash":text_hash,
                        "page":curr_page}
                post_list.append(post_dict)
            except:
                continue

        now = datetime.now()
        file_timestamp = now.strftime("%d-%m-%Y_%H%M%S")
        with open(f"out/posts/{topic_id}_page_{curr_page}-{file_timestamp}.jl","a+") as outfile:
            for p in post_list:
                outfile.write(str(p)+"\n")
            outfile.close()



    def parse_next_page(self, page_links,curr_page):
        for p in page_links:
            try:
                num_page = int(p.xpath("./text()").extract()[0])
            except:
                continue
            if num_page == curr_page + 1:
                next_page = p.xpath("./@href").extract()[0]
                next_page = urljoin("https://www.jeuxvideo.com",next_page)
                return next_page
        return None

    def parse_last_page(self, page_links):
        try:
            last_page = page_links[-1]
            last_page = last_page.xpath("./text()").extract()[0]
            return int(last_page)
        except:
            return None
