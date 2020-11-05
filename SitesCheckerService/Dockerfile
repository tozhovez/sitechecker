FROM python:3.7.4-slim

ARG LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --assume-yes apt-utils
RUN apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    gcc \
    zip \
    unzip \
    git-core && \
    pip install --upgrade pip

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

ARG BUILD_VERSION
ENV VERSION=$BUILD_VERSION

COPY . /app
WORKDIR /app

CMD ["python", "./main.py"]
