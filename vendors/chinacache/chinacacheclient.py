import os
import requests
import json

# These will only by loaded during Lambda cold start. Should this code be placed in the main function instead?
try:
    from . import config
except:
    auth_token=None

try:
    auth_token = config.token
except:
    auth_token=None


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


class Chinacache:
	response = {}
	http_status=0

#..................................................................................................

	def __init__(self, **kwargs):
		self.auth_token = kwargs.get('token', auth_token)
		assert bool(self.auth_token), "Missing authentication API key"
		return None

	# ..................................................................................................
	# ..................................................................................................
	def purge(self, url_list, **kwargs):
		api_command = '/cache/refresh'
		kwargs = kwargs if kwargs is not None else {}
		type = kwargs.get('type', 'url')
		api_payload = {
			"urls": url_list,
			"type": type
		}
		query = {}
		result = self.executeAPI(api_command, api_payload=api_payload, query=query, method='POST')
		try:
			return json.loads(result)
		except:
			return result

	# ..................................................................................................
	def load(self, url_list, **kwargs):
		api_command = '/cache/prefetch'
		kwargs = kwargs if kwargs is not None else {}
		api_payload = {
			"urls": url_list
		}
		query = {}
		result = self.executeAPI(api_command, api_payload=api_payload, query=query, method='POST')
		try:
			return json.loads(result)
		except:
			return result

	# ..................................................................................................

	def executeAPI( self, api_command, api_payload=None , query={} , method='GET'):
		api_base_url = "https://openapiv2.chinacache.com/v2"
		action = api_command 
		url_string =   api_base_url + action
		query["token"] = self.auth_token
		headers = {
			"Content-Type": "application/json",
			"Accept" : "application/json"
		}
		response = requests.request(method, url_string, params=query, headers=headers, json=api_payload)
		# response = requests.get(url_string, params=query, headers=headers)
		self.http_status = response.status_code
		self.http_content = response.content
		try:
			result = json.loads(response.content)
			self.http_status = result.get("error_code", response.status_code)
		except:
			result = response.content
		return result


	# ..................................................................................................

	def construct_url(self, base, bucket, key, vendor=None):
		# ignore vendor and bucket at the moment
		return 'http://{}/{}'.format(base, key)

