from constructs import Construct
from aws_cdk import (
    Stack,
)


class LambdaApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

