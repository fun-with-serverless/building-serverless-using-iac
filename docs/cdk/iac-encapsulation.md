One of the amazing capabilities of CDK is the ability to encapsulate common IaC behaviors into a construct. This allows you to reuse tested constructs and reduce code bugs. In this section, we are going to encapsulate the API GW -> Lambda resources into a single construct and use it across the board.

We will encapsulate the API GW -> Lambda integration, which is a pivotal part of our architecture. The construct will create a single API Gateway and attach Lambda functions using an object `add` method.

## Implementation
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
            resource = resource.add_resource(part)
        resource.add_method(
            method, apigw.LambdaIntegration(lambda_integration, allow_test_invoke=False)
        )
        CfnOutput(self, f"{method} {path}", value=f"{self.api.url}{path}") #(5)!


```

1. Each Construct inherits from `Construct`.
2. We're creating a single API Gateway where we'll make modifications, such as adding Lambda integrations. It's up to you whether you want to export the API as a public property.
3. This is where the magic occurs: you add a Lambda integration by invoking this method. We expect to receive a Lambda construct as a parameter.
4. We need to split the path since each resource in API GW can only have one path element.
5. We automatically output the new integration.


## Exercises
* Add all the Lambdas from the previous AWS SAM section to the stack using this construct.
* Incorporate the DynamoDB table into this construct. Consider how you can encapsulate it.
