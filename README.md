# # ServerLess Energy Live Data Graph

Interconnector electricity flow in Europe refers to the transfer of electrical power across borders between European countries through high-voltage power lines known as interconnectors. These interconnectors are essential components of the European electricity grid, enabling the exchange of electricity to balance supply and demand across different regions, enhance security of supply, and integrate renewable energy sources. This project achieve a serverless solution of reviewing current electricity flow between countries, France, Belgium, Netherlands and Normay.
![image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/f0a8a52a-476a-4ebe-807f-ebac17521bdc)

https://www.nationalgrid.com/stories/energy-explained/what-are-electricity-interconnectors
https://bmrs.elexon.co.uk/interconnector-flows

Use of AWS CloudFront, API Gateway, S3 Bucket, Lambda, DynamoDB, EventBridge and APIs to power a live energy graph showing live prices from within the energy market, which runs completely on the cloud (End to End). Guidance provided by EDF energy company.

**The Architecture of Serverless Energy Outflow Diagram:**

<img title="" src="https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/bbe3d006-bdd3-45e2-8545-0947d7faf468" data-align="center" />

![image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/c6f56811-707a-4252-943e-4685cf97bb9d)


This architecture shows, Lamda calling an API service through the use of Amazon EventBridge (invokes every minute), AWS Parameter Score for the API key. When the API is called, the result is stored in a Amazon DynamoDB.

We will then store our react files in the S3 bucket, in which can be accessed through AWS Cloudfront, and then the react app will communicate with our API in Lambda via the AWS API Gateway, this will invoke another lambda function which gets the data for the day.

The API service, will grab the data from Entsoe data service via library, EntsoePandasClient.

https://pypi.org/project/entsoe-py/

Lambda Functions are shown in folder.

------



## End to End Live Electricy Flow Dashboard Notes

Once signed into AWS account, we can set up a the services required to make this work.

<u>**Create AWS S3 Bucket**</u>

We create an S3 bucket, in which its a general purpose, with ACLs disabled, (owned by only this AWS account) 

We block all public access to this object, as its going to be accessed from CloudFront service. 

We do not need versioning, we could just use Git to version our frontend, and only push when the checks and tests succeed.

Policies on who can access the bucket will be set soon. 



**<u>Creating Cloud Front Distribution</u>**

CloudFront is a CDN service for delivering data, video, applications and APIs to customers globally, so we will be using this.

This can be used to deliver content from the S3 bucket such as React project.



| We need to set up origin access for this, which initially is on Public, but should be configured, which is shown as option `Origin access control settings`. 

The orgin set is the S3 bucket, now we do not want the bucket to fully be public, and instead we restrict this bucket to only be accessible by the CloudFront service, when selecting this, we must press the create control setting such that the bucket policy is created for us. This OAC has set the policy we like.



We need to update the bucket policy,  UI will guide us.



**<u>Creating Parameter Store (Environment Variables)</u>**

Here we will store the API keys of our project, which will only be one, we name:

`entsoe-api-token`

This will hold our API key in a os.environ type setting, which can be accessed by the Lambda functions independently.



**<u>Creating DynamoDB Database (NoSQL DB like MongoDB)</u>**

We now need to create a database store that holds this information in a graph, we need to create a table.

name of database table is `electric_data` with partition key datetime (N) and sort key date (N).



**<u>Lambda configuration and running</u>**

Lambdas are cloud functions that can run functions and interact with different services, but by default everything has the minimal permissions to do so.

We need to give a Role to Lambda function such that they can access these resources via IAM. 

![2024-02-03-19-28-28-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/0e6d77ec-37a1-4d86-8950-41225c835c92)


Our Lambda needs to access 2 things, which is DynamoDB and SSM. This is the database, and SSM is Systems Manager, however we need it to access SSM credentials.

 API token from the SSM parameters.

Policies are: 

- `[AmazonDynamoDBFullAccess]`

- `[AmazonSSMReadOnlyAccess]`

We can call this Lambda put Dynamodb, which means it allows this lambda function with this role to access the dynamodb.

`lambda-put-dynamodb` is the role name we set. 



<u>SSM is useful as the following code can be ran:</u>

```python
# Using SSM creds, get API token from parameter store.
ssm_client = boto3.client("ssm")
api_key = ssm_client.get_parameter(Name="entsoe-api-token", WithDecryption=False)

```

```python
# Dynamo db client, can access the database using this code.
boto_client = boto3.resource("dynamodb")
dynamo_db_table = boto_client.Table("electric_data")
```

---

Note: Had some errors with parameter, which kept failing eventhough this key is present in the parameter store, however when querying it could not find it, **this is because it is only present in a specific regions, the region the Parameter store is located is `eu-north-1` and so communicating from `eu-west-2` failed to obtain this.**

Make sure that lambda function is created in the same region as the database.

---





To fix this:

```python
# Define the region as well.
ssm_client = boto3.client(
    "ssm",
    region_name="eu-north-1"
) 

api_key = ssm_client.get_parameter(
    Name="entsoe-api-token",
    WithDecryption=False
)


# The same is needed for the boto3 object.
boto_client = boto3.resource("dynamodb", region_name="eu-north-1")
dynamo_db_table = boto_client.Table("electric_data")

```

Making your AWS Systems Manager Parameter Store access region-agnostic directly is not possible because AWS services, including Systems Manager, are regional. This means that resources created in one region are not automatically available in other regions. Each parameter you create in the Parameter Store is stored in a specific region and can only be accessed from that region.





<u>Understanding Lamdas and Metrics</u>

Every month you are given 1M free requests, and 400.000 GB-seconds.

GB-seconds are the number of seconds your function runs for, multiplied by the amount of RAM memory consumed.



