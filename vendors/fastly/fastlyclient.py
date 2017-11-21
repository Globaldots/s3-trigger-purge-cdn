import requests
import json
import os

# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead?
try:
    import config
except:
    config_token=None

try:
    config_token = config.token
except:
    config_token=None

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
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class Fastly:
    response = {}
    http_status=0

#..................................................................................................
    def __init__(self, **kwargs):
        self.token=kwargs.get('token', config_token)
        return None

#..................................................................................................
    def purge(self, url_list, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        # retrieve dynamic parameters and set defaults
        assert type(url_list) is list, "Error: expecting a list of assets"
        purge_results = []
        headers = {
                'Content-Type' : 'application/json',
                'Accept' : 'application/json',
                'Fastly-Key' : self.token
                }
        for url in url_list:
            r = requests.request('PURGE', url,headers=headers)
            self.http_status = r.status_code
            self.http_content = r.content
            content = r.content
            result = {
                "url" : url,
                "result" : json.loads(content)
            }
            purge_results.append(result)

        return purge_results


#..................................................................................................


    def executeAPI( self, api_command, api_payload , query, verb='GET'):
        api_base_url = "https://api.fastly.com"
        action = api_command
        url =   api_base_url + action
        headers = {
                'Content-Type' : 'application/json',
                'Accept' : 'application/json',
                'Fastly-Key' : self.token
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
