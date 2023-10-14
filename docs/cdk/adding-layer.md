Before moving on to the rest of the implementation, I want to pause and explain how to implement a Lambda layer in CDK. Thankfully, CDK provides a construct that makes layer creation a breeze.

## Implementation
* Change the folder structure to
```
|--app1
|----iac
|----src
|-------get_subscribers
|-------group_subscription_layer
app.py
```
Copy the contents of `group_subscription_layer` from the AWS SAM project to the one found here. Also, move the previous content found under `src` into `get_subscribers`.


* Insert the content into `iac/lambda_api_gateway_stack.py`.

``` {.python .annotate}
layer = lambda_python.PythonLayerVersion( 
    self,
    "MailingListLayer",
    entry="mailinglist_app/src/group_subscription_layer",
    compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11] #(1)!
)
# omitted 
get_subscribers_function = lambda_python.PythonFunction(
    self,
    "GetSubscribersFunction",
    entry="mailinglist_app",
    index="src/get_subscribers/app.py",
    handler="lambda_handler",
    runtime=aws_lambda.Runtime.PYTHON_3_11,
    environment={"SUBSCRIBERS_TABLE": table.table_name},
    layers=[layer], #(2)!
)
```

1. When adding the layer, ensure you define the correct compatibility runtime. The default is `3.7``, and using it may result in failure.
2. Attach the layer to the Lambda.
