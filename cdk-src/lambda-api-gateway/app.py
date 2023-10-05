#!/usr/bin/env python3

import aws_cdk as cdk

from lambda_api_gateway.lambda_api_gateway_stack import LambdaApiGatewayStack


app = cdk.App()
LambdaApiGatewayStack(app, "LambdaApiGatewayStack")

app.synth()
