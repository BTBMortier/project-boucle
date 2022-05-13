# project-boucle

_'La boucle est un terme conceptuel désignant la manière dont un forum tend à toujours traiter des mêmes sujets en boucle. Ce concept est particulièrement employé sur le 18-25'._

Source : https://jvflux.fr/Boucle

Le projet boucle a pour but de constituer une archive des posts(messages) et topics(sujets) du forum blabla 18-25 ans de jeuxvideo.com assez exhaustive pour pouvoir à terme alimenter un algorithme de Topic Analysis (classification de sujets) permettant de détecter les topics de la boucle.

Sous sa forme actuelle c'est une suite de spiders scrapy et la pipeline d'ETL qui va avec pour appuyer mes candidatures d'alternance (Data Engineer ou Data Analyst Big Data/Spark)

Vous trouverez le diagramme de la pipeline ci-dessous:


![boucled](https://user-images.githubusercontent.com/19901661/156818063-241ba9c3-ce63-4d53-af9c-0fa9673c1c0f.png)

//TODO

Scraping user info

Nettoyage topics

Nettoyage user

Chargement données => PostgreSQL

Dockerizer l'application

Désimplémenter le hashage des posts
