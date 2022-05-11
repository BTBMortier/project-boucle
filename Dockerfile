FROM python:3
CMD /bin/bash

RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN apt-get update && apt-get install -y \
	mongodb \
	postgresql \
	postgresql-contrib \

RUN pip install apache-airflow
RUN pip install pyspark 

WORKDIR /usr/src/app
COPY . .

WORKDIR ./project-boucle
RUN ./change_psql_password.sh password
WORKDIR ./project-boucle/boucled/boucled/spiders

#Ports to forward 
#PSQL 5432
#MongoDB 27017
#Airflow web 8080
