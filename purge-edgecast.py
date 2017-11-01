#
# (c) 2017 Shalom Carmel shalom@globaldots.com 
#
# purge-edgecast version 1
#
# Changelog
# version 1:   Initial version

from __future__ import print_function
import os
import json 
import logging

from edgecast.client import Edgecast
import config

# Lambda has some special environment variables
isLambda = True if "LAMBDA_RUNTIME_DIR" in os.environ else False

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead? 
if isLambda:
    hex=os.environ.get('hex')
    token=os.environ.get('token')
    base_url = os.environ.get('base_url')
    platform = os.environ.get('platform')  # small|large|flash|adn
else:
    hex=config.hex
    token=config.token
    base_url = config.base_url
    platform = config.platform  # small|large|flash|adn
    
    
assert hex,"Error: missing hex account number"
assert token, "Error: missing API token"
assert base_url, "Error: missing base URL"
assert (platform in ['flash', 'small', 'large', 'adn']), "Error: bad or misssing delivery platform"




def construct_url(base, bucket, key):
    return '{}/{}'.format(base, key) 

   
def main(event, context=None):
    output=[]
    # if context: print(context.logGroupName)
    # if context: print(context.logStreamName)
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        edgecast = Edgecast(token, hex)
        cdn_url = construct_url(base_url, bucket, key)  
        platformID = edgecast.platforms.get(platform, 8)
        # platform defaults to small (8)
        purge_response = edgecast.purge(cdn_url, platformID)
        purge_response_http_status = edgecast.http_status
        cdnEvent = {
                            "url" : cdn_url, 
                            "platform" : platformID ,
                            "edgecast_response" : {
                                "status" : purge_response_http_status , 
                                "response" : purge_response
                                }
                        }
        if  purge_response_http_status != 200 or 'error' in edgecast.http_content.lower(): 
            logger.error('HTTP status: {} ; {}'.format(purge_response_http_status, json.dumps(cdnEvent) ) )
        else:
            logger.info(json.dumps(cdnEvent))
    

        output.append( cdnEvent ) 
    return(output)


    
    
if __name__ == '__main__': 
    event = {
      "Records": [
        {
          "eventVersion": "2.0",
          "eventTime": "1970-01-01T00:00:00.000Z",
          "requestParameters": {
            "sourceIPAddress": "127.0.0.1"
          },
          "s3": {
            "configurationId": "testConfigRule",
            "object": {
              "eTag": "0123456789abcdef0123456789abcdef",
              "sequencer": "0A1B2C3D4E5F678901",
              "key": "HappyFace.jpg",
              "size": 1024
            },
            "bucket": {
              "arn": "arn:aws:s3:::mybucket",
              "name": "mybucket",
              "ownerIdentity": {
                "principalId": "EXAMPLE"
              }
            },
            "s3SchemaVersion": "1.0"
          },
          "responseElements": {
            "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
            "x-amz-request-id": "EXAMPLE123456789"
          },
          "awsRegion": "us-east-1",
          "eventName": "ObjectCreated:Put",
          "userIdentity": {
            "principalId": "EXAMPLE"
          },
          "eventSource": "aws:s3"
        }
      ]
    }
    
    print( main(event) )