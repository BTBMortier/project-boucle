FROM python:3
WORKDIR /usr/src/app
RUN sudo apt update ; sudo apt upgrade -y
RUN sudo apt install mongodb -y
RUN sudo apt install postgresql postgresql-contrib -y
RUN git clone https://github.com/BTBMortier/project-boucle 
WORKDIR ./project-boucle/boucled/boucled/spiders
