# project-boucle

//TODO

Désimplémenter le hashage des posts

_'La boucle est un terme conceptuel désignant la manière dont un forum tend à toujours traiter des mêmes sujets en boucle. Ce concept est particulièrement employé sur le 18-25'._

Source : https://jvflux.fr/Boucle

Le projet boucle a pour but de constituer une archive des posts(messages) et topics(sujets) du forum blabla 18-25 ans de jeuxvideo.com assez exhaustive pour pouvoir à terme alimenter un algorithme de Topic Analysis (classification de sujets) permettant de détecter les topics de la boucle.

Sous sa forme actuelle c'est une suite de spiders scrapy et la pipeline d'ETL qui va avec pour appuyer mes candidatures d'alternance (Data Engineer ou Data Analyst Big Data/Spark)

(Si vous êtes recruteur/Tech Lead continuez à scroller)

Vous trouverez le diagramme de la pipeline ci-dessous:


![boucled](https://user-images.githubusercontent.com/19901661/156818063-241ba9c3-ce63-4d53-af9c-0fa9673c1c0f.png)

En ce qui concerne le code en lui même, tout commence avec le Dockerfile:
```
FROM apache/airflow:latest

COPY ./. /usr/src/app/
COPY ./pipeline/dags/. /opt/airflow/dags/


#Ajout des cl\u00e9s et d\u00e9pots du paquet MongoDB
RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list

#Installation de MongoDB et PostgreSQL
RUN apt-get update && apt-get install -y \
	mongodb-org \
	postgresql \
	postgresql-contrib 

#Demarrage de PostgreSQL et changement du mot de passe
RUN su -c 'pg_ctlcluster 13 main start' postgres
RUN su -c 'service postgresql restart' postgres
RUN su -c './src/boucled_db/change_psql_password.sh password' postgres

#Installation des d\u00e9pendances python
RUN pip install -r requirements.txt
RUN python3 ./pipeline/boucled_db/mongodb.py
RUN python3 ./pipeline/boucled_db/postres.py

#Pr\u00e9paration des dossiers et cr\u00e9ation des fichiers temporaires des spiders
WORKDIR /usr/src/app/project-boucle/pipeline/boucled_scrapers/spiders
RUN touch topics.jl
RUN touch long_topics.jl
RUN mkdir -p out/posts/processed
RUN mkdir -p out/topics/processed

#Expostion des ports
EXPOSE 5432 5442
EXPOSE 8080 8090
EXPOSE 27017 28017
```
Ici, rien de bien particulier, j'installes les dépendances , démarre le service Postgres et exposes les ports nécessaires pour pouvoir accéder à mes BDD de l'exterieur du container.

# EXTRACTION
# 1) Extraction des topics
J'ai choisi d'utiliser scrapy.

Avant toute chose mon spider commence par initier une connection avec une MongoDB(archivage d'HTML brut pour faciliter une consultation web qui sera implémentée ultérieurement)

```
    def __init__(self):
        self.db = MongoClient('localhost', 27017)
        self.db = self.db["boucled"]
```

Puis pour le scraping des topics en lui-même, après avoir parsé les éléments correspondants aux topics je définis dans une variable la valeur d'attribut de la balise d'icone des topics épinglès afin de les discriminer du reste qui m'intéresse:

```
        topics   = response.xpath("//li[@class='']")
        grn_pin = "icon-topic-pin topic-pin-on topic-img"
        red_pin = "icon-topic-pin topic-pin-off topic-img"
```
 
 Puis je récupére et compile dans un dictionnaire ce j'ai extrait: 
 
 ```
         for t in topics:
            icon = t.xpath(".//i/@class").extract()[0]
            if (icon != red_pin) and (icon != grn_pin):
                try:
                    author   = t.xpath(".//span[@target='_blank']/text()").extract()[0].strip("\n").strip()
                    topic_id = t.xpath("./@data-id").extract()[0]
                    title = t.xpath(".//a[@class='lien-jv topic-title']/@title").extract()[0]
                    n_posts = int(t.xpath(".//span[@class='topic-count']/text()").extract()[0])
                    url = t.xpath(".//a[@class='lien-jv topic-title']/@href").extract()[0]
                    url = urljoin("https://www.jeuxvideo.com",url)
                    topic_dict = {
                            "topic_id":topic_id,
                            "topic":url,
                            "author":author,
                            "title":title,
                            "mod_title":"0",
                            "n_posts":n_posts}
                except:
                    continue
```

Avant d'envoyer mes topics sur la MongoDB, je vérifie que je ne les ai déjà pas dans mes enregistrements pour:
1)Éviter les doublons
2)Détecter et enregistrer les changements de titre (pratique très courante parmis les plaisantins de jeuxvideo.com )

