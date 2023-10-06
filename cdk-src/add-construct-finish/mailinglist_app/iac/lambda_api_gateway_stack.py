from .api_gw_lambda_construct import LambdaApiGatewayConstruct
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
        get_subscribers_function = lambda_python.PythonFunction(
            self,
            "GetSubscribersFunction",
            entry="mailinglist_app",
            index="src/get_subscribers/app.py",
            handler="lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            environment={"SUBSCRIBERS_TABLE": table.table_name},
            layers=[layer],
        )

        add_subscriber_function = lambda_python.PythonFunction(
            self,
            "AddSubscriberFunction",
            entry="mailinglist_app",
            index="src/add_subscriber/app.py",
            handler="lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            environment={"SUBSCRIBERS_TABLE": table.table_name},
            layers=[layer],
        )

        api = LambdaApiGatewayConstruct(self, "LambdaAPIGWMailingList")
        api.add_lambda_integration(
            get_subscribers_function, "{group}/subscription", "GET"
        )
        api.add_lambda_integration(
            add_subscriber_function, "{group}/subscribers", "POST"
        )

        table.grant_read_data(get_subscribers_function)
        table.grant_write_data(add_subscriber_function)
