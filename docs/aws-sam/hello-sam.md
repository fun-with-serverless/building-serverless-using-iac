## Prepare your machine
1. Install AWS SAM. Follow [https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
2. Verify it works as expected, run `sam --version` you should be getting something like `> SAM CLI, version 1.96.0`. Pay attention that the version might change
3. Check that you have a working Python environment, run `python --version`. In case you are getting an error:
   - Install [pyenv](https://github.com/pyenv/pyenv)
   - Install Python 3.11 - `pyenv install 3.11`
   - Make it global - `pyenv global 3.11`

4. Clone `https://github.com/fun-with-serverless/building-serverless-using-iac.git`

## What is AWS SAM ?
The application will be constructed using AWS SAM. The next section provides an overview of AWS SAM; if you already have experience with this service, feel free to skip ahead.

[Amazon Web Services Serverless Application Model (AWS SAM)](https://aws.amazon.com/serverless/sam/) is a framework for building serverless applications. It simplifies the process of creating and managing resources used in serverless applications using AWS services like Lambda, API Gateway, and DynamoDB. 
AWS SAM uses a template file to define your serverless application and its resources, providing a streamlined and consistent method for deploying complex serverless applications. 
By leveraging AWS SAM, you can more easily automate deployment processes, test your applications locally before deploying, and even generate boilerplate code for common serverless patterns.

In the following section we will build a simple hello world application using SAM.

1. `sam init`
2. Choose `AWS Quick Start Templates`
3. Next choose `Hello World Example`
4. If you choose to use the most popular runtime and package type, then make sure that Python 3.9 is installed
6. Choose `Python 3.11`
7. Choose `Zip`
8. For project name, choose the default
<img src="https://github.com/aws-hebrew-book/building-serverless-in-hebrew-workshop/assets/110536677/4bf1a5ca-cdbe-455b-a29d-2ce4a4ddddf0" width="400">

10. You need to build the sam packge 
11. Go to the folder the template created `cd sam-app`
12. Run `sam build` and next run `sam deploy --guided`. You should run guided each time you want to add something to the sam configuration file or create it for the first time.
13. When asked `HelloWorldFunction may not have authorization defined, Is this okay?` choose `y`
14. The rest can be defaults
15. `Deploy this changeset?` choose `y`
16. Give the deployment a try, you should see under `Outputs` the `API Gateway endpoint URL`, copy the URL and try it on browser.
17. When done, run `sam delete` to remove the stack.

## Insights

### Template
	
At the core of every AWS SAM application lies the template.yaml, a file that outlines the resources utilized by the app. Our sample template file is split into four main sections:
  <ol>
    <li>
      Header - This section provides the template's definition and description, which are displayed in the CloudFormation console.
    </li>
    <li>
      Global - This section contains global configurations that apply to all resources. In our case, we have set default values for the timeout and memory of all Lambdas to 3 seconds and 128 MB, respectively.
    </li>
    <li>
      Resources - This section details the resources to be established as part of the application. In our case, it is a Lambda function.
    </li>
    <li>
      Outputs - This section enumerates output values that can be imported into other stacks (for creating cross-stack references), returned in responses (to provide stack call descriptions), or viewed on the AWS CloudFormation console.
    </li>
  </ol>

The heart of your AWS SAM template file is the resource section, let's deep dive into its content.


```{ .yaml .annotate }
HelloWorldFunction: #(1)!
    Type: AWS::Serverless::Function #(2)!
    Properties:
      CodeUri: hello_world/ #(3)!
      Handler: app.lambda_handler #(4)!
      Runtime: python3.11
      Architectures:
        - x86_64
      Events: #(5)!
        HelloWorld:
          Type: Api #(6)!
          Properties: #(7)!
            Path: /hello 
            Method: get
```

1. This is the logical ID for the Lambda function.
2. Specifies that the resource is a Lambda function. There are many different resource types.
3. The directory where the Lambda function code resides.
4. Specifies the entry point for the Lambda function.
5. This section defines the event sources that will trigger the Lambda function.
6. Specifies that this event is an API Gateway event.
7. The API endpoint and the HTTP method.
	
### Simplicity
With AWS SAM, defining a Lambda function is as straightforward as pointing to a directory containing your code. AWS SAM then takes care of bundling the folder's contents along with the necessary dependencies into a zip file, and uploading it to AWS. It also automatically generates the appropriate IAM roles for you during this process.
  
### Interoperability
A key advantage of AWS SAM is its seamless integration with other services. For instance, in our example, we've integrated our Lambda function with API Gateway, demonstrating the simplicity of combining AWS services in a SAM application.

## Exercises
* Accept a path parameter that contains your name, and when calling the endpoint, it will return the specified name - `hello <path parameter>`. For example calling `https://apigw-url/hello/efi` will return `hello efi`.
??? tip
    1. Add `/{name}` to the path
    2. In the Lambda handler, extract the path parameter using the following code - `event.get("pathParameters", {}).get("name")`

* Add a new Python Lambda to the template that returns "Mama Mia" in its response.