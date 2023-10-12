FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install poetry

COPY pyproject.toml /app/
COPY poetry.lock /app/

RUN cd /app && poetry install

WORKDIR / app

COPY mysite .

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
