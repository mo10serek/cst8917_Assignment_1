# CST 8917 Assignment 1

## Introduction

This assignment is a combination of Lab 1 and Lab 2 where you both make an Durable function and having a SQL output binding. In the durable function setup, there is a trigger function that run the program when someone submit an image to the blob storage and it will be send to the orchestrator function. The trigger function is also connected to the input container in the blob storage to get the image from the user. In the orchestrator function will call two functions which are extract_metadata and send_to_SQL functions. The extract_metadata is an activity function that get data from the image such as dimentions, format, name, and size. Then it will return all of the extracted data in a json format. The send_to_SQL is also another activity function that send the extracted json data format to the SQL database. The extracted_metadata is connected to the SQL server that have a table that is used to store the extracted data from the image.

## Set up Azure resoruces 

### Configure Azurite
In order to deploy the application, you first need to press F1 and run this command
```txt
Azurite: Start
```

to run the processes.

### create the Function resource in Azure
After configuring Azurite, we will create the function in Azure by pressing F1 and run this command
```txt
Azure Functions: Create Function App in Azure
```

and then enter the following prompts:
1. (your subscription)
2. get-image
3. East US
4. Python 3.10
5. Secrets

After that, a blob storage will be created for you including a resource group where we will create all the other functions.

## Blob Storage

After the function is deploy, you need to make a container which input 'input'. Go to the storage resource, and fill in the requirements. Then click on `create +` twice and after the blob storage is created, make the input container by going to the containers section on the left. Select 'Add container' and call it input"  After that, Go to the Access keys in the `Access keys` section and get the first connection string and paste it in the `BLOB_STORAGE_ENDPOINT` environment variable in local.settings.json file.

## Binding SQL Queue

Now we need to run the SQL Queue binding function in the other repo.

### Developed first single database

In Azure Portal, open Azure SQL and select Single database under Resource type and select Create under SQL Databases. Fill out the detail for the project

- **Subscription**: (your subscription)
- **Resource group**: get-image
- **Database name**: mySampleDatabase
- **Server**:
    - **Server name**: pick a unique name
    - **Location**: `West ES`
    - **Authentication method**: Select SQL Server authentication
    - **username**: (your username)
    - **password**: (your password)
- **Want to use SQL elastic pool**: **No**
Go to the network section next:
- **Allow Azure services and resources to access this server**: **Yes**

After filling out the details, select `Create` in the `Review + create` page.

### adjusting the SQL database

After the SQL database is deployed, get the connection string in the `Connection strings` under **ADO.NET (SQL authentication)** and store it somewhere.

After that, go the Query editor under the database blade and pastes

```
CREATE TABLE dbo.imageMetrics (
    Id UNIQUEIDENTIFIER PRIMARY KEY,
    Name NVARCHAR(255),
    SizeKB FLOAT,
    Width INT,
    Height INT,
    Format NVARCHAR(50)
);
```

In the query and run it to save the table named `dbo.MetricData` by running it.

Go to the Connection strings blade under Setting section in the SQL database resource and copy the connection string under **ADO.NET** (SQL authentication) and store it in some document.

### Update your function app settings

In the document, replace the value of the `Password` with the password when making the SQL Server and copy the entire string from the document. 

Press F1 and run `Azure Functions: Add New Setting...` and fill out the following prompts: 

- **name**: SqlConnectionString
- **value for "SqlConnectionString"**: (connection string)

After that press F1 again and run `Azure Functions: Download Remote Settings...` and select **Yes to all** to overwrite the existing local settings.

### Deploying the Function resource
Now we need to deploy the application by pressing `F5` and it will run the entire program. Go to the input container and upload any image

after that, go to the **Query editor** blade in the database resource in Azure Portal and log in. Then select **Select Top 1000 Rows** after right click the dbo.ImageMetrics table and check the results if there are any updated rows.

#### Run again and deploy the function to Azure

Press F1 again to open the command palette and run `Azure Functions: Deploy to function app...`. Choose the function app you made and later select **Deploy** when you are in the redeploying process.

After redeploying, run the `Execute Function Now...` command to run the function.

submit the image in the blob storage and check if the database is updated

## Clean up the resources

After you finish a function application, go to the resource groups in Azure Portal and delete each one of them to prevent additional costs.

## Link for demo

[cst8917-Assignment-1](https://youtu.be/wCYx52_xfXk)