In this section, we'll deploy a Lambda function linked to API Gateway. We'll begin by crafting the IaC for `get-subscribers`.

![get-subscribers](https://github.com/fun-with-serverless/building-serverless-using-iac/assets/110536677/2a6c83f7-8988-4e32-9bae-cd69d6fc3843)

## Implementation
* Navigate to `lambda-api-gateway-start-here` located within `cdk-src`.
* Our stack is already set up in `app.py`, so our modifications will focus on `lambda_api_gateway_stack.py`.
* Before moving forward, ensure you create and activate your `virtualenv`. Since `virtualenv` isn't included in git, set it up using `python -m venv .venv` or your preferred method, such as [poetry](https://python-poetry.org/), then activate with `source .venv/bin/activate`.
* Install the necessary dependencies with `pip install -r requirements.txt`.
*   While code organization can be subjective, a best practice in CDK is to structure it as:

``` {.bash .annotate}
|--app1
|----iac #(1)!
|----application code #(2)!
|--app2
|----iac
|----application code
app.py #(2)!
```

1. CDK code related to this app is found here. Usually, each app will create a separate stack.
2. The source code for the application itself.
2. Tie all the stacks in a single file - `app.py`.

Where each app corresponds to its own stack.

* Insert the content

``` {.python .annotate}
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python, #(1)!
    aws_apigateway as apigw,
    aws_lambda,
    aws_dynamodb as ddb,
    CfnOutput
)


class LambdaApiGatewayStack(Stack): #(2)!
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None: #(3)!
        super().__init__(scope, construct_id, **kwargs)

        table = ddb.Table( #(4)!
            self,
            "SubscribersTable",
            partition_key={"name": "group_name", "type": ddb.AttributeType.STRING},
            sort_key = {"name": "subscriber", "type": ddb.AttributeType.STRING}
        )

        get_subscribers_function = lambda_python.PythonFunction( #(5)!
            self,
            "GetSubscribersFunction",
            entry="mailinglist_app",
            index="src/app.py",
            handler="lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            environment={
                "SUBSCRIBERS_TABLE": table.table_name
            }
        )

        api = apigw.LambdaRestApi( #(6)!
            self,
            "MailingListAPI",
            handler=get_subscribers_function,
            proxy=False, #(7)!
            integration_options=apigw.LambdaIntegrationOptions(allow_test_invoke=False), #(8)!
        )

        group = api.root.add_resource("{group}") #(9)!
        subscribers = group.add_resource("subscribers")
        subscribers.add_method("GET")

        table.grant_read_data(get_subscribers_function) #(10)!

        CfnOutput(self, "GroupURL", value=f"{api.url}{{group}}/subscribers") #(11)!

```

1. Start by importing the necessary constructs. Beyond the built-in constructs, we'll also incorporate an alpha construct named `aws_lambda_python_alpha`.
2. Here, we're creating a stack.
3. Each stack receives a parent construct and a logical ID.
4. We'll begin by specifying our initial resource: a DynamoDB table. It's crucial to note the order of definition; the table must be established before the Lambda since we assign permissions to it subsequently.
5. Next, define a Lambda function.
6. Establish a Rest API Gateway linked to the aforementioned Lambda.
7. For more granular control over our API Gateway resources and methods (refer to item 9), ensure the `proxy` attribute is set to `false`. If not adjusted, all http methods will be configured on the root path.
8. When set to `True`, an additional permission is appended to the AWS Lambda resource policy, enabling the `test-invoke-stage` stage to invoke this handler. If set to `False`, the function can only be accessed via the deployment endpoint.
9. Append resources and methods. It's vital to differentiate between path parameters and the remaining parts of the path.
10. Bestow the Lambda with the necessary permissions to interface with DynamoDB.
11. As a part of the CDK deployment process, output the complete HTTP path.

into `iac/lambda_api_gateway_stack.py`

* Deploy the application. Run `cdk deploy`
* Try invoking the API listed in the outputs.
```
Outputs:
LambdaApiGatewayStack.GroupURL = https://xxxxxx.execute-api.us-east-1.amazonaws.com/prod/{group}/subscribers
LambdaApiGatewayStack.MailingListAPIEndpoint92BB94CD = https://xxxxxx.execute-api.us-east-1.amazonaws.com/prod/
Stack ARN:
```


## Insights

### Constructs
Constructs form the core of every CDK application. In the aforementioned code, we employed three constructs to establish a Lambda function, an API Gateway, and a DynamoDB table. Additionally, we devised a construct symbolizing a stack, consumed by the CDK app outlined in `app.py`.

Your CDK endeavors will likely follow this pattern: importing various constructs, utilizing them to create resources, and bundling everything within a stack.

### Alpha Constructs
Constructs come in different maturity levels; some are designated as "preview," meaning they aren't integral to the official SDK. These constructs possess distinct packages and necessitate separate installations. In our example, we adopted a construct that enhances the packaging procedure for an AWS Lambda scripted in Python. The conventional Lambda construct demands manual construction of the deployment package, like installing requirements and zipping. The alpha construct simplifies this by anticipating a Python packaging file, such as `requirements.txt` or `pyproject.toml`.

Typically, preview constructs are appended with an `-alpha` suffix.

Bear in mind, the alpha Python construct mandates Docker.

### Order Importance
Contrary to the template crafted using AWS SAM, our script here is imperative, making execution sequence pivotal. This is because we're sharing parameters across various objects, necessitating certain objects to be instantiated first for subsequent code use. We required the table name within the Lambda environment settings, prompting us to initialize the table at the outset. In AWS SAM, the underlying engine (CloudFormation) determines the creation sequence.

### Outputs
Diverging from AWS SAM, which mandates explicit output definitions to view any, CDK provides certain default outputs. For instance, without any specific definition, you'll receive the HTTP address in the output, resembling:
```
LambdaApiGatewayStack.MailingListAPIEndpoint92BB94CD = https://yyyyyy.execute-api.us-east-1.amazonaws.com/prod/
```
For customized output with varying data, the `CfnOutput` construct can be utilized.


## Exercises
* Include the DynamoDB table name in the output.
* Enhance the stack by adding the `add_subscriber` lambda.
