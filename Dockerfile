FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "\n  python manage.py migrate --noinput &&\n  python manage.py collectstatic --noinput &&\n  python manage.py runserver 0.0.0.0:8000\n"]
