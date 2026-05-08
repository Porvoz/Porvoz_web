FROM python:3.11-slim

WORKDIR /app

COPY porvoz/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

RUN python porvoz/manage.py collectstatic --noinput --settings=config.settings.production || true

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--chdir", "porvoz"]
