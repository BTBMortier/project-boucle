FROM python:3
CMD /bin/bash

RUN apt-get update && apt-get install -y \
	mongodb \
	postgresql \
	postgresql-contrib \
RUN psql -c "ALTER USER postgres WITH PASSWORD 'password'"

RUN pip install apache-airflow
RUN pip install pyspark 

WORKDIR /usr/src/app
COPY . .
WORKDIR ./project-boucle/boucled/boucled/spiders
#Ports to forward 
#PSQL 5432
#MongoDB 27017
#Airflow web 8080
