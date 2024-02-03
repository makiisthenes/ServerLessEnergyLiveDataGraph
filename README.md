# ServerLess Energy Live Data Graph
Use of AWS CloudFront, API Gateway, S3 Bucket, Lambda, DynamoDB, EventBridge and APIs to power a live energy graph showing live prices from within the energy market, which runs completely on the cloud (End to End). Guidance provided by EDF energy company.

**The Architecture of Serverless Energy Outflow Diagram:**

![image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/bbe3d006-bdd3-45e2-8545-0947d7faf468)

This architecture shows, Lamda calling an API service through the use of Amazon EventBridge (invokes every minute), AWS Parameter Score for the API key. When the API is called, the result is stored in a Amazon DynamoDB.

We will then store our react files in the S3 bucket, in which can be accessed through AWS Cloudfront, and then the react app will communicate with our API in Lambda via the AWS API Gateway, this will invoke another lambda function which gets the data for the day.

The API service, will grab the data from Entsoe data service via library, EntsoePandasClient.

https://pypi.org/project/entsoe-py/

Lambda Functions are shown in folder.
