Writing code and creating resources directly through the AWS Console is fun and above all, very fast; a few button clicks and you're ready to go. This approach is excellent for experiments and prototype building. However, one of the central issues with this method is that it does not allow for automation. In other words, you would want the code and services you've written to be precisely deployable across multiple AWS environments without having to manually follow a document and risk making mistakes.

To address this, various tools and processes have been introduced in recent years that allow you to define your resource configuration and creation, such as Lambda functions, as code. These tools and processes are known as Infrastructure as Code, or IAC for short. Once your work methodology becomes code-based, many elements from the code life cycle come into play. This includes code reviews, testing, and more, enabling you to ensure that your configuration is of high quality and, most importantly, operates consistently.

Here's a small AWS Serverless Application Model (SAM) example that defines a Lambda function and an API Gateway:
```yaml
Resources:
  HelloWorldFunction:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: hello-world/
      Handler: app.lambdaHandler
      Runtime: nodejs14.x
      Events:
        HelloWorld:
          Type: Api 
          Properties:
            Path: /hello
            Method: get
```

This is a classic example of Infrastructure as Code (IAC). Instead of going to the AWS Console and manually creating these resources, you define everything in a YAML file. This code can be version controlled, reviewed, and deployed programmatically, thereby allowing for automated, consistent deployments.

We will begin by exploring AWS SAM and then move on to AWS CDK, two different IaC tools that share the same objective.
