#!/usr/bin/python3

import sys
import argparse
import requests
import json

# create argument parser
parser = argparse.ArgumentParser(description='Get value os sensor on found MDM devices.')
parser.add_argument('-f', '--searchField', default="DeviceFriendlyName", help='MDM search field. Defaults to DeviceFriendlyName')
parser.add_argument('-s', '--sensor', help='The sensor name')
parser.add_argument('-v', '--searchValue', type=str, help='MDM search value.')

args = parser.parse_args()

SEARCH_VALUE = args.searchValue
SEARCH_FIELD = args.searchField
SENSOR = args.sensor
	
try:
	from secrets import secrets
except ImportError:
	print("All your secrets should be kept in secrets.py!")
	raise

def get_access_token(access_token_url, client_id, client_secret):
	token_body = {
		"grant_type": "client_credentials",
		"client_id" : client_id,
		"client_secret": client_secret
	}
	
	response = requests.post(access_token_url, data=token_body)
	if response.status_code == 200:
		api_response = response.json()
		return api_response["access_token"]
	else:
		return False
	
access_token = get_access_token(secrets["access_token_url"], secrets["client_id"], secrets["client_secret"])

def find_devices(access_token, server, search_field, search_value):
	header = {
		"Authorization": "Bearer {}".format(access_token),
		"Accept": "application/json;version=2",
		"Content-Type": "application/json"
	}
		
	request_url = "{}/api/mdm/devices/search".format(server)
	
	response = requests.get(request_url, headers=header)
	if response.status_code == 200:
		api_response = response.json()
		if search_value is not None:
			api_response = [x for x in api_response["Devices"] if search_value in x[search_field]]
		else:
			api_response = [x for x in api_response["Devices"]]
		device_list = []
		for device in sorted(api_response, key = lambda i: i['DeviceFriendlyName']):
			device_list.append({"deviceid": str(device["Id"]["Value"]), "devicefriendlyname": device["DeviceFriendlyName"], "Uuid": device["Uuid"]})
		return device_list
	else:
		return False

devices = find_devices(access_token, secrets["server"], SEARCH_FIELD, SEARCH_VALUE)

device_id_list = [x["deviceid"] for x in devices if "deviceid" in x]
for device in devices:
	request_url = "{}/api/mdm/devices/{}/sensors".format(secrets["server"], device["Uuid"])
	header = {
		"Authorization": "Bearer {}".format(access_token),
		"Accept": "application/json;version=2",
		"Content-Type": "application/json"
	}
	response = requests.get(request_url, headers=header)
	#print("status_code: {}".format(str(response.status_code)))
	api_response = response.json()
	#print(json.dumps(api_response, sort_keys=True, indent=4))
	# Key-value pair you want to filter by
	desired_key = "name"
	desired_value = SENSOR
	
	# Use a list comprehension to filter dictionaries
	filtered_dicts = [d for d in api_response["results"] if d.get(desired_key) == desired_value]

	# print(api_response)
	# print(json.dumps(api_response["results"], sort_keys=True, indent=4))
	if len(filtered_dicts) > 0:
		print("Device Name: {}, {} value: {}".format(device["devicefriendlyname"], SENSOR, filtered_dicts[0]["value"]))







