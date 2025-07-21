# Task 5 - Data Ingestion from S3 to RDS with Fallback to AWS Glue

This project automates data ingestion from an S3 bucket to an RDS MySQL database using a Dockerized Python script. If the RDS upload fails, it falls back to AWS Glue to create a table and register the dataset.

## Steps
1. Read CSV from S3 using boto3
2. Upload to RDS using SQLAlchemy
3. If RDS upload fails, create Glue database & table
4. Dockerized the script for easy deployment

## Usage
```bash
docker build -t s3-to-rds-or-glue .
docker run --rm   -e AWS_ACCESS_KEY_ID=xxx   -e AWS_SECRET_ACCESS_KEY=xxx   -e AWS_DEFAULT_REGION=us-east-1   -e S3_BUCKET_NAME=my-bucket   -e S3_FILE_KEY=sample.csv   -e RDS_HOST=mydb.rds.amazonaws.com   -e RDS_USER=admin   -e RDS_PASSWORD=pass   -e RDS_DB=mydatabase   -e RDS_TABLE=mytable   -e GLUE_DATABASE=my_glue_db   -e GLUE_TABLE=my_glue_table   -e GLUE_S3_LOCATION=s3://my-bucket/glue-data/   s3-to-rds-or-glue
```

## Files
- `s3_to_rds_or_glue.py` → Main Python script
- `Dockerfile` → Docker build configuration
- `requirements.txt` → Python dependencies
