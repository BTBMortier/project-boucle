FROM python:3

RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
EXPOSE 27017 28017

RUN apt-get update && apt-get install -y \
	mongodb-org \
	postgresql \
	postgresql-contrib 

RUN pip install apache-airflow
RUN pip install pyspark 

WORKDIR /usr/src/app
COPY project-boucle/ .

WORKDIR ./project-boucle
RUN ls -l
RUN ./change_psql_password.sh password
WORKDIR ./project-boucle/boucled/boucled/spiders

#Ports to forward 
#PSQL 5432
#Airflow web 8080

#Exposed ports
#MongoDB 28017
