In this final chapter of the AWS SAM section, you'll implement a piece of functionality entirely on your own. This will require you to create a new Lambda function using Lambda Power Tools and add its configuration to AWS SAM.

As you're well aware, the functionality we've developed is open to the world. This means anyone with your application's web link can access it and start scheduling messages. To address this, we aim to add some basic authentication. In the current chapter, you'll implement a Lambda authentication flow.

## What is Lambda Authorizers
> A Lambda authorizer (formerly known as a custom authorizer) is an API Gateway feature that uses a Lambda function to control access to your API.


[~AWS~ ~Documentation~](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)

API Gateway Lambda authorizers are essentially custom-built Lambda functions that control access to your API endpoints. When a client makes a request to a secured endpoint, the Lambda authorizer executes and inspects the incoming request headers, query string parameters, or JWT tokens to determine if the request is authorized.

Here's the flow:

* A client sends a request to an API Gateway endpoint.
* Before routing to the actual backend service, API Gateway triggers the Lambda authorizer.
* The Lambda authorizer examines the request to identify credentials or tokens (e.g., API key, OAuth token).
* Based on the extracted information, the Lambda function makes an allow, deny, or unauthorized decision, which can involve anything from simple key matching to complex business logic or even third-party API calls.
* API Gateway caches this decision for a configurable period (TTL), so subsequent requests with the same tokens don't trigger the Lambda authorizer again during this period.

![auth](https://github.com/fun-with-serverless/building-serverless-using-iac/assets/110536677/43d504c2-4d68-403f-8827-7337fd44a179)


## Implementation Pointers
* You will implement a Lambda authorizer solely for the message scheduling flow, while keeping the rest of the Lambdas open to the world.
* To keep things simple, let's assume we have just a single user, and that their password is stored as a secret in Secrets Manager. Check the [official template documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html). Use the [Lambda Power Tools](https://docs.powertools.aws.dev/lambda/python/latest/utilities/parameters/) to extract the secrets
* In order to define a Lambda authorizer, you need to define the API Gateway as a seperate SAM resource - 
```yaml
RootApiRust:
    Type: AWS::Serverless::Api
    Properties:
      StageName: Prod
      Auth: # <-- Check this
      ...
``` 
Check the [official template documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html#sam-api-auth)
* Next, you need to connect the new resource to the Lambda event.
* To implement the Lambda logic, don't reinvent the wheel; use [Lambda Power Tools](https://docs.powertools.aws.dev/lambda/python/latest/utilities/data_classes/#api-gateway-authorizer).

Good Luck!

