# Building a Serverless application using IAC - the workshop

  * [Welcome](#welcome)
  * [Prepare your machine](#prepare-your-machine)
  * [Hello SAM](#hello-sam)
  * [Step 1 - Implement get-subscribers](#step-1---implement-get-subscribers)
    + [Add a new group with subscribers](#add-a-new-group-with-subscribers)
  * [Step 2 - Implement add-subscriber](#step-2---implement-add-subscriber)
  * [Step 3 - Schedule a message](#step-3---schedule-a-message)
  * [Step 4 - Send a message](#step-4---send-a-message)
  * [Testing & Monitoring](#testing---monitoring)
  * [Deletion](#deletion)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

 
## Welcome
Ever wanted to create your own mailing list manager a la Serverless style, now is your chance. In this workshop you'll build a mailing list manager with the ability to:
* Create new mailing list
* Allow external participants to join these lists
* Schedule sending a message via email to the subscribers.
![workshop](https://user-images.githubusercontent.com/43570637/162735759-7a6dd10b-c1da-4250-bf4c-ddccd53766f7.png)

The development of the application is carried out in four phases, where each phase incorporates new features.


## Prepare your machine
1. Install AWS SAM. Follow https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
2. Verify it works as expected, run `sam --version` you should be getting something like `> SAM CLI, version 1.33.0`. Pay attention that the version might change
3. Let's initialize an Hello World for SAM example. If it works, then your machine is ready.
4. Clone `https://github.com/aws-hebrew-book/building-serverless-using-iac.git`

The application will be constructed using AWS SAM. The next section provides an overview of AWS SAM; if you already have experience with this service, feel free to skip ahead.

## Hello SAM
[Amazon Web Services Serverless Application Model (AWS SAM)](https://aws.amazon.com/serverless/sam/) is a framework for building serverless applications. It simplifies the process of creating and managing resources used in serverless applications using AWS services like Lambda, API Gateway, and DynamoDB. 
AWS SAM uses a template file to define your serverless application and its resources, providing a streamlined and consistent method for deploying complex serverless applications. 
By leveraging AWS SAM, you can more easily automate deployment processes, test your applications locally before deploying, and even generate boilerplate code for common serverless patterns.

In the following section we will build a simple hello world application using SAM.
1. `sam init`
2. Choose `AWS Quick Start Templates`
3. Next choose `Hello World Example`
4. If you choose to use the most popular runtime and package type, then make sure that Python 3.9 is installed
6. Choose `Python 3.7`
7. Choose `Zip`
8. For project name, choose the default
<img src="https://github.com/aws-hebrew-book/building-serverless-in-hebrew-workshop/assets/110536677/4bf1a5ca-cdbe-455b-a29d-2ce4a4ddddf0" width="400">

10. You need to build the sam packge 
11. Go to the folder the template created `cd sam-app`
12. Run `sam build` and next run `sam deploy --guided`. You should run guided each time you want to add something to the sam configuration file or create it for the first time.
13. When asked `HelloWorldFunction may not have authorization defined, Is this okay?` choose `y`
14. The rest can be defaults
15. `Deploy this changeset?` choose `y`
16. Give the deployment a try, you should see under `Outputs` the `API Gateway endpoint URL`, copy the URL and try it on browser.
17. When done, run `sam delete` to remove the stack.


<details>
  <summary>👂 Speaker Notes</summary>
	
### Template
	
At the core of every AWS SAM application lies the template.yaml, a file that outlines the resources utilized by the app. Our sample template file is split into four main sections:
  <ol>
    <li>
      Header - This section provides the template's definition and description, which are displayed in the CloudFormation console.
    </li>
    <li>
      Global - This section contains global configurations that apply to all resources. In our case, we have set default values for the timeout and memory of all Lambdas to 3 seconds and 128 MB, respectively.
    </li>
    <li>
      Resources - This section details the resources to be established as part of the application. In our case, it is a Lambda function.
    </li>
    <li>
      Outputs - This section enumerates output values that can be imported into other stacks (for creating cross-stack references), returned in responses (to provide stack call descriptions), or viewed on the AWS CloudFormation console.
    </li>
  </ol>
	
### Simplicity
With AWS SAM, defining a Lambda function is as straightforward as pointing to a directory containing your code. AWS SAM then takes care of bundling the folder's contents along with the necessary dependencies into a zip file, and uploading it to AWS. It also automatically generates the appropriate IAM roles for you during this process.
  
### Interoperability
A key advantage of AWS SAM is its seamless integration with other services. For instance, in our example, we've integrated our Lambda function with API Gateway, demonstrating the simplicity of combining AWS services in a SAM application.
</details>



## Step 1 - Implement get-subscribers
1. Go to `start-here-step1`
3. You should see a basic structure of our SAM aplication for managing user groups.
5. Add `boto3==1.21.37` to `get_subscribers/requirements.txt`
6. Paste
```
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
  user-group
  User group functionality
Globals:
  Function:
    Timeout: 10

Resources:
  GetSubscribersFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: get_subscribers/
      Handler: app.lambda_handler
      Runtime: python3.7
      Environment:
        Variables:
          SUBSCRIBERS_TABLE: !Ref SubscribersTable
      Architectures:
        - x86_64
      Policies:
        - DynamoDBReadPolicy:
            TableName:
              !Ref SubscribersTable
      
      Events:
        Subscribers:
          Type: Api 
          Properties:
            Path: /{group}/subscribers
            Method: get
  
  SubscribersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      AttributeDefinitions: 
        - 
          AttributeName: "group_name"
          AttributeType: "S"
        - 
          AttributeName: "subscriber"
          AttributeType: "S"
      KeySchema: 
        - 
          AttributeName: "group_name"
          KeyType: "HASH"
        - 
          AttributeName: "subscriber"
          KeyType: "RANGE"
      BillingMode: PAY_PER_REQUEST
Outputs:
  SubscribersApi:
    Description: "API Gateway endpoint URL for Prod stage for subscribers"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/{group}/subscribers"
```
into `template.yaml`


7. Paste 
```
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
```
into `app.py`

8. Build and deploy `sam build`
9. `sam deploy --guided`. Use `user-groups` as stack name

### Add a new group with subscribers
1. Use the DynamoDB console to add a new group with multiple subscribers
2. Make an API call and get back results
<img width="1320" alt="CleanShot 2023-05-16 at 14 29 16@2x" src="https://github.com/aws-hebrew-book/building-serverless-in-hebrew-workshop/assets/110536677/8349b69a-9370-4150-950b-7273c705ee70">


<details>
<summary>👂 Speaker Notes</summary>

### Hard coding resource names
Avoid hardcoding resource names into your code. Resource names have a tendency to change quite frequently, especially if you are following best practices such as using a unique prefix for each environment.

In AWS SAM, you can easily retrieve resource names using `!Ref` or `!GetAtt logicalNameOfResource.attributeName`. Each CloudFormation resource type documentation includes a 'Return Value' section, which can guide you on which CloudFormation function to use.

You can pass the resource name as an environment variable into Lambda and easily retrieve it via code. In the above code snippet, we are passing the table name using the `SUBSCRIBERS_TABLE` environment variable and retrieving it using `os.environ.get("SUBSCRIBERS_TABLE")`.

### Session managment and Caching
Sessions can be used to isolate resources and clients from each other, which can help to prevent accidental access to another session's resources. This is particularly useful when you want to use a different set of AWS credentials or when you want to ensure that the resources and clients of one part of your code do not accidentally have access to another part's resources. Creating a new session does not establish a new connection to AWS. Instead, it helps manage AWS credentials and configurations and allows Boto3 to more efficiently reuse connections, so the second time this Lambda container is called, it can reuse a previous connection.

### DDB structure
We are structuring our DynamoDB table based on the queries we intend to use. Currently, we expect to retrieve all subscribers for a specific group, so we are defining the group name as the primary key. This is achieved by setting `group_name` as `HASH` in the AWS SAM definition of the table.

### Principle of Least Priviliged Access
> Every module (such as a process, a user, or a program, depending on the subject) must be able to access only the information and resources that are necessary for its legitimate purpose.

Our Lambda function only requires ReadOnly access to the DynamoDB table we created. You can define permissions by adding a `Policies` attribute. AWS SAM includes a list of predefined policies that you can use, which can be found [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-template-list.html#dynamo-db-read-policy). Each policy typically accepts a parameter that specifies the resource to which the policy is applied. In our case, the parameter is `TableName`.

### API Gateway integration
One of the benefits of AWS SAM is its ease of event-based integration with additional AWS services like SQS, SNS, API Gateway, etc. To add event integration, all you need to do is add an `Event` attribute with the relevant configuration.

In our case, we are integrating with API Gateway. We define the base URL path using curly braces, like `/{group}/subscribers`. This means that whenever an external client accesses the API, it needs to supply the group it wants to pull. The integration here is proxy-based, so all paths and headers are passed directly to the Lambda function as part of the event variable. You can easily retrieve the path parameter by using `event.get("pathParameters", {}).get("group")` in the code.

</details>



## Step 2 - Implement add-subscriber
1. Duplicate `get_subscribers` and rename the new folder `add_subscriber`
2. Paste
```
import json
import boto3
from datetime import datetime

from utils.consts import SUBSCRIBERS_TABLE
from utils.api_gw_helpers import require_group, lambda_response

# Cache client
session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(SUBSCRIBERS_TABLE)

@require_group
def lambda_handler(event, context):
    # Get group name
    group = event["group_name"]
    email = json.loads(event.get("body", {})).get("email")
    if email:
        response = table.put_item(
           Item={
                "group_name": group,
                "subscriber": email,
                "date_joined": int(datetime.now().timestamp() * 1000)
            }
        )

        return lambda_response({"message":f"{email} added successfully"})

    return lambda_response({"err":"Email not found"}, status_code=500)
```
into `app.py`

3. We are going to create a Lambda Layer. Create a new folder `group_subscription_layer` and inside create `utils` python package. It is a folder with `__init__.py` file.
<img width="158" alt="CleanShot 2023-05-16 at 16 08 08@2x" src="https://github.com/aws-hebrew-book/building-serverless-using-iac/assets/110536677/4b775466-b89a-456b-bc86-5c2176c7d198">

5. Paste 
```
import json 
from typing import Callable, Any, Optional, List, Dict, Union

def lambda_response(
    content: Any,
    status_code: int = 200,
    content_type: str = "application/json",
) -> dict:
    """
    Returns a dictionary that adheres to the required format that is needed by AWS api gw ->> Lambda proxy integration.
    See https://aws.amazon.com/premiumsupport/knowledge-center/malformed-502-api-gateway/ for more details
    :param content: The actual content that needs to return
    :param status_code: The status code of the response. In case of an exception, you can use a more specialized method
    :param content_type: The Content-Type header value of the response.
    :param should_gzip: Should the content be compressed.
    """

    try:
        body_message = (
            json.dumps(content, default=str) if content_type == "application/json" else content
        )
    except Exception as err:
        print(f"Invalid lambda response. {err}")

        status_code = 500
        body_message = "Err"
    response = {
        "statusCode": str(status_code),
        "body": body_message,
        "headers": {
            "Content-Type": content_type,
        },
    }

    return response


def require_group(function):
    def wrapper(*args, **kwargs):
        event = args[0]
        if type(event).__name__ != "dict":
            return function(*args, **kwargs)

        group = event.get("pathParameters", {}).get("group")
        if group:
            event["group_name"] = group
            return function(*args, **kwargs)
        else:
            return {
                "statusCode": 500,
                "body": "Missing group!",
            }

    return wrapper
```
into `group_subscription_layer/utils/api_gw_helpers.py`

5. Paste 
```
import os
SUBSCRIBERS_TABLE = os.environ["SUBSCRIBERS_TABLE"]
``` 
into `group_subscription_layer/utils/consts.py`

6. Add
```
SharedLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: group-subscription-layer
      Description: Utility layer used by subscription application
      ContentUri: group_subscription_layer/
      CompatibleRuntimes:
        - python3.10
        - python3.9
        - python3.7
    Metadata:
      BuildMethod: python3.7

AddSubscriberFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: add_subscriber/
      Handler: app.lambda_handler
      Runtime: python3.7
      Environment:
        Variables:
          SUBSCRIBERS_TABLE: !Ref SubscribersTable
      Architectures:
        - x86_64
      Policies:
        - DynamoDBWritePolicy:
            TableName:
              !Ref SubscribersTable

      Layers: 
        - !Ref SharedLayer
      Events:
        Subscribers:
          Type: Api 
          Properties:
            Path: /{group}/subscribers
            Method: post
```
to `template.yaml` under `Resources`

7. Add
```
Layers: 
	- !Ref SharedLayer
```
to under `template.yaml` under `GetSubscribersFunction` function definition.
9. Simplify `get_subscribers/app.py`
```
import json
import boto3
from boto3.dynamodb.conditions import Key
from utils.consts import SUBSCRIBERS_TABLE
from utils.api_gw_helpers import require_group, lambda_response


# Cache client
session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(SUBSCRIBERS_TABLE)

@require_group
def lambda_handler(event, context):
    # Get group name
    group = event["group_name"]
    
    response = table.query(
        KeyConditionExpression=Key('group_name').eq(group)
    )
    return lambda_response(response['Items'])
```
8. Delete `requirements.txt` from `get_subscribers` and `add_subscriber`. We are using a Lambda Layer which will hold our requirements.
9. Paste 
```
boto3==1.21.37
``` 
into `group_subscription_layer/requirements.txt`

10. `sam build && sam deploy`
11. Test it using curl
```
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/Prod/serverless/subscribers -H 'Content-Type: application/json' -d '{"email":"mymail@mail.com"}'
curl https://<api-d>.execute-api.<region>.amazonaws.com/Prod/serverless/subscribers
```
Replace **api-id** and **region** with the relevent code you can copy from the output 
This will create a new mailing list named `serverless` and add a new subscriber to it.

<details>
  <summary>👂 Speaker Notes</summary>
	
#### Python Decorators
> A decorator is a function that takes another function and extends the behavior of the latter function without explicitly modifying it.

A Python decorator is a form of syntactic sugar that allows us to modify a function's behavior using an `@<function_name>` annotation. In our scenario, we consistently extract the group name from the path parameter, and if it's not found, we want to return a valid error. We can use a decorator to enhance a Lambda handler by injecting the necessary parameters into the event.

We've defined a decorator called `require_group` as part of the utils package, which incorporates `group_name` into the event. If the path parameter is not found, it returns a `500` error to the caller.

Example:
```
@require_group
def lambda_handler(event, context):
    # Get group name
    group = event["group_name"]
 ```
 #### Permissions
Just like the previous section, we are adhering to the Principle of Least Privilege Access here, granting the Lambda only write access to the table.

#### Lambda Layers
> Lambda layers provide a convenient way to package libraries and other dependencies that you can use with your Lambda functions. Using layers reduces the size of uploaded deployment archives and makes it faster to deploy your code.

The utils package is utilized throughout the project, and our aim is to prevent its duplication. Moreover, our layer envelops all the necessary packages, thereby diminishing the size of the main Lambda. This results in:
1. Expedited deployment
2. The capability to inspect the code within the AWS Console.
	
By incorporating
 
```
Metadata:
	BuildMethod: python3.7
```
into the layer specification, we are directing AWS SAM to construct the layer by installing the appropriate dependencies (utilizing pip in our scenario). Absence of this specification would result in AWS SAM merely zipping and deploying the layer, without any dependency installation.
	
You can view the layer in the AWS Console.
![CleanShot 2023-05-25 at 13 34 54@2x](https://github.com/aws-hebrew-book/building-serverless-using-iac/assets/110536677/7c3cfe9f-f593-4041-8b33-f4d9eb89b6b4)


	
#### API Gateway response
API Gateway requires a specific response structure:
```
{
  "statusCode": str(status_code),
  "body": body_message,
  "headers": {
      "Content-Type": content_type,
}
```
Here, `statusCode` and `body` are mandatory, while `headers` are optional. If you do not return this response structure when integrating with API Gateway, your client will receive a 502 HTTP error.

To simplify our code, this functionality has been encapsulated in the `utils` package.

</details>
	
## Step 3 - Schedule a message
1. Duplicate `get_subscribers` and rename the new folder `schedule_message`
2. Paste
```
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


@dataclass(frozen=True)
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
            tagging = "&".join(
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
into `app.py`

3. Paste
```
boto3==1.21.37
dacite==1.6.0
```
into `group_subscription_layer/utils/requirements.txt`

4. Paste
```
from datetime import datetime
from boto3.dynamodb.conditions import Key

def get_schedule_date_key(exact_date:datetime) -> str:
    return f"{exact_date.year}_{exact_date.month}_{exact_date.day}_{exact_date.hour}"

```
into `group_subscription_layer/utils/general.py`

5. Add to `template.yaml`
Under Resources
```
ScheduleFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: schedule_message/
      Handler: app.lambda_handler
      Runtime: python3.7
      Architectures:
        - x86_64
      Policies:
        - DynamoDBWritePolicy:
            TableName:
              !Ref ScheduledMessagesTable
        - S3WritePolicy:
            BucketName: !Ref ScheduledMessagesBucket
        - Statement:
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

Add new S3 bucket definition
```
ScheduledMessagesBucket:
    Type: AWS::S3::Bucket
```

Add a new table definition
```
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
```
Outputs:
  SubscribersList:
    Description: "API Gateway endpoint URL getting the subscribers"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/{group}/subscribers"
    
  ScheduleMessage:
    Description: "API Gateway endpoint URL for scheduling a message"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/{group}/schedule"
```

6. Paste 
```
import os

SUBSCRIBERS_TABLE = os.environ.get("SUBSCRIBERS_TABLE")
SCHEDULED_MESSAGES_TABLE = os.environ.get("SCHEDULED_MESSAGES_TABLE_NAME")
SCHEDULED_MESSAGES_BUCKET = os.environ.get("SCHEDULED_MESSAGES_BUCKET_NAME") 
```
into `group_subscription_layer/utils/consts.py`

7. Rerun `sam build && sam deploy`.

8. Test it using curl
`curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/serverless/schedule -H 'Content-Type: application/json' -d '{"subject":"Hello SLS workshop!", "body":"The workshop is not recorded.<h1>Welcome dear friends</h1>", "schedule_on":1649753447000}'`
9. Search for the file on the S3 bucket and the record in DynamoDB.

	<details>
  	<summary>👂 Speaker Notes</summary>	
	
	#### Using S3 to store content
	DynamoDB has a strict size limit of 400KB per record. Therefore, when storing content that exceeds this limit, it is recommended to use S3 to store the content and use a 'pointer' (an S3 object path) to the full content, as part of the DynamoDB record. In the above code, we are saving content into S3 and storing the object key as part of the DynamoDB record.
	```
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

	#### Principle of Least Priviliged Access - Take 2
	Sometimes AWS SAM does not have the right predefined IAM policies, in cases like that you should define your own policy. In our case in order to write an S3 object tag, you need `PutObjectTagging` permission, AWS SAM does not provide one, the only one it does provide is `S3FullAccessPolicy` which is too permissive.
	</detail>
	

## Step 4 - Send a message
	
1. Duplicate `get_subscribers` and rename the new folder `send_scheduled_messages`

3. Paste
```
import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from typing import List
from dacite import from_dict
from utils.models import Message

from utils.consts import SCHEDULED_MESSAGES_TABLE, SUBSCRIBERS_TABLE, SCHEDULED_MESSAGES_BUCKET, logger, SOURCE_EMAIL
from utils.general import get_schedule_date_key, get_subscribers_by_group

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
        responses = scheduled_messages_table.query(KeyConditionExpression=Key('scheduled_date').eq(get_schedule_date_key(now)))["Items"]
        messages_to_send = [response for response in responses if response.get("sent") is None ]
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
into `app.py`

4. Add
```
def get_subscribers_by_group(subscribers_table, group:str) -> list:
    return subscribers_table.query(KeyConditionExpression=Key('group_name').eq(group))["Items"] 
```
into `group_subscription_layer/utils/general.py`

5. Paste
```
from dataclasses import dataclass

@dataclass(frozen=True)
class Message:
    subject:str
    body: str
    schedule_on: int 
```
into `group_subscription_layer/utils/models.py`

6. Add
```
import logging

# previous stuff

SOURCE_EMAIL = os.environ.get("SOURCE_EMAIL")

logger = logging.getLogger()
logger.setLevel(logging.INFO) 
```
to `user-group/utils/consts.py`

7. Paste
```
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
into `user-group/get_subscribers/app.py`

9. Add to `user-group/template.yaml`
```
SendScheduledMessagesFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: send_scheduled_messages/
      Handler: app.lambda_handler
      Runtime: python3.7
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
          SOURCE_EMAIL: !Ref SourceEmail
          SCHEDULED_MESSAGES_TABLE_NAME: !Ref ScheduledMessagesTable
          SUBSCRIBERS_TABLE: !Ref SubscribersTable
      Events:
        MessageRule:
          Type: Schedule
          Properties:
            Schedule: 'rate(1 hour)'
            Name: MessageRule
```
Under the `Resources` section 


Add
```
Parameters:
  SourceEmail:
    Type: String
```
above `Resources` section.

10. Let's deploy it `sam build && sam deploy --guided`. Make sure to define `SourceEmail` parameter to your email
11. Next you need to verify your email (the one you defined at the previous step) under the SES service. Follow https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html#verify-email-addresses-procedure
12. You are ready to test it

#### Insights
* Talk about scheduling
* 
## Testing & Monitoring
1. Let's make sure your email is subscribed to the `serverless` group.
```
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/serverless/subscribers -H 'Content-Type: application/json' -d '{"email":"youreamil@mail.com"}'

curl https://<ap-id>.execute-api.us-east-1.amazonaws.com/Prod/serverless/subscribers
```
2. Let's schedule a message for this hour. For the timestamp use https://www.epochconverter.com/
```
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/serverless/schedule -H 'Content-Type: application/json' -d '{"subject":"Hello SLS workshop!", "body":"The workshop is not recorded.<h1>Welcome dear friends</h1>", "schedule_on":<epoch including milliseconds>}'
```
3. We can wait for the `SendScheduledMessagesFunction` Lambda to be triggered, but let's try to run it manually.
4. Go the AWS Lambda console, click on the `Test` tab, choose the default values and click on `Save.
<img width="1618" alt="image" src="https://user-images.githubusercontent.com/43570637/162713355-e8fc83a0-a406-43d0-8618-75ea67c658ef.png">
5. You should be getting a permission error
<img width="1624" alt="image" src="https://user-images.githubusercontent.com/43570637/162713582-464565ab-4080-4954-85be-c15a9e346931.png">

6. Let's add the missing permission. Add
```
SESCrudPolicy:
    IdentityName:
        !Ref SourceEmail
```
Under policies for the `SendScheduledMessagesFunction` Lambda

7. Redeploy (build & deploy)
8. A successful message was sent to your subscribers
<img width="1534" alt="image" src="https://user-images.githubusercontent.com/43570637/162719901-b1e78145-3050-44d4-bcfa-95b8deec3fc7.png">

## Deletion
After you've completed the workshop, you can delete all the resources you created by running sam delete and answering 'y' to all prompts. Please note that the S3 bucket we created will not be deleted because it contains objects. You must delete these objects before attempting to remove the workshop resources.
<img width="781" alt="CleanShot 2023-05-16 at 17 29 51@2x" src="https://github.com/aws-hebrew-book/building-serverless-in-hebrew-workshop/assets/110536677/b1ae99b0-d461-43e7-9623-d910bf94585b">




