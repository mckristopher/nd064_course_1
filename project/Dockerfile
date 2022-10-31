FROM python:3.8
LABEL maintainer="Mercy Christopher"

COPY ./techtrends /techtrends
WORKDIR /techtrends
RUN pip install -r requirements.txt

#Initialize Database
CMD [ "python", "init_db.py" ]

EXPOSE 3111

# command to run on container start
CMD [ "python", "app.py" ]