FROM python:3.12

WORKDIR /code/worker

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
