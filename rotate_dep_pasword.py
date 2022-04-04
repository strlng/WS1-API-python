#!/usr/bin/python3

import sys
import requests

if len(sys.argv) != 2:
	print("usage: rotate_dep_password.py <deviceID>")
	sys.exit(2)

DEVICE_ID=sys.argv[1]

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

request_url = "{}/api/mdm/devices/{}/commands?command=RotateDEPAdminPassword".format(SERVER, DEVICE_ID)

response = requests.post(request_url, headers=header)
print("status_code: {}".format(str(response.status_code)))
api_response = response.json()
