FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt 

COPY . .
ENV ENV=prod
ENV DB_TYPE=postgres
CMD ["/bin/sh", "-c", "python -m counter.entrypoints.webapp"]
