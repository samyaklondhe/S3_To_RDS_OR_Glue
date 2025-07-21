FROM python:3.9-slim

# Install MySQL client (optional)
RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY s3_to_rds_or_glue.py .

# Run script on container start
CMD ["python", "s3_to_rds_or_glue.py"]

