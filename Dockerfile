FROM python:3-buster

WORKDIR /usr/src/app

COPY src/requirements.txt ./
COPY commands.sh ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src/indeed .
COPY src/linkedin .

EXPOSE 8000 8080

CMD ["./commands.sh"]