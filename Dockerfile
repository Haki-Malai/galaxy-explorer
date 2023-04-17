FROM python:3.9.0

WORKDIR /app

COPY main.py /app
COPY requirements.txt /app
COPY starwars_api.py /app
COPY test /app/test

RUN python -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

ENV PYTHONPATH=/app

CMD ["bash", "-c", "source venv/bin/activate && python main.py test"]
