import uuid
import time
from db.client import get_dynamodb_client
from db.knowledge_base import add_kb_entry, get_kb_answer_for_question
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

TABLE_NAME = "help_requests"

def save_help_request(customer_id, question):
    db = get_dynamodb_client()
    table = db.Table(TABLE_NAME)
    item = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "question": question,
        "status": "Pending",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "supervisor_answer": None,
        "resolved_at": None,
    }
    table.put_item(Item=item)
    return item

def get_help_requests_by_status(status="Pending"):
    db = get_dynamodb_client()
    table = db.Table(TABLE_NAME)
    response = table.scan(
        FilterExpression=Attr("status").eq(status)
    )
    return response["Items"]

def resolve_help_request(request_id, answer):
    db = get_dynamodb_client()
    table = db.Table(TABLE_NAME)
    request_id = str(request_id)

    try:
        existing = table.get_item(Key={"id": request_id})
        if "Item" not in existing:
            raise ValueError(f"Help request not found: {request_id}")

        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        resp = table.update_item(
            Key={"id": request_id},
            ExpressionAttributeNames={
                "#st": "status",
                "#sa": "supervisor_answer",
                "#ra": "resolved_at",
            },
            ExpressionAttributeValues={
                ":st": "Resolved",
                ":ans": answer,
                ":now": now,
            },
            UpdateExpression="SET #st = :st, #sa = :ans, #ra = :now",
            ReturnValues="ALL_NEW",
        )
        question = existing["Item"]["question"]
        kb_answer = get_kb_answer_for_question(question)
        if not kb_answer:
            add_kb_entry(question, answer)
        return resp.get("Attributes")
    except ClientError as e:
        print(f"DynamoDB ClientError updating request {request_id}: {e}")
        raise
    except Exception as e:
        print(f"Error resolving help request {request_id}: {e}")
        raise
