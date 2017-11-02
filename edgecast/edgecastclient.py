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
		import httplib as http_client
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
	def __init__(self, token, hex): 
		self.token=token
		self.hex=hex
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
	def purge(self, url, platform): 
		payload = {
			'MediaPath' : url, 
			'MediaType' : platform
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
		if verb == "GET":
			r = requests.get(url,headers=headers, json=api_payload, params=query)
			# Print the result
			self.http_status = r.status_code
			self.http_content = r.content
			content=r.content
		elif verb == "PUT":
			r = requests.put(url,headers=headers, json=api_payload, params=query)
			# Print the result
			self.http_status = r.status_code
			self.http_content = r.content
			content=r.content
		elif verb == "POST":
			r = requests.post(url,headers=headers, json=api_payload, params=query)
			# Print the result
			self.http_status = r.status_code
			self.http_content = r.content
			content=r.content
		elif verb == "DELETE":
			r = requests.delete(url,headers=headers, json=api_payload, params=query)
			# Print the result
			self.http_status = r.status_code
			self.http_content = r.content
			content=r.content
		else:
			self.http_status= None
			self.http_content = None
			content = {"msg" : "Invalid method" }
		return (content)
			
		
####################################################################################################

