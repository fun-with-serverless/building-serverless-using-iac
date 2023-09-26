## Architecture

The "Add Subscribers" function adds a single subscriber to a mailing list.

## Implementation
* Duplicate `get_subscribers` and rename the new folder `add_subscriber`
* Paste

```{ .py .annotate }
import json
import boto3
from datetime import datetime

from utils.consts import SUBSCRIBERS_TABLE
from utils.api_gw_helpers import require_group, lambda_response

# Cache client
session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(SUBSCRIBERS_TABLE)

@require_group #(1)!
def lambda_handler(event, context):
    # Get group name
    group = event["group_name"] #(2)!
    email = json.loads(event.get("body", {})).get("email")
    if email:
        response = table.put_item(
           Item={
                "group_name": group,
                "subscriber": email,
                "date_joined": int(datetime.now().timestamp() * 1000)
            }
        )

        return lambda_response({"message":f"{email} added successfully"}) #(3)!

    return lambda_response({"err":"Email not found"}, status_code=500)
```

1. Use annotations to encapsulate common behavior.
2. The annotation pushes this attribute into the dictionary.
3. Encapsulate the API Gateway return value.

into `app.py`

* We are going to create a Lambda Layer. Create a new folder `group_subscription_layer` and inside create `utils` python package. It is a folder with `__init__.py` file.
<img width="158" alt="CleanShot 2023-05-16 at 16 08 08@2x" src="https://github.com/aws-hebrew-book/building-serverless-using-iac/assets/110536677/4b775466-b89a-456b-bc86-5c2176c7d198">

* Paste 
``` { .py .annotate }
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

* Paste 
```py
import os
SUBSCRIBERS_TABLE = os.environ["SUBSCRIBERS_TABLE"]
``` 
into `group_subscription_layer/utils/consts.py`

* Add

``` { .yaml .annotate }
SharedLayer:
    Type: AWS::Serverless::LayerVersion #(1)!
    Properties:
      LayerName: group-subscription-layer
      Description: Utility layer used by subscription application
      ContentUri: group_subscription_layer/
      CompatibleRuntimes: #(2)!
        - python3.11
    Metadata:
      BuildMethod: python3.11 #(3)!

AddSubscriberFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: add_subscriber/
      Handler: app.lambda_handler
      Runtime: python3.11
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
        - !Ref SharedLayer #(4)!
      Events:
        Subscribers:
          Type: Api 
          Properties:
            Path: /{group}/subscribers
            Method: post
```

1. Lambda Layer also has a resource type.
2. Which Lambda runtimes can attach the Layer. In our case, it's only one, but you can build the layer using Python 3.9, for example, and support other Python versions as well.
3. We tell AWS SAM how to build and package the layer. Specifically, here we use a standard Python build, which means using `pip`.
4. We attache the layer to the Lambda.

to `template.yaml` under `Resources`

* Add
```
Layers: 
	- !Ref SharedLayer
```
to under `template.yaml` under `GetSubscribersFunction` function definition.
9. Simplify `get_subscribers/app.py`
```py
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

## Insights
#### Python Decorators
> A decorator is a function that takes another function and extends the behavior of the latter function without explicitly modifying it.

A Python decorator is a form of syntactic sugar that allows us to modify a function's behavior using an `@<function_name>` annotation. In our scenario, we consistently extract the group name from the path parameter, and if it's not found, we want to return a valid error. We can use a decorator to enhance a Lambda handler by injecting the necessary parameters into the event.

We've defined a decorator called `require_group` as part of the utils package, which incorporates `group_name` into the event. If the path parameter is not found, it returns a `500` error to the caller.

Example:
``` py
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
 
``` yaml
Metadata:
	BuildMethod: python3.11
```
into the layer specification, we are directing AWS SAM to construct the layer by installing the appropriate dependencies (utilizing pip in our scenario). Absence of this specification would result in AWS SAM merely zipping and deploying the layer, without any dependency installation.
	
You can view the layer in the AWS Console.
![CleanShot 2023-05-25 at 13 34 54@2x](https://github.com/aws-hebrew-book/building-serverless-using-iac/assets/110536677/7c3cfe9f-f593-4041-8b33-f4d9eb89b6b4)

	
#### API Gateway response
API Gateway requires a specific response structure:
``` json
{
  "statusCode": str(status_code),
  "body": body_message,
  "headers": {
      "Content-Type": content_type,
}
```
Here, `statusCode` and `body` are mandatory, while `headers` are optional. If you do not return this response structure when integrating with API Gateway, your client will receive a 502 HTTP error.

To simplify our code, this functionality has been encapsulated in the `utils` package.

## Exercises
* Add Python 3.10 to the list of supported runtimes for the layer.
??? tip
    1. Install python 3.10 using pyenv
    2. Then add the missing runtime.
* Add first and surname to the body of the `add-subscriber` lambda and then add these values to the DynamoDB table. Do you need to add these attributes to the table definition?
??? tip
    You only need to add attributes to the table definition if they are either the hash key or the range key.
* Try removing the the `statusCode` attribute from the API Gateway response. Invoke the Lambda through the console, now try through the API. What happens? Why?
??? tip
    The Lambda will run successfully, but the the integration between the Lambda and the API Gateway will fail, resulting in an invalid response. Any idea how to debug it? :wink:
