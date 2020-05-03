# External Room Membership Checker

## Overview
This Python script is built based on the [Symphony Python SDK](https://github.com/SymphonyPlatformSolutions/symphony-api-client-python)

The script will retrieve a list of Active External Conversations (MIM and ROOM) from the pod.
For each conversation, it will check if there is at least 2 Internal users from the home pod.
The script will produce a CSV file containing list of all the Conversations that do not meet the above criteria.

## Output Columns
The CSV file will contain following columns:
- Room Name ("MIM" if it is a MIM)
- Date Created
- Room Created By
- Ext Counterparty Name

The output file will be saved in the root directory in format - ``result_YYYY-MM-dd_HHmmSS.csv``

## Known limitations
Room Created By will be N/A:
- When creator is external and deactivated

Ext Counterparty Name will be N/A:
- When all external members left
- When all external member deactivated

## Environment Setup
This client is compatible with **Python 3.6 or above**

Create a virtual environment by executing the following command **(optional)**:
``python3 -m venv ./venv``

Activate the virtual environment **(optional)**:
``source ./venv/bin/activate``

Install dependencies required for this client by executing the command below.
``pip install -r requirements.txt``


## Getting Started
### 1 - Prepare the service account
The Python client operates using a [Symphony Service Account](https://support.symphony.com/hc/en-us/articles/360000720863-Create-a-new-service-account), which is a type of account that applications use to work with Symphony APIs. Please contact with Symphony Admin in your company to get the account.

The client currently supports two types of Service Account authentications, they are
[Client Certificates Authentication](https://symphony-developers.symphony.com/symphony-developer/docs/bot-authentication-workflow#section-authentication-using-client-certificates)
and [RSA Public/Private Key Pair Authentication](https://symphony-developers.symphony.com/symphony-developer/docs/rsa-bot-authentication-workflow).

**RSA Public/Private Key Pair** is the recommended authentication mechanism by Symphony, due to its robust security and simplicity.

**Important** - The service account must have **User Provisioning** role in order to work.

### 2 - Upload Service Account Private Key
Please copy the Service Account private key file (*.pem) to the **rsa** folder. You will need to configure this in the next step.

### 3 - Update resources/config.json

To run the bot, you will need to configure **config.json** provided in the **resources** directory. 

**Notes:**
Most of the time, the **port numbers** do not need to be changed.

You should replace **pod** with your actual Pod URL.

You also need to update based on the service account created above:
- botPrivateKeyPath (ends with a trailing "/"))
- botPrivateKeyName
- botUsername
- botEmailAddress

Sample:

    {
      "sessionAuthHost": "<pod>.symphony.com",
      "sessionAuthPort": 443,
      "keyAuthHost": "<pod>.symphony.com",
      "keyAuthPort": 443,
      "podHost": "<pod>.symphony.com",
      "podPort": 443,
      "agentHost": "<pod>.symphony.com",
      "agentPort": 443,
      "authType": "rsa",
      "botPrivateKeyPath":"./rsa/",
      "botPrivateKeyName": "bot-private-key.pem",
      "botCertPath": "",
      "botCertName": "",
      "botCertPassword": "",
      "botUsername": "<bot-user>",
      "botEmailAddress": "<bot-email>",
      "appCertPath": "",
      "appCertName": "",
      "appCertPassword": "",
      "authTokenRefreshPeriod": "30",
      "proxyURL": "",
      "proxyUsername": "",
      "proxyPassword": "",
      "podProxyURL": "",
      "podProxyUsername": "",
      "podProxyPassword": "",
      "agentProxyURL": "",
      "agentProxyUsername": "",
      "agentProxyPassword": "",
      "keyManagerProxyURL": "",
      "keyManagerProxyUsername": "",
      "keyManagerProxyPassword": "",
      "truststorePath": ""
    }

### 4 - Run script
The script can be executed by running
``python3 main.py`` 



# Release Notes

## 0.1
- Initial Release