from dotenv import load_dotenv
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import os

load_dotenv(Path(__file__).resolve().parent / ".env")
def get_dynamodb():
    return boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION", "ap-south-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

def table_exists(db, table_name):
    client = db.meta.client
    resp = client.list_tables()
    return table_name in resp.get("TableNames", [])

def create_table_if_missing(table_name):
    db = get_dynamodb()
    if table_exists(db, table_name):
        print(f"Table '{table_name}' already exists.")
        return

    try:
        table = db.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"Creating table '{table_name}' ...")
        table.wait_until_exists()
        print(f"Table '{table_name}' is now ACTIVE.")
    except ClientError as e:
        print(f"Failed to create table '{table_name}': {e}")


if __name__ == "__main__":
    create_table_if_missing("help_requests")
    create_table_if_missing("knowledge_base")
    print("Done creating tables.")
