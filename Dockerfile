FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

RUN mkdir -p /app/logs/

CMD ["gunicorn","--chdir", "/app/src/", "--bind", "0.0.0.0:8080", "main:app"]


