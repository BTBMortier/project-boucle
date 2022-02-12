import scrapy


class PostsSpider(scrapy.Spider):
    name = 'posts'
    allowed_domains = ['https://www.jeuxvideo.com']
    start_urls = ['https://www.jeuxvideo.com/forums/42-51-68970057-1-0-1-0-ca-y-est-j-ai-25-ans.htm']

    def parse(self, response):
        results = []
        posts = response.xpath("//div[@class='inner-head-content']")
        for p in posts:
            bloc_header = p.xpath(".//div[@class='bloc-header']")
            bloc_date_msg = bloc_header.xpath(".//div[@class='bloc-date-msg']")
            bloc_contenu  = p.xpath(".//div[@class='bloc-contenu']")
            
            texte_post = bloc_contenu.xpath(".//div[@class='txt-msg  text-enrichi-forum ']")
            texte_post = [p.extract() for p in texte_post.xpath(".//p") ]            
            timestamp = bloc_date_msg.xpath(".//span[@target='_blank']/text()").extract()
            auteur = bloc_header.xpath(".//span[@target='_blank']/text()").extract()
            post_dict = {"auteur": auteur,"timestamp": timestamp,"texte_post": texte_post}
            yield results



