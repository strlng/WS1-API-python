#!/usr/bin/python3

import sys
import argparse
import requests
import json

# create argument parser
parser = argparse.ArgumentParser(description='Execute the named command on found MDM devices.')
parser.add_argument('-c', '--command', help='MDM command to run. Current options: DeviceWipe, EnableRemoteDesktop, DisableRemoteDesktop')
parser.add_argument('-f', '--searchField', default="DeviceFriendlyName", help='MDM search field. Defaults to DeviceFriendlyName. Other potentially useful search fields: MacAddress, SerialNumber, HostName')
parser.add_argument('searchValue', help='MDM search value.')

args = parser.parse_args()

COMMAND = args.command
SEARCH_VALUE = args.searchValue
SEARCH_FIELD = args.searchField

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
		api_response = [x for x in api_response["Devices"] if search_value in x[search_field]]
		device_list = []
		for device in sorted(api_response, key = lambda i: i['DeviceFriendlyName']):
			device_list.append({"deviceid": str(device["Id"]["Value"]), "devicefriendlyname": device["DeviceFriendlyName"]})
		print(device_list)
		return device_list
	else:
		return False

devices = find_devices(access_token, secrets["server"], SEARCH_FIELD, SEARCH_VALUE)

print("The {} command will be sent to the following devices:".format(COMMAND))
print(', '.join([x["devicefriendlyname"] for x in devices if "devicefriendlyname" in x]))
print()

answer = input("Continue? [y/n] ")
if answer.upper() in ["Y", "YES"]:
	device_id_list = [x["deviceid"] for x in devices if "deviceid" in x]
	request_url = "{}/api/mdm/devices/commands".format(secrets["server"])
	for device in devices:
		if COMMAND == "DeviceWipe":
			execute_command = "CustomMdmCommand"
			bodyJSON = bodyJSON = {
				"CommandXML": "<dict><key>RequestType</key><string>EraseDevice</string></dict>"
			}
		elif COMMAND == "EnableRemoteDesktop":
			execute_command = "CustomMdmCommand"
			bodyJSON = {
				"CommandXML": "<dict><key>RequestType</key><string>EnableRemoteDesktop</string></dict>"
			}
		elif COMMAND == "DisableRemoteDesktop":
			execute_command = "CustomMdmCommand"
			bodyJSON = {
				"CommandXML": "<dict><key>RequestType</key><string>DisableRemoteDesktop</string></dict>"
				}
		
		paramaters = {
			"searchby": "deviceID",
			"id": device["deviceid"],
			"command": execute_command
		}
		header = {
			"Authorization": "Bearer {}".format(access_token),
			"Accept": "application/json;version=2",
			"Content-Type": "application/json"
		}
		
		response = requests.post(request_url, params=paramaters, json=bodyJSON, headers=header)
		requestObject = response.request
		#print("status_code: {}".format(str(response.status_code)))
		if response.status_code == 202:
			print("{} success!".format(device["devicefriendlyname"]))
		else:
			api_response = response.json()
			print(api_response)
if answer.upper() in ["N", "NO"]:
	print("no")








