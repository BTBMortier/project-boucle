FROM python:3
RUN apt-get update && \
      apt-get -y install sudo

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo
USER docker
CMD /bin/bash

RUN apt-get install -y mongodb postgresql postgresql-contrib  --allow-releaseinfo-change 

RUN pip install apache-airflow
RUN pip install pyspark 

WORKDIR /usr/src/app
COPY . .
WORKDIR ./project-boucle/boucled/boucled/spiders
#Ports to forward 
#PSQL 5432
#MongoDB 27017
#Airflow web 8080
