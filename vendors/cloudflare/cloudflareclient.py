import requests
import json
import os


# the config file can be used or skipped.
# if it is used, its credentials will be used as a default


# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead?
try:
    from . import config
except:
    config_apikey=None
    config_email = None

try:
    config_apikey = config.apikey
except:
    config_apikey=None


try:
    config_email = config.email
except:
    config_email=None


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


###################################################################################################

class Cloudflare:
    response = {}
    http_status=0

#..................................................................................................
    def __init__(self, **kwargs):
        self.email=kwargs.get('email', config_email)
        self.apikey=kwargs.get('apikey', config_apikey)
        assert bool(self.email), "Missing authentication email"
        assert bool(self.apikey), "Missing authentication API key"
        return None

#..................................................................................................


    def purge(self, url_list, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        # retrieve dynamic parameters and set defaults
        zoneid = kwargs.get('platform', None)

        assert type(url_list) is list, "Error: expecting a list of assets"
        assert bool(zoneid) , "Error: zoneid is expected as the 'platform' parameter "

        command = "/zones/%s/purge_cache" % (zoneid)
        query= {}
        payload= {
            "files" : url_list
        }
        result = self.executeAPI( command,  payload, query, verb="DELETE" )
        return json.loads(result)

#..................................................................................................

    def getUserOrganizations(self):
        query={}
        payload={}
        account_list=[]
        accounts_command = "/user/organizations"
        result = self.executeAPI( accounts_command,  payload, query )
        result_account_list = json.loads(result)
        return result_account_list

#..................................................................................................

    def getZones(self):
        # Get zones per account
        command = '/zones'
        query={}
        payload={}
        result = self.executeAPI( command,  payload, query )
        return json.loads(result)

#..................................................................................................

    def executeAPI( self, api_command, api_payload , query, verb="GET"):
        api_base_url = "https://api.cloudflare.com/client/v4"
        action = api_command
        url =   api_base_url + action
        headers = {
                'Content-Type' : 'application/json',
                'Accept' : 'application/json',
                'X-Application-Id' : 'globaldots.com',
                'X-Auth-Key' : self.apikey,
                'X-Auth-Email' : self.email
                }
        r = requests.request(verb, url, headers=headers, json=api_payload, params=query)
        # print r.url
        # Print the result
        self.http_status = r.status_code
        self.http_content = r.content
        return r.content


# ..................................................................................................

    def construct_url(self, base, bucket, key, vendor=None):
        # ignore vendor and bucket at the moment
        return 'http://{}/{}'.format(base, key)

####################################################################################################
