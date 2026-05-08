FROM python:3.11-slim

WORKDIR /app

COPY porvoz/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

WORKDIR /app/porvoz
RUN python manage.py migrate --settings=config.settings.production 2>/dev/null || true
RUN python manage.py collectstatic --noinput --settings=config.settings.production 2>/dev/null || true

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:10000"]
