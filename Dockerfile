FROM apache/airflow:latest

WORKDIR /usr/src/app
COPY ./. /usr/src/app/

#Ajout des clés et dépots du paquet MongoDB
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

#Installation des dépendances python
RUN pip install -r requirements.txt
RUN python3 ./src/boucled_db/mongodb.py
RUN python3 ./src/boucled_db/postres.py

#Préparation des dossiers et création des fichiers temporaires des spiders
WORKDIR ./project-boucle/src/boucled_scrapers/spiders
RUN touch topics.jl
RUN touch long_topics.jl
RUN mkdir -p out/posts/processed
RUN mkdir -p out/topics/processed

#Expostion des ports
EXPOSE 5432 5442
EXPOSE 8080 8090
EXPOSE 27017 28017
