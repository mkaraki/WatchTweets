FROM python:3.9-bullseye

RUN apt-get update && apt-get -y install libgsl-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/app/main.py" ]
