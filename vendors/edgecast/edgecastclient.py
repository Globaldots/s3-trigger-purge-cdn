import requests
import json
import os

# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead?
try:
    from . import config
except:
    config_token=None
    config_hex = None
    config_platform = None

try:
    config_token = config.token
except:
    config_token=None


try:
    config_platform = config.platform
except:
    config_platform=None

try:
    config_hex = config.email
except:
    config_hex=None

isLambda = True if "LAMBDA_RUNTIME_DIR" in os.environ else False

debug=os.environ.get('debug', False)

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
        self.token=kwargs.get('token', config_token)
        self.hex=kwargs.get('hex', config_hex)
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
    def purgeOld(self, url_list, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        # retrieve dynamic parameters and set defaults
        platform = kwargs.get('platform', config_platform)
        platform = platform if bool(platform) else 'small'
        assert type(url_list) is list, "Error: expecting a list of assets"
        assert platform in self.platforms, "Error: %r is an unsupported platform" % (platform)
        purge_results = []
        for url in url_list:
            payload = {
                'MediaPath' : url,
                'MediaType' : self.platforms[platform]
                }
            command = "/v2/mcc/customers/%s/edge/purge" % (self.hex)
            query={}
            result = self.executeAPI( command,  payload, query , verb='PUT' )
            result_item = {
                "url": url,
                "result": json.loads(result)
            }
            purge_results.append(result_item)

        return purge_results

#..................................................................................................
    def purge(self, url_list, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        kwargs['action'] = 'purge'
        # retrieve dynamic parameters and set defaults
        edge_results = self.edge(url_list, **kwargs)

        return edge_results

#..................................................................................................
    def load(self, url_list, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        kwargs['action'] = 'load'
        # retrieve dynamic parameters and set defaults
        edge_results = self.edge(url_list, **kwargs)

        return edge_results


#..................................................................................................
    def edge(self, url_list, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        # retrieve dynamic parameters and set defaults
        platform = kwargs.get('platform', config_platform)
        platform = platform if bool(platform) else 'small'
        action = kwargs.get('action', None)
        EdgeNodeRegionIds = kwargs.get('regions', None)
        
        assert type(url_list) is list, "Error: expecting a list of assets"
        assert platform in self.platforms, "Error: %r is an unsupported platform" % (platform)
        assert action in ['load', 'purge'], "Error: action %r is not load or purge" % (action)
        edge_results = []
        for url in url_list:
            payload = {
                'MediaPath' : url,
                'MediaType' : self.platforms[platform]
                }
            if EdgeNodeRegionIds:
                payload['EdgeNodeRegionIds']=EdgeNodeRegionIds
            command = "/v2/mcc/customers/%s/edge/%s" % (self.hex, action)
            query={}
            result = self.executeAPI( command,  payload, query , verb='PUT' )
            result_item = {
                "action" : action, 
                "url": url,
                "result": json.loads(result)
            }
            edge_results.append(result_item)

        return edge_results


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

    # ..................................................................................................

    def construct_url(self, base, bucket, key, vendor=None):
        # ignore vendor and bucket at the moment
        return 'http://{}/{}'.format(base, key)

####################################################################################################
