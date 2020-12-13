s3-trigger-purge-cdn
==========
A CDN requires an origin server, which can be a S3 bucket. 
s3-trigger-purge-cdn are python scripts that run as Lambda functions, and are triggered by file uploads to the bucket. Once triggered, the Lambda function will attempt to purge the old file from the CDN cache.
Currently supported CDN vendors: 

- Akamai 
- Chinacache
- Cloudflare
- Edgecast
- Fastly
- Highwinds


*Standalone Legacy mode* 
- Edgecast
- Akamai
- Highwinds

While I started as a project with separate parts for each CDN vendor, the standalone parts will not be maintained anymore. 

Features:
- *Python based*: Easy to set up and maintain
- *Uses Lambda environment variables*: Modify the environment variables to modify the Lambda behavior
- *purge or load*: On Edgecast and Chinacache, you can decide whether to purge from the edge or load onto the edge

Environment variables
==========
Environment variables will be loaded only at the Lambda cold start
* `debug` <true|false>
* `config_file` defaults to multicdn.config.yml


General Usage
==========
1. Install and configure Python, pip and Boto3
2. In the project directory, run the following command: `pip install -r requirements.txt -t .` This is in order to be able to create a full deployable package for Lambda
3. Update the config files. There is a master YAML file, but credentials can also be managed in the `config.py` files in each vendor's folder. 
4. Create a deployment package and upload to your AWS account.  

Additional Notes
=========
Creating an Edgecast API key: https://support.globaldots.com/hc/en-us/articles/115004003749-Edgecast-Allowing-API-access

Adding authentication to Fastly purge: https://docs.fastly.com/guides/purging/authenticating-api-purge-requests 

The Akamai section now supports purging of items protected by token authorization.
This requires an additional API call to find out the ARL of the object, and is turned off by default.
To turn this behaviour on, set the "use_arl" key in the yaml configuration to True.
Ask your Akamai account manager or reseller for help with setting up a user for purging.

