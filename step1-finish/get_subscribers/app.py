import json
import os
import boto3
from boto3.dynamodb.conditions import Key


# Cache client
session = boto3.Session()
dynamodb = session.resource("dynamodb")
SUBSCRIBERS_TABLE = os.environ.get("SUBSCRIBERS_TABLE")
table = dynamodb.Table(SUBSCRIBERS_TABLE)
def lambda_handler(event, context):
    # Get group name
    group = event.get("pathParameters", {}).get("group")
    if group:
        response = table.query(
            KeyConditionExpression=Key('group_name').eq(group)
        )
        return {
            "statusCode": 200,
            "body": json.dumps(response['Items']),
        }
    else:
        return {
            "statusCode": 500,
            "body": "Missing group!",
        }