FROM python:3-buster

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
