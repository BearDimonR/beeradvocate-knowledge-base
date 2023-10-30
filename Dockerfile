FROM python:3.9

WORKDIR /app

COPY . .

RUN pip3 install py2neo pandas beautifulsoup4 tqdm

ENV DOTENV_PATH .env

CMD ["python", "app.py"]
