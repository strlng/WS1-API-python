#!/usr/bin/python3

import sys
import requests
import json

if len(sys.argv) != 2:
	print("usage: get_user_devices.py <userID>")
	sys.exit(2)

USER_ID=sys.argv[1]

try:
	from secrets import secrets
except ImportError:
	print("All your secrets should be kept in secrets.py!")
	raise

SERVER=secrets["server"]
CLIENT_ID=secrets["client_id"]
CLIENT_SECRET=secrets["client_secret"]
ACCESS_TOKEN_URL=secrets["access_token_url"]

token_body = {
	"grant_type": "client_credentials",
	"client_id" : CLIENT_ID,
	"client_secret": CLIENT_SECRET
}

response = requests.post(ACCESS_TOKEN_URL, data=token_body)
response.status_code
api_response = response.json()
#print(api_response["access_token"])

header = {
	"Authorization": "Bearer " + api_response["access_token"],
	"Accept": "application/json;version=2",
	"Content-Type": "application/json"
}

request_url = "{}/api/mdm/devices/search?user={}".format(SERVER, USER_ID)

response = requests.get(request_url, headers=header)
print("status_code: {}".format(str(response.status_code)))
api_response = response.json()

# print the result all pretty like
#print(json.dumps(api_response, sort_keys=True, indent=4))

for device in api_response["Devices"]:
	print("Device Namne: {}".format(device["DeviceFriendlyName"]))
	print("Device ID: {}".format(device["Id"]["Value"]))
