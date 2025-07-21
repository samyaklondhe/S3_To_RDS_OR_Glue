import boto3
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import sys

# ✅ AWS Configuration
S3_BUCKET = "your-buckrt-name"   # your bucket
CSV_KEY = "sample-file-name"         # your file
REGION = "us-east-1"

# ✅ RDS MySQL Configuration
RDS_HOST = "myrdsinstance.cs7ococ2ib65.us-east-1.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "MySecurePass123"
RDS_DB = "mydatabase"
RDS_TABLE = "mytabel"

# ✅ Glue Configuration
GLUE_DATABASE = "fallback_db"
GLUE_TABLE = "fallback_people"
GLUE_S3_PATH = f"s3://{S3_BUCKET}/fallback/"

# Initialize clients
s3 = boto3.client('s3', region_name=REGION)
glue = boto3.client('glue', region_name=REGION)

def read_csv_from_s3():
    print("📥 Reading CSV from S3...")
    obj = s3.get_object(Bucket=S3_BUCKET, Key=CSV_KEY)
    df = pd.read_csv(obj['Body'])
    print(f"✅ Loaded {len(df)} records from S3")
    return df

def insert_into_rds(df):
    try:
        print("🔗 Connecting to RDS...")
        conn_str = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}/{RDS_DB}"
        engine = create_engine(conn_str)
        df.to_sql(RDS_TABLE, engine, if_exists='replace', index=False)
        print("✅ Data successfully inserted into RDS")
        return True
    except Exception as e:
        print(f"❌ RDS upload failed: {e}")
        return False

def fallback_to_glue():
    try:
        print("⚠️ Falling back to Glue...")
        glue.create_database(DatabaseInput={'Name': GLUE_DATABASE})
    except glue.exceptions.AlreadyExistsException:
        print("ℹ️ Glue database already exists")

    try:
        glue.create_table(
            DatabaseName=GLUE_DATABASE,
            TableInput={
                'Name': GLUE_TABLE,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'name', 'Type': 'string'},
                        {'Name': 'age', 'Type': 'int'},
                        {'Name': 'city', 'Type': 'string'}
                    ],
                    'Location': GLUE_S3_PATH,
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ','}
                    }
                },
                'TableType': 'EXTERNAL_TABLE'
            }
        )
        print("✅ Glue table created successfully")
    except glue.exceptions.AlreadyExistsException:
        print("ℹ️ Glue table already exists")

if __name__ == "__main__":
    df = read_csv_from_s3()
    if not insert_into_rds(df):
        fallback_to_glue()