```
              id_matches = int(self.db.topics.find({"topic_id":topic_id}).count())
                title_matches = int(self.db.topics.find({"title":title}).count())
                mod_title_matches = int(self.db.topics.find({"new_title": { "$in":[title]}}).count())
                if id_matches == 0:
                    self.db.topics.insert(topic_dict)
                elif title_matches == 0 :
                    self.db.topics.update({"topic_id":topic_id},{"$set":{"new_title":title}})
                    self.db.topics.update({"topic_id":topic_id},{"$set":{"mod_title":"1"}})
                    
```

Enfin pour éviter que mon scrapers de posts tourne pendant 1h, je discrimines les topics à + de 1000 posts qui sont enregistrés dans un fichier séparé:

```
                f = open("long_topics.jl","w+")
                if topic_dict["n_posts"] < 1000:
                    yield json.loads(json.dumps(topic_dict, default=str))
                else:
                    f.write(json.dumps(topic_dict, default=str))

```

Note: Le scraper étant lancé avec la commande ```scrapy crawl topics -O topics.jl```, les topics de moins de 1000 posts sont enregistrés dans topics.jl

# 2) Extraction des posts

Cette fois ci avant d'initier la connection à la BDD , je dois d'abord:

1)Récupérer les URL des topics à scraper dans topics.jl

```
    name = 'posts'
    allowed_domains = ['www.jeuxvideo.com']
    f = open("topics.jl","r")
    start_urls = [json.loads(url)["topic"] for url in f if json.loads(url)["n_posts"] < 1000 ]
    topic_list = f.readlines()
    f.close()
    custom_settings = {
            'CONCURRENT_REQUESTS' : 30,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 30}
```
Et j'en profites aussi pour définir des paramètres personalisés à la spider pour assurer un scraping relativement rapide

2)Faire une copie de topics.jl et l'enregistrer dans la zone de travail de mes scripts d'ETL

```
      now = datetime.now()
        file_timestamp = now.strftime("%d-%m-%Y_%H%M%S")
        in_path = os.path.abspath("topics.jl")
        out_path = os.path.abspath(f"out/topics/topics_{file_timestamp}.json")
        shutil.copy(in_path, out_path)
```
3)Puis j'initie enfin ma connection

```
       self.db = MongoClient('localhost', 27017)
       self.db = self.db["boucled"]
```


En ce qui concerne le scraping en lui même:

Je renvoie un résultat nul si je reçois du serveur du forum un code 410 (topic supprimé)

```
    if response.status == 410:
            yield None
```

Je parse les éléments des posts et les URL de pages pour pouvoir directement détecter la page suivante 

```
        posts = response.xpath("//div[@class='bloc-message-forum mx-2 mx-lg-0 ']")
        curr_page   = int(response.xpath("//span[@class='page-active']/text()").extract()[0])
        page_links  = response.xpath("//div[@class='bloc-liste-num-page']")[0]
        page_links  = page_links.xpath(".//a[@class='lien-jv']")
        next_page = self.parse_next_page(page_links,curr_page)
        scraped_posts = self.parse_posts(response, posts, curr_page)
        if next_page != None:
            yield scrapy.Request(url=next_page,callback=self.parse)
```

Et selon le même principe que les posts, je parse , compile en dictionnaire, enregistre dans MongoDB puis dans le disque mes posts

```
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

        now = datetime.now()
        file_timestamp = now.strftime("%d-%m-%Y_%H%M%S")
        with open(f"out/posts/{topic_id}_page_{curr_page}-{file_timestamp}.json","a+") as outfile:
            for p in post_list:
                p = json.dumps(p,default=str)
                outfile.write(p+"\n")
            outfile.close()
```

Note: L'enregistrement des hashs et toutes les actions qui y sont liés seront désimplémentées à l'avenir dans un souci de conservation d'espace de stockage.

A titre indicatif: la fonction qui initie le scraping de la page n+1 :

```
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
```








 



