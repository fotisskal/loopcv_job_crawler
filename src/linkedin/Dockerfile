FROM python:3-buster

WORKDIR /usr/src/app

COPY src/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src/linkedin .

EXPOSE 8000

CMD ["uvicorn", "linkedin/linkedin:app", "--port", "8000", "--reload"]