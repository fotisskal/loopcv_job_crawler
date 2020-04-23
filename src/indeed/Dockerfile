FROM python:3-buster

WORKDIR /usr/src/app

COPY src/requirements.txt ./
COPY commands.sh ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src/indeed .

EXPOSE 8000

CMD ["uvicorn", "indeed:app", "--port", "8000", "--reload"]