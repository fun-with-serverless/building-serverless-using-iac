> Serverless computing is a cloud computing execution model in which the cloud provider allocates machine resources on demand, taking care of the servers on behalf of their customers. 


[~Wikipedia~ ~(Serverless~ ~commputing)~](https://en.wikipedia.org/wiki/Serverless_computing)

A Serverless service stands on two rules:

* A cloud provider is managing its resources, you as a user, iteract with the service using APIs, usually, you don't have access to the underlying machines. It's transperent to you as a user what happens behind the scenes, the cloud provider can add or remove resources depending on your requests. Scaling is done automatically for you.
* You pay on usage which means if you didn't use, then you won't pay anything. You can still provision a serverless service, but if you didn't do any API calls agaionst it, you won't pay a dime.

There are different Serverless services, usually AWS Lambda is a synonym to Serverless, however, every service that adheres to these rules is aa Serverless service. In the next section we will meet a couple of these services.
