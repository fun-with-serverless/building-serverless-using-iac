Trigger a Lambda every hour to send the scheduled messages.
![send](https://github.com/fun-with-serverless/building-serverless-using-iac/assets/110536677/2345a27a-143e-49df-a4c8-ad951d401019)


## Implementation
* Duplicate `get_subscribers` and rename the new folder `send_scheduled_messages`

* Paste

``` { .py .annotate }
import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from typing import List
from dacite import from_dict
from utils.models import Message
from aws_lambda_powertools import Logger

from utils.consts import SCHEDULED_MESSAGES_TABLE, SUBSCRIBERS_TABLE, SCHEDULED_MESSAGES_BUCKET, SOURCE_EMAIL
from utils.general import get_schedule_date_key, get_subscribers_by_group

logger = Logger()
# Cache client
dynamodb = boto3.resource("dynamodb")
scheduled_messages_table = dynamodb.Table(SCHEDULED_MESSAGES_TABLE)
subscribers_table = dynamodb.Table(SUBSCRIBERS_TABLE)
s3 = boto3.resource("s3")
ses_client = boto3.client('ses')

def lambda_handler(event, context):
    try:
        now = datetime.now()
        logger.info("Checking in DB for relevant messages")
        #(1)!
        responses = scheduled_messages_table.query(KeyConditionExpression=Key('scheduled_date').eq(get_schedule_date_key(now)))["Items"]
        messages_to_send = [response for response in responses if response.get("sent") is None ] #(2)!
        logger.info(f"Found {len(messages_to_send)} messages")
        _send_email_to_subscribers(messages_to_send, s3, SCHEDULED_MESSAGES_BUCKET)

        if len(messages_to_send) > 0:
            logger.info("Emails sent successfully")

        for item in messages_to_send:
            scheduled_messages_table.update_item(
                Key={
                    "scheduled_date": get_schedule_date_key(now),
                    "group_name": item["group_name"]
                },
                UpdateExpression="SET sent=:sent",
                ExpressionAttributeValues={
                    ":sent": True
                },
            )
            logger.info(f"Marked {get_schedule_date_key(now)} for {item['group_name']} as sent")


    except Exception as e:
        logger.error(e)
        raise e



def _get_s3_content(s3, bucket:str, key:str):
    response = s3.Object(SCHEDULED_MESSAGES_BUCKET, key).get()
    return response["Body"].read()

def _send_email(subscribers:List[str], content:Message):
    logger.info(f"Sending {len(subscribers)} emails")
    ses_client.send_email(Source=SOURCE_EMAIL, Destination= {"BccAddresses": subscribers}, Message={
        "Body": {
            "Html": {
                "Charset": "UTF-8",
                "Data": content.body,
            }
        },
        "Subject": {
            "Charset": "UTF-8",
            "Data": content.subject,
        },
    },)


def _send_email_to_subscribers(scheduled_messages:List[dict], s3, bucket:str):
    for message in scheduled_messages:
        subscribers = get_subscribers_by_group(subscribers_table, message["group_name"])
        logger.info(subscribers)
        content = from_dict(data_class=Message, data = json.loads(_get_s3_content(s3, bucket, message["message_key"])))
        _send_email([subscriber["subscriber"] for subscriber in subscribers], content)
```

1. A query returns a list, unlike a regular get operation. A query operates on a specific hash key and retrieves all values with different range keys.
2. Add support for idempotency.

into `app.py`

* Add
``` py
def get_subscribers_by_group(subscribers_table, group:str) -> list:
    return subscribers_table.query(KeyConditionExpression=Key('group_name').eq(group))["Items"] 
```
into `group_subscription_layer/utils/general.py`

* Paste
``` py
from dataclasses import dataclass

@dataclass(frozen=True)
class Message:
    subject:str
    body: str
    schedule_on: int 
```
into `group_subscription_layer/utils/models.py`

* Add
``` py
SOURCE_EMAIL = os.environ.get("SOURCE_EMAIL")
```
to `group_subscription_layer/utils/consts.py`

* Paste
``` py
import json
import boto3
from boto3.dynamodb.conditions import Key
from utils.consts import SUBSCRIBERS_TABLE
from utils.api_gw_helpers import require_group, lambda_response
from utils.general import get_subscribers_by_group

# Cache client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(SUBSCRIBERS_TABLE)

@require_group
def lambda_handler(event, context):
    # Get group name
    group = event["group_name"]
    
    return lambda_response(get_subscribers_by_group(table, group))
```
into `get_subscribers/app.py`

* Add to `user-group/template.yaml`

``` { .yaml .annotate }
SendScheduledMessagesFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: send_scheduled_messages/
      Handler: app.lambda_handler
      Runtime: python3.11
      Architectures:
        - x86_64
      Policies:
        - DynamoDBCrudPolicy:
            TableName:
              !Ref ScheduledMessagesTable
        - DynamoDBReadPolicy:
            TableName:
              !Ref SubscribersTable
        - S3ReadPolicy:
            BucketName:
              !Ref ScheduledMessagesBucket

      Layers: 
        - !Ref SharedLayer
      Environment:
        Variables:
          SCHEDULED_MESSAGES_BUCKET_NAME: !Ref ScheduledMessagesBucket
          SOURCE_EMAIL: !Ref SourceEmail #(1)!
          SCHEDULED_MESSAGES_TABLE_NAME: !Ref ScheduledMessagesTable
          SUBSCRIBERS_TABLE: !Ref SubscribersTable
      Events:
        MessageRule:
          Type: Schedule #(2)!
          Properties:
            Schedule: 'rate(1 hour)' #(3)!
```

1. Access the value of the parameter we will define shortly.
2. Many events can trigger a Lambda; a scheduled event is one of them.
3. You can use also a cron string.


Under the `Resources` section 


* Add
``` yaml
Parameters:
  SourceEmail:
    Type: String
```
above `Resources` section.

* Add
```
aws-lambda-powertools
```
to `group_subscription_layer/utils/requirements.txt`
* Let's deploy it `sam build && sam deploy --guided`. Make sure to define `SourceEmail` parameter to your email
* Next you need to verify your email (the one you defined at the previous step) under the SES service. Follow https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html#verify-email-addresses-procedure
* You are ready to test it

## Testing
1. Let's make sure your email is subscribed to the `sam` group.
```
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/sam/subscribers -H 'Content-Type: application/json' -d '{"email":"youreamil@mail.com"}'
```
```
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/sam/subscribers
```
2. Let's schedule a message for this hour. For the timestamp use https://www.epochconverter.com/
```
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/sam/schedule -H 'Content-Type: application/json' -d '{"subject":"Hello SLS workshop!", "body":"The workshop is not recorded.<h1>Welcome dear friends</h1>", "schedule_on":<epoch including milliseconds>}'
```
3. We can wait for the `SendScheduledMessagesFunction` Lambda to be triggered, but let's try to run it manually.
4. Go the AWS Lambda console, click on the `Test` tab, choose the default values and click on `Save.
<img width="1618" alt="image" src="https://user-images.githubusercontent.com/43570637/162713355-e8fc83a0-a406-43d0-8618-75ea67c658ef.png">
5. You should be getting a permission error
<img width="1624" alt="image" src="https://user-images.githubusercontent.com/43570637/162713582-464565ab-4080-4954-85be-c15a9e346931.png">


   

## Insights
### Parameters
Sometimes you need to accept external values from the users of your template. For example, in our case, we might need an email from which the messages will be sent. This can be achieved in AWS SAM using `Parameters`. When running `sam deploy --guided`, AWS SAM will prompt for the parameter and ask the user to provide its value. You can later access the value of the parameters using `!Ref`.

#### Scheduling
There are multiple ways to schedule events in AWS:

* Use [SQS Delay Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html) to postpone the delivery of a new message by up to 15 minutes.
* Using [EventBridge Rule](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html) is the most straightforward method to schedule an event.
* Using [DDB TTL with DDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/time-to-live-ttl-streams.html) to trigger a Lambda.
* The recently added [AWS Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html) service.

## Exercise
* Add the missing permission, redeploy and retest it.
??? tip
    add the missing permission. Add
    ```
    SESCrudPolicy:
        IdentityName:
            !Ref SourceEmail
    ```
    Under policies for the `SendScheduledMessagesFunction` Lambda
* Replace the `Schedule` attribute with an identical cron string.
* Replace the scheduling mechanism with `AWS Scheduler`
??? tip
    Use `ScheduleV2`
* Use the Lambda Power Tools to add event source data classes to the API Gatway Lambdas.
??? tip
    Follow https://docs.powertools.aws.dev/lambda/python/latest/utilities/data_classes/#api-gateway-proxy
