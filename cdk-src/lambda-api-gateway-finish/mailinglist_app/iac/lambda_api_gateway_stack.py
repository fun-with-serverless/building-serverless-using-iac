from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,
    aws_apigateway as apigw,
    aws_lambda,
    aws_dynamodb as ddb,
    CfnOutput
)


class LambdaApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = ddb.Table(
            self,
            "SubscribersTable",
            partition_key={"name": "group_name", "type": ddb.AttributeType.STRING},
            sort_key = {"name": "subscriber", "type": ddb.AttributeType.STRING}
        )

        get_subscribers_function = lambda_python.PythonFunction(
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

        api = apigw.LambdaRestApi(
            self,
            "MailingListAPI",
            handler=get_subscribers_function,
            proxy=False,
            integration_options=apigw.LambdaIntegrationOptions(allow_test_invoke=False),
        )

        group = api.root.add_resource("{group}")
        subscribers = group.add_resource("subscribers")
        subscribers.add_method("GET")

        table.grant_read_data(get_subscribers_function)

        CfnOutput(self, "GroupURL", value=f"{api.url}{{group}}/subscribers")
