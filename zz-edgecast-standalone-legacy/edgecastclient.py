import requests
import datetime
import calendar
import json


debug=False

if debug:
    import logging

    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class Edgecast:
    response = {}
    http_status=0

#..................................................................................................
    def __init__(self, **kwargs):
        self.token=kwargs['token']
        self.hex=['hex']
        self.flashPlatform=2
        self.largePlatform=3
        self.smallPlatform=8
        self.ADNPlatform=14
        self.platforms = {
                            "flash" : 2 ,
                            "large" : 3 ,
                            "small" : 8 ,
                            "adn" : 14
                        }
        return None

#..................................................................................................
    def purge(self, url, **kwargs):
        payload = {
            'MediaPath' : url,
            'MediaType' : kwargs['platform']
            }
        command = "/v2/mcc/customers/%s/edge/purge" % (self.hex)
        query={}
        result = self.executeAPI( command,  payload, query , verb='PUT' )
        return json.loads(result)
#..................................................................................................
    def executeAPI( self, api_command, api_payload , query, verb='GET'):
        api_base_url = "https://api.edgecast.com"
        action = api_command
        url =   api_base_url + action
        headers = {
                'Content-Type' : 'application/json',
                'Accept' : 'application/json',
                'Authorization' : 'tok:'+self.token
                }
        r = requests.request(verb, url,headers=headers, json=api_payload, params=query)
        self.http_status = r.status_code
        self.http_content = r.content
        content = r.content
        return (content)

####################################################################################################

