## Implementation
1. Go to `start-here-step1`
3. You should see a basic structure of our SAM aplication for managing user groups.
5. Add `boto3==1.21.37` to `get_subscribers/requirements.txt`
6. Paste
``` yaml
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
``` py
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

## Insights

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