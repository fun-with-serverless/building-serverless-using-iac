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
