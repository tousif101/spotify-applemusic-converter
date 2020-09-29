FROM python:3

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

COPY * /app/

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]