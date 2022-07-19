#
# (c) 2017 Shalom Carmel shalom@globaldots.com 
#
# purge-multi version 1
# https://api.ccu.akamai.com/ccu/v2/docs/

# Changelog
# version 1:   Initial version
# Version 2:   full multicdn support


import os
import json
import sys
import logging

import multicdn
from vendors import *

# Lambda has some special environment variables
isLambda = True if "LAMBDA_RUNTIME_DIR" in os.environ else False
debug=os.environ.get('debug', False)

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# load CDN configuration from external source

multi = multicdn.Multicdn()
multi_cdn_bucket_configuration = multi.getConf()
multi_cdn_configuration = multi.getCDNConf()

if debug: print("bucket config:", json.dumps(multi_cdn_bucket_configuration))
if debug: print("cdn config:", json.dumps(multi_cdn_configuration))


def construct_url(base, bucket, key, vendor=None):
    # ignore vendor and bucket at the moment
    return 'http://{}/{}'.format(base, key)

   
def main(event, context=None):
    output=[]
    url_list = []
    # accumulate a batch of URLs to purge

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        bucket_cdn_array = multi_cdn_bucket_configuration.get(bucket, {})
        if debug: print(bucket,key,bucket_cdn_array)
        #
        # The next structure may be too complex, as tests show that S3 fires events one at a time
        # However, we cannot be sure that it will always be so.
        #
        for cdn, cdn_platform_array in bucket_cdn_array.items():
            cdn_config=multi_cdn_configuration.get(cdn, {})
            try:
                cdn_class = globals()[cdn]
                cdn_instance = cdn_class(**cdn_config)
            except:
                logger.error('CDN failed to instantiate: {} '.format(cdn))
                continue
                # if cdn object failed to instantiate - ignore it and skip to next

            for platform, host_list in cdn_platform_array.items():
                url_list=[]
                action='purge' # by default
                for host_element in host_list:
                    if host_element.get('host'):
                        cdn_url = cdn_instance.construct_url(host_element['host'], bucket, key)
                        url_list.append(cdn_url)
                    # Edgecast specific
                    elif cdn=='edgecast' and host_element.get('action', None) is not None: 
                        action=host_element.get('action')
                if debug: print(cdn, platform, url_list)
                
                if action=='purge':
                    purge_response = cdn_instance.purge(url_list, platform=platform)
                elif action=='load':
                    purge_response = cdn_instance.load(url_list, platform=platform)
                    
                if debug: print(purge_response)

                purge_response_http_status = cdn_instance.http_status
                cdnEvent = {
                            "url_list" : url_list,
                            "cdn" : cdn,
                            "platform" : platform ,
                            "cdn_response" : {
                                "status" : purge_response_http_status , 
                                "response" : purge_response
                                }
                        }
                # if  purge_response_http_status not in range (200,299) or 'error' in cdn_instance.http_content.lower():
                # cloudflare was returning false positives because their response has an empty 'error' key even on success
                if purge_response_http_status not in list(range(200, 299)):
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
              "key": "index.html",
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
    
    print( json.dumps(main(event)) )