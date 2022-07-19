import requests
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



class Highwinds:
    response = {}
    http_status=0
#..................................................................................................
    def __init__(self, **credentials):
        self.user = credentials['user']
        self.password = credentials['password']
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



####################################################################################################

if __name__=="__main__":
    credentials = [
        { 'user' : 'shalom@globaldots.com', 'password' : 'Panda3131'}
        ]
    user=credentials[0]['user']
    password=credentials[0]['password']
    highwinds = Highwinds(user, password)
    print(highwinds.masterAccount)
    account='t8i3z7k8'
    account='b6g8z3d9'
    # hcs_command = '/api/v1/accounts/' + account + '/hcs/tenants'
    # query={}
    # # payload={
            # # "name": "Test1",
            # # "hcsUser": "azubu01",
            # # "hcsUserPassword": "kukunamuniu",
            # # "hcsRegion": "europe"
            # # }
    # # result = highwinds.executeAPI( hcs_command,  payload, query, APITYPE='POST' )
    # payload={}
    # result = highwinds.executeAPI( hcs_command,  payload, query )
    # print result

    print(json.dumps(highwinds.getHCS( account) ))