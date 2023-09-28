The following sections will review well-known serverless services in AWS. This is a cursory overview; you're more than welcome to dive deeper into each service by reading the official documentation.

## AWS Lambda
AWS Lambda is a serverless compute service that allows you to run code in response to various events. By "compute," I mean it executes the code you write without requiring you to manage the underlying servers. AWS Lambda operates on an event-driven model, triggering executions based on different events such as:

* A new message arriving in an SQS queue
* An HTTPS call via API Gateway
* A new item being added to a DynamoDB table

Key Features:

* Scalability: AWS Lambda automatically scales your applications in response to the traffic received.
* Statelessness: Each Lambda function execution is independent, allowing stateless operation.
* Resource Constraints: Unlike traditional compute services, AWS Lambda imposes restrictions on resources like memory, disk space, and execution time, affecting how you architect your solutions.
* Multiple Language Support: AWS Lambda supports several programming languages, including Python, Node.js, Java, and more.

For more details, follow the official documentation - [https://docs.aws.amazon.com/lambda/latest/dg/welcome.html](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)

## API Gateway
API Gateway is a serverless HTTP(S) proxy, offering a bridge between the public internet and private services within your organization. While it can connect to various AWS services, one of its standout features is the seamless integration with AWS Lambda. This allows each external HTTP(S) call to trigger a Lambda function, facilitating real-time request handling without the need to manage servers.

Key Features:

* Security: API Gateway provides multiple layers of security, including API keys, OAuth tokens, and AWS Identity and Access Management (IAM) policies.
* Rate Limiting: Control the number of requests users can make to your API, preventing abuse and ensuring fair usage.
* Caching: Offers caching capabilities to improve performance and reduce the backend load.
* Monitoring and Logging: Integrated with AWS CloudWatch for real-time monitoring and logging capabilities.

For more details follow the official documentation -
[https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)

## DynamoDB
DynamoDB is a serverless NoSQL database service provided by AWS, designed for high-performance data operations. One of its hallmark features is the speed at which it can retrieve and insert data, irrespective of the database size. It can easily scale to handle hundreds of millions of requests per second.

Key Features:

* Low Latency: DynamoDB provides single-digit millisecond latency, making it suitable for real-time applications.
* Scalability: Designed for seamless scalability, DynamoDB can handle large amounts of traffic without any manual intervention.
* Global Distribution: With Global Tables, you can replicate your data across multiple AWS regions for better availability and latency.
* Flexible Schema: Being a NoSQL database, it allows for a flexible schema design, accommodating complex data structures.

For more details follow the official documentation - [https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)

## S3
S3, or Simple Storage Service, is a serverless blob storage service provided by AWS that offers a file-like view of stored objects. You can store blobs ranging from as small as 1 byte to as large as 5TB. It features global distribution and is renowned for its durability.

Key Features:

* Durability and Availability: S3 promises 99.999999999% (11 9's) durability over a given year, ensuring that your data is safe and always accessible.
* Data Lifecycle Policies: Allows you to automatically move or delete data based on age or other criteria, optimizing storage costs.
* Versioning: Provides the ability to keep multiple variants of an object in the same bucket, useful for backup and restoration.
* Security: Offers a range of features for securing your data, including bucket policies, IAM roles, and server-side encryption.

For more details follow the official documentation - [https://docs.aws.amazon.com/AmazonS3/latest/userguide//Welcome.html](https://docs.aws.amazon.com/AmazonS3/latest/userguide//Welcome.html)