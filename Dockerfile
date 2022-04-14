FROM python:3.9-bullseye

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/app/main.py" ]
