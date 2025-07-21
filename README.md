Data Ingestion from S3 to RDS with Fallback to AWS Glue

Project Overview

This project demonstrates a fault-tolerant data ingestion pipeline that reads a CSV file from an Amazon S3 bucket, attempts to insert the data into an RDS MySQL database, and if the RDS database is unavailable or the operation fails, it falls back to AWS Glue by creating a Glue Data Catalog table pointing to the S3 dataset.

The pipeline is Dockerized for easy deployment and automation.


---

Architecture

1. S3 → RDS (Primary Path)

Reads sample_data.csv from S3

Parses it using pandas

Inserts rows into RDS MySQL table using SQLAlchemy



2. Fallback → Glue Catalog

If RDS connection fails

Creates a Glue Database (if not exists)

Creates a Glue Table with schema inferred from the CSV

Registers the dataset location in S3



3. Dockerized Setup

Python application packaged into a Docker image

Runs automatically with required AWS credentials as environment variables





---

AWS Services Used

Amazon S3 → Stores input CSV file

Amazon RDS (MySQL) → Primary database to store ingested data

AWS Glue → Fallback data catalog when RDS is unavailable

IAM → Provides programmatic access credentials for the pipeline



---

Prerequisites

AWS Account with access to S3, RDS, and Glue

EC2 or local machine with:

Docker installed

AWS CLI configured

MySQL client installed


Python 3.9+ if running locally (not in Docker)



---

Setup Steps

1. Create an S3 bucket & upload CSV file

aws s3 mb s3://my-data-pipeline-bucket
aws s3 cp sample_data.csv s3://my-data-pipeline-bucket/


2. Create RDS MySQL Instance

aws rds create-db-instance \
    --db-instance-identifier myrdsinstance \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username admin \
    --master-user-password MySecurePass123 \
    --allocated-storage 20 \
    --publicly-accessible \
    --region us-east-1

Fetch endpoint:

aws rds describe-db-instances --db-instance-identifier myrdsinstance --query "DBInstances[0].Endpoint.Address"


3. Allow RDS Access

Edit Security Group → add Inbound rule for MySQL (3306)

From your EC2/Public IP



4. Create Database & Table

mysql -h <RDS_ENDPOINT> -u admin -p
CREATE DATABASE mydatabase;
USE mydatabase;
CREATE TABLE mytable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    city VARCHAR(100)
);


5. Create Glue Database (fallback)

aws glue create-database --database-input '{"Name":"my_glue_db"}'




---

Python Script Explanation

s3_to_rds_or_glue.py

Downloads CSV from S3

Reads using pandas

Tries inserting into RDS

If fails → registers Glue Table



Key Libraries
boto3, pandas, sqlalchemy, pymysql


---

Running Locally (Virtual Environment)

python3 -m venv myenv
source myenv/bin/activate
pip install boto3 pandas sqlalchemy pymysql
python3 s3_to_rds_or_glue.py


---

Docker Setup

1. Build Docker Image

sudo docker build -t s3-to-rds-or-glue .


2. Run Docker Container

sudo docker run --rm \
  -e AWS_ACCESS_KEY_ID=xxxx \
  -e AWS_SECRET_ACCESS_KEY=xxxx \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e S3_BUCKET_NAME=my-data-pipeline-bucket \
  -e S3_FILE_KEY=sample_data.csv \
  -e RDS_HOST=myrdsinstance.abcdefgh.us-east-1.rds.amazonaws.com \
  -e RDS_USER=admin \
  -e RDS_PASSWORD=MySecurePass123 \
  -e RDS_DB=mydatabase \
  -e RDS_TABLE=mytable \
  -e GLUE_DATABASE=my_glue_db \
  -e GLUE_TABLE=my_glue_table \
  -e GLUE_S3_LOCATION=s3://my-data-pipeline-bucket/glue-data/ \
  s3-to-rds-or-glue




---

Expected Output

✅ Case 1: RDS available

CSV rows inserted into RDS

MySQL query SELECT * FROM mytable; shows data


✅ Case 2: RDS unavailable

Logs show “RDS upload failed”

Glue Database + Table created

AWS Glue Console shows registered table



---

Benefits

Ensures high availability of data ingestion

Eliminates manual intervention for failures

Uses AWS-native services for scalability



---

Challenges & Fixes

RDS connectivity issue → Fixed by updating Security Group

Docker AWS credentials → Passed via environment variables

Glue schema mismatch → Used pandas dataframe for schema inference



---

How It Works

1. Read CSV from S3


2. Parse and insert into RDS


3. If insert fails → Glue Catalog fallback


4. Docker ensures isolated & repeatable execution




---

Conclusion

This project demonstrates a robust ETL pipeline using AWS services. It prioritizes RDS for structured storage and automatically falls back to Glue for metadata registration, ensuring data is always accessible even during failures.


---
