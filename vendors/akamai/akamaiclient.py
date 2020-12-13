import requests
import json
import os

from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urlparse import urljoin

# the config file can be used or skipped.
# if it is used, its credentials will be used as a default


# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead?
try:
    import config
except:
    config_user=None
    config_password = None
    edgerc_location = None
    edgerc_section = None

try:
    config_user = config.user
except:
    config_user=None

try:
    config_password = config.password
except:
    config_password=None

try:
    edgerc_location = config.edgerc_location
except:
    edgerc_location=None

try:
    edgerc_section = config.edgerc_section
except:
    edgerc_section=None


isLambda = True if "LAMBDA_RUNTIME_DIR" in os.environ else False

# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead?
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


class Akamai:
    response = {}
    http_status = 0

    # ..................................................................................................
    def __init__(self, **credentials):
        self.user = credentials.get('user', config_user)
        self.password = credentials.get('password', config_password)
        self.use_arl = credentials.get('use_arl', False)

        self.edgerc_location = credentials.get('edgerc', edgerc_location)
        self.edgerc_section = credentials.get('edgerc_section', edgerc_section)

        assert self.password, "Error: missing API password"
        assert self.user, "Error: missing API user"
        assert self.edgerc_location, "Error: missing edgerc file"
        assert self.edgerc_section, "Error: missing edgerc section"

        self.edgerc = EdgeRc(self.edgerc_location)
        section = self.edgerc_section
        self.baseurl = 'https://%s' % self.edgerc.get(section, 'host')

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
        assert platform in ['production', 'staging'], "Error: %r is wrong platform, must be production or staging" % (
            platform)
        assert queue in ['default', 'emergency'], "Error: %r is wrong queue, must be default or emergency" % (queue)
        assert action in ['delete', 'invalidate'], "Error: %r is wrong action, must be delete or invalidate" % (action)
        assert list_type in ['arl', 'cpcode'], "Error: %r is wrong list type, must be arl or cpcode" % (
            list_type)

        if self.use_arl:
            url_list = [self.get_arl(url) for url in url_list]
        payload = { "objects": url_list }
        command = "/ccu/v3/%s/url/%s" % (action, platform)
        query = {}
        result = self.executeAPI(command, payload, query, verb='POST')
        return json.loads(result)

    # ..................................................................................................
    def get_arl(self, url, **kwargs):
        # if no parameters passed, initialize to an empty set.
        kwargs = kwargs if kwargs is not None else {}
        request_headers = {
            "Pragma": "akamai-x-cache-on,akamai-x-cache-remote-on,akamai-x-check-cacheable,akamai-x-get-cache-key,akamai-x-get-true-cache-key,akamai-x-serial-no,akamai-x-get-request-id,akamai-x-get-client-ip,akamai-x-feo-trace"
        }
        r = requests.request('HEAD', url, headers=request_headers, json={}, params={} )
        response_headers = dict(r.headers)
        x_cache_key=response_headers.get("X-Cache-Key", "")
        # typical response looks like
        # 'L1/=/16382/705116/1d/castplus-usw2-prod-served-episodes.s3-us-west-2.amazonaws.com/1.html'
        self.http_status = r.status_code
        self.http_content = r.content
        if x_cache_key:
            arl = x_cache_key
            return arl
        else:
            return url

    # ..................................................................................................
    def executeAPI(self, api_command, api_payload, query, verb='GET', headers={}):
        api_base_url = self.baseurl
        action = api_command
        url = urljoin(self.baseurl,  action)
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        request_headers.update(headers)
        session = requests.Session()
        session.auth = EdgeGridAuth.from_edgerc(self.edgerc, self.edgerc_section)
        r =session.request(verb, url, headers=request_headers, json=api_payload, params=query)
        self.http_status = r.status_code
        self.http_content = r.content
        content = r.content
        return (content)

        # ..................................................................................................

    def construct_url(self, base, bucket, key, vendor=None):
        # ignore vendor and bucket at the moment
        return 'http://{}/{}'.format(base, key)


####################################################################################################

if __name__=="__main__":
    akamai=Akamai()
    res = akamai.purge(['https://www.globaldots.com/wordpress/wp-content/uploads/js_composer/custom.css?ver=4.3.4'])
    print res
