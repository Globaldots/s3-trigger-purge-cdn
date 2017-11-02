s3-trigger-purge-cdn
==========
A CDN requires an origin server, which can be a S3 bucket. 
s3-trigger-purge-cdn are python scripts that run as a Lambda function, and are triggered by file uploads to the bucket. Once triggered, the Lambda function will attempt to purge the old file from the CDN cache.
Currently supported: 
- Edgecast
- Akamai

Features:
- *Python based*: Easy to set up and maintain
- *Uses Lambda environment variables*: Modify the environment variables to modify the Lambda behavior

Usage
==========
1. Install and configure Python, pip and Boto3
2. In the project directory, run the following command: `pip install -r requirements.txt -t .` This is in order to be able to create a full deployable package for Lambda
3. Update the config file. 
4. Run the installation script. It will upload the function and its dependencies to AWS Lambda , as well as create the necessary roles, policies and triggers. 

Additional Notes
=========
Creating an Edgecast API key: https://support.globaldots.com/hc/en-us/articles/115004003749-Edgecast-Allowing-API-access
Ask your Akamai account manager or reseller for help with setting up a user for purging.

