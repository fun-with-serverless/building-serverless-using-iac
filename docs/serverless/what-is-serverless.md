> Serverless computing is a cloud computing execution model in which the cloud provider allocates machine resources on demand, taking care of the servers on behalf of their customers. 


[~Wikipedia~ ~(Serverless~ ~computing)~](https://en.wikipedia.org/wiki/Serverless_computing)

Any serverless service is based on two key principles:

* A cloud provider manages the resources, allowing you as a user to interact with the service via APIs. Typically, you don't have access to the underlying machines. The operational details are transparent to you; the cloud provider can add or remove resources based on your demand, handling scaling automatically.
* You pay based on usage, meaning if you don't use the service, you don't incur any costs. While you can provision a serverless service, you won't be billed unless you make API calls against it.

Although AWS Lambda is often synonymous with serverless, any service that adheres to these principles is considered a serverless service. In the following section, we will explore several such services.