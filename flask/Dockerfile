FROM ubuntu:16.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y time
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install requests
RUN pip3 install flask
RUN pip3 install flask_wtf
RUN pip3 install wtforms
RUN pip3 install wtforms-validators
RUN pip3 install flask_bootstrap
RUN pip3 install pymongo
RUN pip3 install Flask-Pymongo
WORKDIR /app
COPY . /app
ENTRYPOINT ["python3"]
CMD ["pika.py"]
