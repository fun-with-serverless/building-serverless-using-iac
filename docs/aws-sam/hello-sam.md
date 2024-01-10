## Prepare your machine
### Cloud9
1. I highly recommend using Cloud9. AWS Cloud9 is a cloud-based integrated development environment (IDE) that allows you to write, run, and debug code from any web browser. Don't opt for the bare-minimum machine type; a 2-core machine (t2.small) is sufficient, [assign at least 50 GB of disk space](#resize-your-ebs). The script in Step 3 is designed for Ubuntu; therefore, select Ubuntu as your operating system in the dropdown menu.
2. After creating the machine, clone `https://github.com/fun-with-serverless/building-serverless-using-iac.git`
3. Execute the script located at `./scripts/update_python_on_cloud9.sh` to prepare your environment. It'll take a couple of minutes. Grab a cup of coffee.

### Resize your EBS
In case you are using Cloud9, each machine is equipped with 10GB of disk space, which sometimes is not enough, especially if you are using CDK. [Follow these instructions to add more disk space](https://ec2spotworkshops.com/ecs-spot-capacity-providers/workshopsetup/resize_ebs.html).

### Non Cloud9 machine
If you prefer to use your own environment, please follow these steps:

1. Install AWS SAM. Follow [https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
2. Verify it works as expected, run `sam --version` you should be getting something like `> SAM CLI, version 1.96.0`. Pay attention that the version might change
3. Check that you have a working Python environment, run `python --version`. In case you are getting an error:
    1. Install [pyenv](https://github.com/pyenv/pyenv)
    2. Install Python 3.11 - `pyenv install 3.11`
    3. Make it global - `pyenv global 3.11`

4. Clone `https://github.com/fun-with-serverless/building-serverless-using-iac.git`

## What is AWS SAM ?
The application will be constructed using AWS SAM. The next section provides an overview of AWS SAM; if you already have experience with this service, feel free to skip ahead.

[Amazon Web Services Serverless Application Model (AWS SAM)](https://aws.amazon.com/serverless/sam/) is a framework for building serverless applications. It simplifies the process of creating and managing resources used in serverless applications using AWS services like Lambda, API Gateway, and DynamoDB. 
AWS SAM uses a template file to define your serverless application and its resources, providing a streamlined and consistent method for deploying complex serverless applications. 
By leveraging AWS SAM, you can more easily automate deployment processes, test your applications locally before deploying, and even generate boilerplate code for common serverless patterns.

In the following section we will build a simple hello world application using SAM.

* `sam init`
* Choose `AWS Quick Start Templates`
* Next choose `Hello World Example`
* If you choose to use the most popular runtime and package type, then make sure that Python 3.9 is installed
* Choose `Python 3.11`
* Choose `Zip`
* Choose the default answers for the rest of the questions.
* For project name, choose the default
<img src="https://github.com/aws-hebrew-book/building-serverless-in-hebrew-workshop/assets/110536677/4bf1a5ca-cdbe-455b-a29d-2ce4a4ddddf0" width="400">

* You need to build the sam packge 
* Go to the folder the template created `cd sam-app`
* Run `sam build` and next run `sam deploy --guided`. You should run guided each time you want to add something to the sam configuration file or create it for the first time.
* When asked `HelloWorldFunction may not have authorization defined, Is this okay?` choose `y`
* The rest can be defaults
* `Deploy this changeset?` choose `y`
* Give the deployment a try, you should see under `Outputs` the `API Gateway endpoint URL`, copy the URL and try it on browser.
* When done, run `sam delete` to remove the stack.

## Insights

### Template
	
At the core of every AWS SAM application lies the template.yaml, a file that outlines the resources utilized by the app. The file is located at the root of the SAM application you created; in our case, it's `sam-app`. 

Our sample template file is split into four main sections:
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

### Deploying changes
Each time you make changes to any of your source files, there are two steps that need to be done in order to deploy the changes to AWS:

1. `sam build` - This creates the deployment package for the different Lambdas.
2. `sam deploy` - This deploys the zip package along with any required changes in the additional resources that are created.

## Exercises
* Accept a path parameter that contains your name, and when calling the endpoint, it will return the specified name - `hello <path parameter>`. For example calling `https://apigw-url/hello/efi` will return `hello efi`.
??? tip
    1. Add `/{name}` to the path
    2. In the Lambda handler, extract the path parameter using the following code - `event.get("pathParameters", {}).get("name")`

* Add a new Python Lambda to the template that returns "Mama Mia" in its response.
* What is the purpose of `sam build`? Can you locate its artifacts?
