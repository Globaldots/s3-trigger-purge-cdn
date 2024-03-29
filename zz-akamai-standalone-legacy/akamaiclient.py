import requests
import json

debug = False

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


class Akamai:
    response = {}
    http_status = 0

    # ..................................................................................................
    def __init__(self, **credentials):
        self.user = credentials['user']
        self.password = credentials['password']

        return None


    # ..................................................................................................
    def purge(self, url_list, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        # retrieve dynamic parameters and set defaults
        platform = kwargs.get('platform', 'production')
        queue = kwargs.get('queue','default')
        action = kwargs.get('action', 'remove')
        list_type = kwargs.get('list_type','arl')
        assert type(url_list) is list, "Error: expecting a list of assets"
        assert platform in ['production', 'staging'], "Error: %r is wrong platform, must be sproduction or staging" % (
            platform)
        assert queue in ['default', 'emergency'], "Error: %r is wrong queue, must be 'default' or 'emergency'" % (queue)
        assert action in ['remove', 'invalidate'], "Error: %r is wrong action, must be 'remove' or 'invalidate'" % (action)
        assert list_type in ['arl', 'cpcode'], "Error: %r is wrong list type, must be 'arl' or 'cpcode'" % (
            list_type)

        payload = {
            "objects": url_list,
            "action": action,
            "type": list_type,
            "domain": platform
        }
        command = "/ccu/v2/queues/%s" % (queue)
        query = {}
        result = self.executeAPI(command, payload, query, verb='POST')
        return json.loads(result)

    # ..................................................................................................
    def executeAPI(self, api_command, api_payload, query, verb='GET'):
        api_base_url = "https://api.ccu.akamai.com"
        action = api_command
        url = api_base_url + action
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.request(verb, url, headers=headers, json=api_payload, params=query,
                             auth=(self.user, self.password))
        self.http_status = r.status_code
        self.http_content = r.content
        content = r.content
        return (content)

        ####################################################################################################
