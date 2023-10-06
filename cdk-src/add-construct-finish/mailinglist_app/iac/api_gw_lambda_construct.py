from constructs import Construct
from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_apigateway as apigw,
    CfnOutput,
)


class LambdaApiGatewayConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.api = apigw.RestApi(
            self,
            "MailingListAPI",
        )

    def add_lambda_integration(
        self, lambda_integration: lambda_python.PythonFunction, path: str, method: str
    ) -> None:
        path_parts = path.split("/")
        resource = self.api.root
        for part in path_parts:
            resource = resource.get_resource(part) or resource.add_resource(part)
        resource.add_method(
            method, apigw.LambdaIntegration(lambda_integration, allow_test_invoke=False)
        )
        CfnOutput(self, f"{method} {path}", value=f"{self.api.url}{path}")
