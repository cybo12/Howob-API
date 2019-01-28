FROM python:3.6.7

COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN python --version

COPY . .

CMD [ "python", "./flask/howob/app.py", "prod" ]
