FROM python:3.9-slim

RUN apt-get update && apt-get install -y default-mysql-client

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY s3_to_rds_or_glue.py .

CMD ["python", "s3_to_rds_or_glue.py"]
