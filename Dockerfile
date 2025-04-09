FROM python:3.11-slim

WORKDIR /project
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY app /project/app
COPY alembic /project/alembic
COPY alembic.ini /project/alembic.ini
COPY .env /project/.env
# RUN alembic upgrade head

ENV PYTHONUNBUFFERED=1

EXPOSE 8005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]