In this section, we'll deploy a Lambda function linked to API Gateway. We'll begin by crafting the IaC for `get-subscribers`.

![get-subscribers](https://github.com/fun-with-serverless/building-serverless-using-iac/assets/110536677/2a6c83f7-8988-4e32-9bae-cd69d6fc3843)

## Implementation
* Go to `lambda-api-gateway` found under `cdk-src`
* We already have our stack created in `app.py`, so we will only change `lambda_api_gateway_stack.py`.
* Before proceeding, make sure to create and then activate your `virtualenv`. The `virtualenv` is not part of git. You can create a virtualenv using `python -m venv .venv` or your favorite tool ([poetry](https://python-poetry.org/) 👑) and then `source .venv/bin/activate` to activate it.
* Install the relevant dependencies using `pip install -r requirements.txt`.
* Code organization is usually opinianated, however it is best practice to organize your code in CDK in the following way:
|--app1
|----iac
|----application code
|--app2
|----iac
|----application code
app.py

When each app has its own stack.
* Paste into `iac/lambda_api_gateway_stack.py`

``` {.python .annotate}

```



## Exercises
* Remove the policy from the Lambda definition. Try invoking the Lambda. What happens, and why?
??? tip
    1. Use AWS CloudWatch to debug your Lambda function.
    2. Type "CloudWatch" in the search bar, then go to "Logs" -> "Log Groups" and search for your Lambda function by name.
* Improve the response JSON by adding an attribute that contains the number of items, in addition to the list itself.
* Add the DynamoDB table name to the `Output` section of the `template.yaml` file.
??? tip
    1. Look at the Return values section in https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html
    2. Use `!Ref` or `!Sub` to pull the value.
