FROM python:3.11
WORKDIR /app
COPY . /app
RUN python -m pip install -r requirements.txt 

CMD [ "python","m_mongo_updater.py" ]