FROM python:3
WORKDIR /usr/src/app
RUN sudo apt update 
RUN sudo apt install mongodb -y
RUN sudo apt install postgresql postgresql-contrib -y
RUN git clone https://github.com/BTBMortier/project-boucle 
