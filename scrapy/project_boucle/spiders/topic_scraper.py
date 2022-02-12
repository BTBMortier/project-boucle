import requests
from bs4 import BeautifulSoup as bs



def get_topics():
    url = "https://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm"
    page = requests.get(url)
    soup = bs(page.content , 'html.parser')
    body = soup.body
    topics = body.find_all("li",class_="")
    topics = [t for t in topics if "data-id" in t.attrs]
    topics = [t for t in topics if t.contents[1].contents[1].attrs["class"][0] != "icon-topic-pin"]
    return topics

def get_topic_info(topics_obj):
    display = [] 
    for topic in topics_obj:
            tinfos  = []
            topax   = topic.a['title']
            tlink   = topic.a['href']
            auteur  = topic.span.find_next("span",target="_blank").text.strip()
            tinfos  = [topax,tlink,auteur]
            display.append(tinfos)
    return display
        
def main():
    topics = get_topics()
    display = get_topic_info(topics)
    print(display)

if __name__ == '__main__': 
    main()




 
