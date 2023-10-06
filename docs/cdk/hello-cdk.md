## Prepare your machine
I highly recommend using Cloud9. AWS Cloud9 is a cloud-based integrated development environment (IDE) that allows you to write, run, and debug code from any web browser. Don't opt for the bare-minimum machine type; a 2-core machine (t2.small) is sufficient. If you're using Cloud9, you can execute the script located at `./scripts/update_python_on_cloud9.sh` to prepare your environment. Use Linux 2 as the OS.

If you prefer to use your own environment, please follow these steps:

1. Install CDK. Execute `npm install -g aws-cdk`.
2. Verify it works as expected, run `cdk --version`.
3. Check that you have a working Python environment, run `python --version`. In case you are getting an error:
   - Install [pyenv](https://github.com/pyenv/pyenv)
   - Install Python 3.11 - `pyenv install 3.11`
   - Make it global - `pyenv global 3.11`

4. Clone `https://github.com/fun-with-serverless/building-serverless-using-iac.git`

## What is AWS CDK ?
Just like AWS SAM, AWS CDK is an IaC framework that allows you to define your infrastructure as code, but with a twist. If you're familiar with CDK, you can skip the next section.

AWS SAM, Terraform, Cloudformation and other IaC as well are declarative IaC. Declarative IaC is an approach where developers specify the desired end state of the infrastructure without detailing the steps to achieve it. The underlying IaC tooling then determines the necessary actions to bring the infrastructure to that state. 
Let's look at a declarative IaC example using AWS SAM to create a simple Lambda function and an API Gateway endpoint:

```yaml
Resources:
  HelloWorldFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: nodejs14.x
      CodeUri: ./code/
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

The provided AWS SAM example is declarative because it specifies what the desired end state of the infrastructure should be, rather than how to achieve it.

The HelloWorldFunction resource simply states that there should exist a Lambda function with certain properties (like its handler, runtime, and code location). It doesn't specify the steps to create the function.

The Events property states that an API Gateway endpoint should be linked to this function at the specified path (/hello) with the given method (get). Again, it doesn't detail how to set up the API Gateway, how to link it to the Lambda function, or any other procedural steps.

On the other hand Imperative IaC defines the specific steps and commands that must be executed to achieve a desired infrastructure state. Instead of merely describing the desired end state, it provides a sequence of actions to be taken to create or modify the infrastructure. 

Let's represent this with a pseudo-code that mirrors the process of setting up the resources mentioned in the declarative AWS SAM example:
```javascript
function createLambdaFunction() {
  if (!lambdaFunctionExists("HelloWorldFunction")) {
    setupLambda({
      name: "HelloWorldFunction",
      handler: "index.handler",
      runtime: "nodejs14.x",
      codeLocation: "./code/"
    });
  }
}

function setupAPIGatewayForLambda(lambdaName) {
  if (!apiGatewayExistsForLambda(lambdaName)) {
    createAPIGateway({
      path: "/hello",
      method: "GET",
      linkedFunction: lambdaName
    });
  }
}

createLambdaFunction();
setupAPIGatewayForLambda("HelloWorldFunction");
```
The `createLambdaFunction` function checks if a Lambda function with the name "HelloWorldFunction" exists (lambdaFunctionExists). If it doesn't, it sets up a new Lambda function with specified properties using the setupLambda command.

The `setupAPIGatewayForLambda` function checks if an API Gateway exists for the given Lambda function (apiGatewayExistsForLambda). If one doesn't exist, it creates an API Gateway with the specified path, method, and links it to the given Lambda function using the createAPIGateway command.

Finally, the two main functions are called in sequence: first to create the Lambda function and then to set up the API Gateway for that function.

This pseudo-code provides step-by-step actions (imperative) to achieve the desired infrastructure state.

CDK is an imperative IaC, and the process of writing it resembles writing standard code in any modern language.

### CDK bindings
CDK bindings are the libraries provided by the AWS Cloud Development Kit (CDK) that allow developers to define cloud infrastructure in their preferred programming language. These bindings translate high-level programmatic constructs into CloudFormation templates. This makes it possible for developers to leverage the full expressiveness of familiar programming languages, such as Python, TypeScript, Java, and others, to define and model their cloud resources.

Examples:

1. **Python**:
   ```python
   from aws_cdk import core, aws_s3 as s3

   class MyStack(core.Stack):
       def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
           super().__init__(scope, id, **kwargs)
           s3.Bucket(self, 'MyFirstBucket')
   ```

2. **NodeJS (TypeScript)**:
   ```typescript
   import * as cdk from 'aws-cdk-lib';
   import * as s3 from 'aws-cdk-lib/aws-s3';

   export class MyStack extends cdk.Stack {
       constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
           super(scope, id, props);
           new s3.Bucket(this, 'MyFirstBucket');
       }
   }
   ```

In both examples, we define a simple CDK stack that creates an S3 bucket. The structure is similar, but the syntax is tailored to the specifics of each programming language.

In thise workshop we will use the Python bindings.

In the following section we will build a simple hello world application using SAM.
### CDK Example
* Create a new folder named `iac-cdk-workshop` and navigate to it using `cd iac-cdk-workshop`.
* Initialize a CDK example using a template with the command `cdk init sample-app --language=python`.
* Since we are using Python, the CDK will automatically create a `virtualenv` for you. Activate the virtualenv by running `source .venv/bin/activate`.
??? info
  Python virtualenv is a tool that allows developers to create isolated Python environments to ensure dependencies are kept consistent and separate for different projects.
* Install the necessary dependencies using the command `pip install -r requirements.txt`.
* The CDK code for our project consists of two files: `app.py` and `iac_cdk_workshop/iac_cdk_workshop_stack.py`.
```python
# app.py
#!/usr/bin/env python3

