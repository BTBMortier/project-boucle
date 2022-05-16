FROM python:3

WORKDIR /usr/src/app
COPY ./. /usr/src/app/

RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list

RUN apt-get update && apt-get install -y \
	mongodb-org \
	postgresql \
	postgresql-contrib 

RUN su -c 'pg_ctlcluster 13 main start' postgres
RUN su -c 'service postgresql restart' postgres
RUN su -c './src/boucled_db/change_psql_password.sh' postgres

RUN pip install -r requirements.txt
RUN python3 ./src/boucled_db/mongodb.py
RUN python3 ./src/boucled_db/postres.py

WORKDIR ./project-boucle/src/boucled_scrapers/spiders
RUN mkdir out

EXPOSE 5432 5442
EXPOSE 8080 8090
EXPOSE 27017 28017
#Ports to forward 
#PSQL 5432
#Airflow web 8080

#Exposed ports
#MongoDB 28017
