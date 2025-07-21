import os
import boto3
import pandas as pd
from sqlalchemy import create_engine
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_FILE_KEY = os.getenv("S3_FILE_KEY")
RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_DB = os.getenv("RDS_DB")
RDS_TABLE = os.getenv("RDS_TABLE")
GLUE_DATABASE = os.getenv("GLUE_DATABASE")
GLUE_TABLE = os.getenv("GLUE_TABLE")
GLUE_S3_LOCATION = os.getenv("GLUE_S3_LOCATION")

def read_csv_from_s3():
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_KEY)
    return pd.read_csv(obj['Body'])

def upload_to_rds(df):
    try:
        engine = create_engine(f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}/{RDS_DB}")
        df.to_sql(RDS_TABLE, con=engine, if_exists='append', index=False)
        print("✅ Data successfully inserted into RDS")
        return True
    except Exception as e:
        print(f"❌ RDS upload failed: {e}")
        return False

def fallback_to_glue():
    glue = boto3.client('glue', region_name=AWS_REGION)
    try:
        glue.create_database(DatabaseInput={"Name": GLUE_DATABASE})
    except glue.exceptions.AlreadyExistsException:
        print("Glue database already exists")

    glue.create_table(
        DatabaseName=GLUE_DATABASE,
        TableInput={
            "Name": GLUE_TABLE,
            "StorageDescriptor": {
                "Columns": [{"Name": "col1", "Type": "string"}, {"Name": "col2", "Type": "string"}],
                "Location": GLUE_S3_LOCATION,
                "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                "SerdeInfo": {"SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"}
            }
        }
    )
    print("✅ Fallback Glue table created successfully")

if __name__ == "__main__":
    df = read_csv_from_s3()
    print(f"📄 Loaded {len(df)} records from S3")
    if not upload_to_rds(df):
        fallback_to_glue()
