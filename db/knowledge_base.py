import uuid
import time
from db.client import get_dynamodb_client

TABLE_NAME = "knowledge_base"

def add_kb_entry(question, answer):
    db = get_dynamodb_client()
    table = db.Table(TABLE_NAME)
    item = {
        "id": str(uuid.uuid4()),
        "question": question,
        "answer": answer,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    table.put_item(Item=item)
    return item

def get_kb_entries():
    db = get_dynamodb_client()
    table = db.Table(TABLE_NAME)
    response = table.scan()
    return response["Items"]

def get_kb_answer_for_question(question):
    db = get_dynamodb_client()
    table = db.Table(TABLE_NAME)
    response = table.scan(
        FilterExpression="question = :qval",
        ExpressionAttributeValues={":qval": question}
    )
    items = response["Items"]
    return items[0]["answer"] if items else None

def delete_kb_entry(entry_id):
    db = get_dynamodb_client()
    table = db.Table(TABLE_NAME)
    response = table.delete_item(Key={"id": entry_id})
    return response

