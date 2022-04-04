#!/usr/bin/python3

import requests

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
print(api_response["access_token"])