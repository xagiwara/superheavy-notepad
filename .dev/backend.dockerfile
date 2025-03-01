FROM python:3.13-slim AS requirements

WORKDIR /app

ADD Pipfile /app/Pipfile
ADD Pipfile.lock /app/Pipfile.lock

RUN pip install pipenv \
 && pipenv requirements > /app/requirements.txt

FROM python:3.13-slim AS packages

COPY --from=requirements /app/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY --from=packages /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

WORKDIR /app/backend

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
