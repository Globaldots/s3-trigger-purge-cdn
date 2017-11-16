import requests
import json
import os


# the config file can be used or skipped.
# if it is used, its credentials will be used as a default


# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead?
try:
    import config
except:
    config_user=None
    config_password = None

try:
    config_user = config.user
except:
    config_user=None

try:
    config_password = config.password
except:
    config_password=None


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



class Highwinds:
    response = {}
    http_status=0
#..................................................................................................
    def __init__(self, **credentials):
        self.user = credentials.get('user', config_user)
        self.password = credentials.get('password', config_password)
        authentication_object= self.authenticate(self.user, self.password)
        self.token=authentication_object["access_token"]
        me=self.getMyself()
        self.masterAccount=me["accountHash"]
        return None

#..................................................................................................

    def getAccountList(self):
        query={}
        payload={}
        account_list=[]
        accounts_command = '/api/v1/accounts/' + self.masterAccount + '/subaccounts'
        result = self.executeAPI( accounts_command,  payload, query )
        result_account_list = json.loads(result)
        account_list += result_account_list["list"]
        return account_list
#..................................................................................................

    def getMyself(self):
        query={}
        payload={}
        command = '/api/v1/users/me'
        result = self.executeAPI( command,  payload, query )
        me = json.loads(result)
        return me
#..................................................................................................



    def executeAPI(self, api_command, api_payload, query, verb='GET'):
        api_base_url = "https://striketracker3.highwinds.com"
        action = api_command
        url = api_base_url + action
        headers = {
                'Content-Type' : 'application/json',
                'Accept' : 'application/json',
                'X-Application-Id' : 'globaldots.com',
                'Authorization' : 'Bearer ' + self.token
                }
        r = requests.request(verb, url, headers=headers, json=api_payload, params=query)
        self.http_status = r.status_code
        self.http_content = r.content
        return (r.content)

#..................................................................................................

    def authenticate( self, user, password):
        url =   'https://striketracker3.highwinds.com/auth/token'
        headers = {
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Accept' : 'application/json',
                'X-Application-Id' : 'globaldots.com'
                }
        postbody= {
            'grant_type' : 'password',
            'username' : user,
            'password' : password
            }
        r = requests.post(url,headers=headers, data=postbody)
        result=json.loads(r.content)
        # Print the result
        return result



#..................................................................................................

    def purge( self, url_list, **kwargs ):
        kwargs = kwargs if kwargs is not None else {}
        # retrieve dynamic parameters and set defaults
        account = kwargs.get('account', self.masterAccount)
        assert type(url_list) is list, "Error: expecting a list of assets"

        command = "/api/v1/accounts/%s/purge" % (account)
        query={}
        payload = {
            "list":
                [ {"url":url,"recursive":"false"} for url in url_list ]
        }
        result = self.executeAPI(command, payload, query, verb='POST')
        return json.loads(result)


# ..................................................................................................

    def construct_url(self, base, bucket, key, vendor=None):
        # ignore vendor and bucket at the moment
        return 'http://{}/{}'.format(base, key)



####################################################################################################
