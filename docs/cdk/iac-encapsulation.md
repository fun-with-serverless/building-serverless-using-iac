One of the amazing capabilities of CDK is the ability to encapsulate common IaC behaviors into a construct. This allows you to reuse tested constructs and reduce code bugs. In this section, we are going to encapsulate the API GW -> Lambda resources into a single construct and use it across the board.

We will encapsulate the API GW -> Lambda integration, which is a pivotal part of our architecture. The construct will create a single API Gateway and attach Lambda functions using an object `add` method.

## Implementation
### Adding a construct
* Add a new file named `iac/api_gw_lambda_construct.py`, it will containt the construct we are building.
* Insert the content into `iac/api_gw_lambda_construct.py`.

``` {.python .annotate}
from constructs import Construct
from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_apigateway as apigw,
    CfnOutput,
)


class LambdaApiGatewayConstruct(Construct): #(1)!
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.api = apigw.RestApi( #(2)!
            self,
            "MailingListAPI",
        )

    def add_lambda_integration( #(3)!
        self, lambda_integration: lambda_python.PythonFunction, path: str, method: str
    ) -> None:
        path_parts = path.split("/") #(4)!
        resource = self.api.root
        for part in path_parts:
            resource = resource.get_resource(part) or resource.add_resource(part) #(5)!
        resource.add_method(
            method, apigw.LambdaIntegration(lambda_integration, allow_test_invoke=False)
        )
        CfnOutput(self, f"{method} {path}", value=f"{self.api.url}{path}") #(6)!


```

1. Each Construct inherits from `Construct`.
2. We're creating a single API Gateway where we'll make modifications, such as adding Lambda integrations. It's up to you whether you want to export the API as a public property.
3. This is where the magic occurs: you add a Lambda integration by invoking this method. We expect to receive a Lambda construct as a parameter.
4. We need to split the path since each resource in API GW can only have one path element.
5. We can't add the same resource twice, so check if it exists.
6. We automatically output the new integration.

### Using a construct
A construct is a regular Python class; just import it and use it directly in your code. Paste the following code to `lambda_api_gateway_stack.py`

``` {.python .annotate}
from .api_gw_lambda_construct import LambdaApiGatewayConstruct #(1)!
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,
    aws_lambda,
    aws_dynamodb as ddb,
)


class LambdaApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = ddb.Table(
            self,
            "SubscribersTable",
            partition_key={"name": "group_name", "type": ddb.AttributeType.STRING},
            sort_key={"name": "subscriber", "type": ddb.AttributeType.STRING},
        )

        layer = lambda_python.PythonLayerVersion(
            self,
            "MailingListLayer",
            entry="mailinglist_app/src/group_subscription_layer",
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
        )
        get_subscribers_function = lambda_python.PythonFunction( #(2)!
            self,
            "GetSubscribersFunction",
            entry="mailinglist_app",
            index="src/get_subscribers/app.py",
            handler="lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            environment={"SUBSCRIBERS_TABLE": table.table_name},
            layers=[layer],
        )


        api = LambdaApiGatewayConstruct(self, "LambdaAPIGWMailingList") #(3)!
        api.add_lambda_integration( #(4)!
            get_subscribers_function, "{group}/subscription", "GET"
        )

        table.grant_read_data(get_subscribers_function)


```

1. Import the class.
2. Continue creating the Lambda construct as we did previously.
3. Instantiate the construct.
4. Add the integration.

Deploy using `cdk deploy`


## Exercises
* Add all the Lambdas from the previous AWS SAM section to the stack using this construct.
* Incorporate the DynamoDB table into this construct. Consider how you can encapsulate it.
