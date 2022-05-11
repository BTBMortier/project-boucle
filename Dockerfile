FROM python:3

WORKDIR /usr/src/app
COPY ./ /usr/src/app/

RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list

RUN apt-get update && apt-get install -y \
	mongodb-org \
	postgresql \
	postgresql-contrib 

RUN pg_ctlcluster 13 main start
RUN service postgresql restart
RUN ./change_psql_password.sh password

RUN pip install apache-airflow
RUN pip install pyspark 


WORKDIR ./project-boucle/boucled/boucled/spiders

EXPOSE 5432 5442
EXPOSE 8080 8090
EXPOSE 27017 28017
#Ports to forward 
#PSQL 5432
#Airflow web 8080

#Exposed ports
#MongoDB 28017