Also Lambdas can run functions, in which we do require that such functions running contain, 

Note, the reason I use a zip file here is because AWS only provides the basic packages,
if there’s a non-standard package, you need to zip it up and include it with the code!

If not we could just copy and paste into the code source, each code block should contain, `lambda_handler()`

![2024-02-03-20-25-14-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/6df52f1c-12da-421c-b4e5-e0d231ffeaea)




This lambda function is called `lambda_db_push` and will be used, now that we have this we need to make sure that it can be called, we need to provide a zip with the python function as well as the packages that are not standard. 

<img title="" src="https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/70782fd5-097a-4b23-b4e5-a19ae5624cee" alt="" width="214" data-align="center">

The zip should look like the following, where the lambda function is shown below, and all these folders contain the libraries, that it uses.



If we upload this via `Upload Form` and test the function, we should then get a configuration setting, in which we can see the memory and timeout settings, which we can set. 

As it fails after 3 seconds, we can extend this. 

I changed memory size to be 200 MB and timeout to 30 seconds. This means the 



---

Running this, should give us a success response, with a new entry in the database.

![2024-02-03-21-45-04-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/d96036bd-fbb2-4099-93b2-444ee457094b)


![2024-02-03-21-46-10-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/783ddaf4-ef30-4ae9-ac21-9c9e4145767d)


These can be seen in the DynamoDB UI, which shows the list of query items.

---

**<u>Schedule this Lambda</u>**

We will use something called AWS EventBridge, this service allows for a schedule to invoke a target one-time or at regular intervals defined by a cron or rate expression.



Before making a scheduler to obtain this data every x minutes, we should calculate, the amount of GB-Sec it takes, we are allocated 400k GB-Sec per month for free, 

So from the test run, we are looking at roughly, (7659ms * 152MB) = 1.164GB Sec. Per Run of Lambda

We can afford to do 343,642 calls per month without being charged.



We start by making an EventBridge Rule (now Schedule can be made straight away),

This sets the name `db-push-scheduler`

![2024-02-03-22-03-43-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/7adc124f-1eb2-4805-a4b0-9726d89a3080)


Running every 15 minutes.

We invoke the target, which is a AWS Lambda, with function name `db-push`. Now this lambda function will be called every 15 minutes, as easy as that and technically can run forever for free. However we need to consider the costs associated with holding a DynamoDB, and possible set limits.



**This is the backend done, but we still need to make sure that such operation is sustainable.**

---

Now we need to setup the frontend handling of React build code, and setting up the API gateway such that the frontend can call a specific lambda function which will call the database.



**<u>Lambda Function for API</u>**

We now want to make another lambda function, so a new IAM role is needed for this trusted entity / AWS service. We will take the policy, `DynamoDBReadOnly`

We call this role `api-lambda-exec` in which will be allowed to be invoked when a API request is called and will contact the dynamo db entries, via the read only priviledge.

Done, now create the lambda function, 

Lambda function will have name `api-lambda-db-read` and also be with Python 3.9

We will then apply the code through the code source,

![2024-02-03-22-19-20-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/59090f26-fe9e-4e95-83e6-3da5850b0e35)


And deploy these, we can then test this and see how much resources this takes. 



Now we obtain a response, we know that the lambda function works, what I realised is that the test only works on deployed code, so if we have edited it then we need to deploy before testing it. 



----

Now invoking this lambda such that the user is able to obtain it is the next step, we do this by doing the following, 



Make an API Gateway, such that users from the frontend can simply request this from the lambda.

To do this we go to API Gateway and then go to REST API, in which we set the name,

We call this API, with the name `interconnector-api`

Once we make this resource, we can create a method, GET with integration type being the lambda function.

Here we set the lambda function to be:

`arn:aws:lambda:eu-north-1:992382465295:function:api-lambda-db-read`

We can enable CORS on this through the resource button, but also this help page will aid you:

https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors-console.html


<img title="" src="https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/9a496386-714b-493d-94d0-46e19194e419" alt="" width="387" data-align="center">

----

We then deploy the API, and call it production.

We will be able to obtain the invoke url, through the use of Stages section, which will give you the URL, 

![2024-02-03-22-40-34-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/08e95be9-6659-4f52-b88e-02144cfcd6cb)


----

Now we go to the final part of the code, which is the frontend code.

Frontend is created using something called react-redux, a good tutorial recommended is: [React Redux API Request With Redux and Chart.js - React Javascript Tutorial - YouTube](https://www.youtube.com/watch?v=UsL46JwBZwk)



So now we put our code into the S3 bucket, which is accessible by the CloudFront distribution.

The code will need to be rebuilt, to contain the updated URL, this can be updated in App.js and then built using `npm run build` for a new build.



We put the contents of the build folder into the S3, by uploading it as a object.

![2024-02-03-23-07-50-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/066e2721-b02e-4803-800b-c4733473ac87)


Now we have access to these files within our directory, 

![2024-02-03-23-08-42-image](https://github.com/makiisthenes/ServerLessEnergyLiveDataGraph/assets/52138450/c171ec7d-405d-4a56-8e85-bdc62f5826be)

We go onto CloudFront, the front to the internet from the S3 bucket connection we made earlier. 



Now we can copy the domain name, and add index.html

[React App](https://d3h26qfmdraaxa.cloudfront.net/index.html)

Is shown below, 

---

I have stopped the services from running for the sake of not causing any account balance issues.

When considering updating the code frequently, make sure to clear cache of CloudFront, such that the updates are shown, the command for this would be:

`aws cloudfront create-invalidation --distribution-id E3G4RNRQVISTEW --paths "/*"`


End of Notes ~ Michael Peres