import aws_cdk as cdk

from iac_cdk_workshop.iac_cdk_workshop_stack import IacCdkWorkshopStack


app = cdk.App()
IacCdkWorkshopStack(app, "IacCdkWorkshopStack")

app.synth()

```

When executing the CDK CLI, it searches for `app.py`. This file, when run, programmatically creates the CloudFormation stacks that will be deployed to your AWS account.
The CDK translates your imperative Python code into a declarative CloudFormation template. While you can define multiple CloudFormation stacks using CDK, this example creates a single stack named `IacCdkWorkshopStack`.

Typically, `app.py` remains simple, and modifications are made in the file representing the CloudFormation stack.

```python
# iac_cdk_workshop_stack.py
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)


class IacCdkWorkshopStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "IacCdkWorkshopQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "IacCdkWorkshopTopic"
        )

        topic.add_subscription(subs.SqsSubscription(queue))

```

In the provided code, we inherit from `Stack` and create two AWS resources: SQS and SNS. Note that instantiating a new object, whether it's SQS or Stack, requires at least two parameters:
1. A construct - This is a fundamental building block representing a "cloud component," encapsulating all that AWS CloudFormation needs to create the component.
2. A logical name that will be used in the final CloudFormation template.

#### Synthesize 
As mentioned earlier, the CDK translates your imperative Python code into a declarative CloudFormation template. To view the corresponding CloudFormation representation, run `cdk synth`, and the output will be displayed on the screen.

Give it a try.

#### Bootstraping
The CDK handles its own setup, necessitating specific AWS resources to function correctly, such as an S3 bucket for uploading your code, AWS ECR for storing Docker images when required, and certain IAM roles, among others. The CDK initializes these resources only once for each AWS region, so there's no need to repeat this process multiple times in the same region.

Run `cdk bootstrap`.

You should observe an output similar to `⏳  Bootstrapping environment ...`.


#### Deploying
You're now set to deploy your hello world application. Execute `cdk deploy`. This command will automatically synthesize the code, so there's no need to do it manually, and it will handle the deployment process for you. Any changes to IAM will prompt for your confirmation; when asked, approve with `y`.

In a few moments, the deployment will conclude. You can then review the stack and its associated resources within CloudFormation.

#### Detroying
Once you've finished, you can remove the stack by executing `cdk destroy`.