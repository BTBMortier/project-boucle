FROM python:3
RUN apt-get update && \
      apt-get -y install sudo

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo
USER docker
CMD /bin/bash

RUN sudo apt update ; sudo apt upgrade -y
RUN sudo apt install mongodb -y
RUN sudo apt install postgresql postgresql-contrib -y

RUN sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'password'"

RUN pip install apache-airflow
RUN pip install pyspark 

WORKDIR /usr/src/app
COPY . .
WORKDIR ./project-boucle/boucled/boucled/spiders
#Ports to forward 
#PSQL 5432
#MongoDB 27017
#Airflow web 8080
