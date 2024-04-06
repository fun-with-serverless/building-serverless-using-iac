## Welcome
Ever wanted to create your own mailing list manager a la Serverless style, now is your chance. In this workshop you'll build a mailing list manager with the ability to:

* Create new mailing list
* Allow external participants to join these lists
* Schedule sending a message via email to the subscribers.

![workshop](https://github.com/fun-with-serverless/building-serverless-using-iac/assets/110536677/cbcb2866-93a8-488f-ad30-d014c10bba1d)

We are going to build the same application using AWS SAM and CDK, learning along the way the differences between the two IaC tools.

## What's In It For Me (WIIFM)
* Learn how to use AWS SAM.
* Learn how to use AWS CDK.
* Understand their differences through hands-on practice, enabling you to make an informed choice between the two.
* Discover best practices for Serverless development.

## Target Audience
* Individuals with development experience, preferably in Python. However, Python knowledge is not mandatory.
* Those who have prior experience with AWS services and have access to an AWS environment.
* People familiar with serverless services such as AWS Lambda, S3, and DynamoDB.


## Workshop Structure
The workshop is divided into four main parts:

* For those who are unfamiliar or only partially familiar with the concept of Serverless, we have a brief section that explains the concept and introduces various serverless services. You may skip this section if you already have experience with AWS Lambda.
* A concise introduction to the world of Infrastructure as Code (IaC).
* Building the application from scratch using AWS SAM and Python. Each subsection focuses on constructing a different part of the application, covering both code and the relevant IaC.
* Rebuilding the application using AWS CDK, based on the code developed in the AWS SAM section. This part solely focuses on the CDK aspect, as it assumes familiarity with the application's code.


## Source Code
You can find the relevant code for each section in the repository under `aws-sam-src` and `cdk-src`. You have the option to either write the code from scratch or use the repository as a starting point.

In this workshop, I highly recommended to type the code instead of copying & pasting (there’s usually not much to type). This way, you’ll be able to fully experience what it’s like to use the AWS SAM and CDK. It’s especially cool to see your IDE help you with auto-complete, inline documentation and type safety.

## Page Structure
Each page is divided into four main parts:

* High level architecture.
* Implementation details - Code snippets that drive the application you build. Pay attention to the fact that the code snippets contain comments, represented by a + sign. You can click on the comments to get more context.
![comments](https://github.com/fun-with-serverless/building-serverless-using-iac/assets/110536677/4d5c6765-c350-4b13-a405-63fbce820288)
* Insights - Various insights about the code itself. Usually, the insights expand upon the comments given in the previous section.
* Exercises - To get the most out of the workshop, it's recommended that you complete all the exercises.

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
