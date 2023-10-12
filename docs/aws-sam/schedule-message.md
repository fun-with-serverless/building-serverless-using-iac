Schedule content to be sent at a specific hour and date to all the subscribers of a specific group.
![schedule](https://github.com/fun-with-serverless/building-serverless-using-iac/assets/110536677/9e2637f9-2ff5-4548-816c-5d4df74b1806)

## Implementation
* Duplicate `get_subscribers` and rename the new folder `schedule_message`
* Paste

``` { .py .annotate }
import json
import boto3
from datetime import datetime
from dataclasses import dataclass
from dacite import from_dict
import logging
import random
import string
import re


from utils.consts import SCHEDULED_MESSAGES_TABLE, SCHEDULED_MESSAGES_BUCKET
from utils.api_gw_helpers import require_group, lambda_response
from utils.general import get_schedule_date_key

# Cache client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(SCHEDULED_MESSAGES_TABLE)

s3 = boto3.resource("s3")
bucket = s3.Bucket(SCHEDULED_MESSAGES_BUCKET)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass(frozen=True) #(1)!
class Message:
    subject: str
    body: str
    schedule_on: int


@require_group
def lambda_handler(event, context):
    # Get group name
    group = event["group_name"]
    body = event.get("body")
    if body is None:
        return lambda_response({"err": "Missing message details"}, status_code=500)
    else:
        try:
            message = from_dict(data_class=Message, data=json.loads(body))
            logger.info("Saving message into S3")
            key = "".join(random.choice(string.ascii_lowercase) for i in range(10))
            meta_data = {
                "group": group,
                "subject": message.subject,
                "scheduled": str(datetime.fromtimestamp(message.schedule_on / 1000)),
                "key": key,
            }
            tagging = "&".join( #(2)!
                f"{k}={_filter_string(str(v))}" for k, v in meta_data.items()
            )
            logger.info(tagging)
            bucket.put_object(Body=str.encode(body), Key=key, Tagging=tagging)
            logger.info("S3 object saved successfully")
            response = table.put_item(
                Item={
                    "group_name": group,
                    "scheduled_date": get_schedule_date_key(
                        datetime.fromtimestamp(message.schedule_on / 1000)
                    ),
                    "message_key": key,
                    "message_added": int(datetime.now().timestamp() * 1000),
                }
            )
            logger.info("DDB object saved successfully")

            return lambda_response(
                {"message": "Message scheduled successfully", "details": meta_data}
            )

        except Exception as e:
            logging.error(e)
            return lambda_response({"err": "Failed saving message"}, status_code=500)


def _filter_string(s: str):
    return re.sub(r"[^\w\s\+\-=:\/@\.]", "", s)

```

1. Encapsulate data as a model.
2. Not all tage values are valid.

into `app.py`

* Paste
```
boto3==1.21.37
dacite==1.6.0
```
into `group_subscription_layer/utils/requirements.txt`

* Paste
``` py
from datetime import datetime
from boto3.dynamodb.conditions import Key

def get_schedule_date_key(exact_date:datetime) -> str:
    return f"{exact_date.year}_{exact_date.month}_{exact_date.day}_{exact_date.hour}"

```
into `group_subscription_layer/utils/general.py`

* Add to `template.yaml`
Under Resources

``` { .yaml .annotate }
ScheduleFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: schedule_message/
      Handler: app.lambda_handler
      Runtime: python3.11
      Architectures:
        - x86_64
      Policies:
        - DynamoDBWritePolicy:
            TableName:
              !Ref ScheduledMessagesTable
        - S3WritePolicy:
            BucketName: !Ref ScheduledMessagesBucket
        - Statement: #(1)!
            - Effect: "Allow"
              Action:
                - "s3:PutObjectTagging"
              Resource: !Sub "arn:aws:s3:::${ScheduledMessagesBucket}/*"

      Layers: 
        - !Ref SharedLayer
      Environment:
        Variables:
          SCHEDULED_MESSAGES_BUCKET_NAME: !Ref ScheduledMessagesBucket
          SCHEDULED_MESSAGES_TABLE_NAME: !Ref ScheduledMessagesTable
      Events:
        Subscribers:
          Type: Api 
          Properties:
            Path: /{group}/schedule
            Method: post
```

1. Use a manually defined policy.



Add new S3 bucket definition
``` yaml
ScheduledMessagesBucket:
    Type: AWS::S3::Bucket
```

Add a new table definition
``` yaml
ScheduledMessagesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: "scheduled_messages"
      AttributeDefinitions: 
        - 
          AttributeName: "group_name"
          AttributeType: "S"
        - 
          AttributeName: "scheduled_date"
          AttributeType: "S"
      KeySchema: 
        - 
          AttributeName: "scheduled_date"
          KeyType: "HASH"
        - 
          AttributeName: "group_name"
          KeyType: "RANGE"
      BillingMode: PAY_PER_REQUEST
```

Replace the `Outputs` section
``` yaml
Outputs:
  SubscribersList:
    Description: "API Gateway endpoint URL getting the subscribers"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/{group}/subscribers"
    
  ScheduleMessage:
    Description: "API Gateway endpoint URL for scheduling a message"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/{group}/schedule"
```

* Paste 
``` py
import os

SUBSCRIBERS_TABLE = os.environ.get("SUBSCRIBERS_TABLE")
SCHEDULED_MESSAGES_TABLE = os.environ.get("SCHEDULED_MESSAGES_TABLE_NAME")
SCHEDULED_MESSAGES_BUCKET = os.environ.get("SCHEDULED_MESSAGES_BUCKET_NAME") 
```
into `group_subscription_layer/utils/consts.py`

* Rerun `sam build && sam deploy`.

* Test it using curl
`curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/serverless/schedule -H 'Content-Type: application/json' -d '{"subject":"Hello SLS workshop!", "body":"The workshop is not recorded.<h1>Welcome dear friends</h1>", "schedule_on":1649753447000}'`
* Search for the file on the S3 bucket and the record in DynamoDB.

## Insights
#### Using S3 to store content
DynamoDB has a strict size limit of 400KB per record. Therefore, when storing content that exceeds this limit, it is recommended to use S3 to store the content and use a 'pointer' (an S3 object path) to the full content, as part of the DynamoDB record. In the above code, we are saving content into S3 and storing the object key as part of the DynamoDB record.
``` py
bucket.put_object(Body=str.encode(body), Key=key, Tagging=tagging) # <-- Save to S3
logger.info("S3 object saved successfully")
response = table.put_item(
    Item={
    "group_name": group,
    "scheduled_date": message.schedule_on,
    "message_key": key, # <-- Use key
    "message_added": int(datetime.now().timestamp() * 1000)
    }
)
```

#### Tagging S3 objects
AWS Tags are a valuable feature in AWS. I highly recommend making use of them wherever possible, as they can aid in [cost optimization](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) and [compliance](https://docs.aws.amazon.com/config/latest/developerguide/tagging.html).

In addition to tagging resources, you can also tag your S3 objects, which serves several purposes:

* An easy way to understand the content of the object without actually downloading and opening it.
* Identify large objects in S3, manage their costs, and control their [life cycle](https://aws.amazon.com/blogs/storage/simplify-your-data-lifecycle-by-using-object-tags-with-amazon-s3-lifecycle/)
* [Access control](https://docs.aws.amazon.com/AmazonS3/latest/userguide/tagging-and-policies.html)

Tagging S3 objects has some limitations on the types of characters that are allowed as part of your key and value content. For example, characters like `!` or `@` are not allowed. In cases like this, you can encode your string to eliminate these characters

![CleanShot 2023-05-16 at 17 19 34@2x](https://github.com/aws-hebrew-book/building-serverless-in-hebrew-workshop/assets/110536677/23bf743f-5fb7-4cb3-8df0-d1d1c19c08bc)

#### PowerTools
Stop reinventing the wheel. AWS Lambda Power Tools is a suite of utilities for AWS Lambda functions that makes it easier for developers to follow best practices for tracing, structured logging, custom metrics, and more. You can find more details [here](https://awslabs.github.io/aws-lambda-powertools-python/2.15.0/)
#### Principle of Least Priviliged Access - Take 2
There may be instances where AWS SAM doesn't supply the exact IAM policies you require. In such situations, it becomes necessary to formulate your own policy. For our specific scenario, we need the `PutObjectTagging` permission to write an S3 object tag. Unfortunately, AWS SAM doesn't offer this particular policy. The only available option is the `S3FullAccessPolicy`, which is excessively broad for our needs.

## Exercies
* Add Lambda Power Tools and replace the existing log statements with those provided by Power Tools.
* Why did we choose to structure the DynamoDB table the way we did?
* Replace the `DynamoDBWritePolicy` policy with a manually defined policy that only allows the `dynamodb:PutItem` operation.
??? tip
    1. Each policy has a strict structure; adhere to it.
    2. Define `Effect`, `Action` and `Resource`
