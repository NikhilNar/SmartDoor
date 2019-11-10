from __future__ import print_function  # Python 2/3 compatibility
import boto3
import json
import decimal
import requests
from requests_aws4auth import AWS4Auth
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-west-2',
                          endpoint_url="http://dynamodb.us-west-2.amazonaws.com")

table = dynamodb.Table('yelp-restaurants')

def send_signed(method, url, service='es', region='us-west-2', body=None):
    # print(body)

    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(credentials.access_key, credentials.secret_key,
                  region, service, session_token=credentials.token)

    fn = getattr(requests, method)
    if body and not body.endswith("\n"):
        body += "\n"
    fn(url, auth=auth, data=body,
       headers={"Content-Type":"application/json"})

# AWS ElasticSearch Endpoint
url = 'https://search-reeco-6uqlqkoo5s2zrbgplboq5shdtq.us-east-1.es.amazonaws.com/restaurant/restaurants'

new_dict = []
#  DynamoDB fields : Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code
with open("cuisines-verona.json") as json_file:
    restaurants = json.load(json_file, parse_float=decimal.Decimal)
    for restaurant in restaurants:
        passcode = restaurant['passcode']

        table.put_item(
            Item = {
                'passcode': passcode
        })
        