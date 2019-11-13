import json
import time
from random import randint

import boto3
from boto3.dynamodb.conditions import Key
import re

resources_prefix = "cc-smart-door-"
passcodes_table_name = resources_prefix + "passcodes"
visitors_table_name = resources_prefix + "visitors"

# recognition_collection = "rekVideoBlog"
app_region = "us-west-2"

def handler(event, context):
    print("Event: {}".format(json.dumps(event)))
    body = json.loads(event.get("body", None))
    body = json.loads(body)
    print("Body type: {}".format(type(body)))
    print("Body: {}".format(body))
    validation_result = validate(body)
    if validation_result["isValid"]:
        otp = body["otp"]  # get OTP from URL
        phone = body["phone"]   # get phone from URL

        print("OTP: {}".format(otp))
        print("Phone: {}".format(phone))

        # Validate OTP for the phone number
        if(validate_user_otp(otp, phone_number) == True):

            # Fetch Username from DynamoDB using phone as key
            user_name = authorise_user(phone_number)

            body = {
                "message": "This user is now authorised",
                "user_name": user_name
            }
        
        else:
            body = {
                "message": "Invalid OTP. Access Denied!"
            }
        
        response = build_response(200, body)
    else:
        response = build_response(500, { "message": validation_result["message"] })

    return response


def validate(body):
    if not body:
        return build_validation_result(
            False,
            'body',
            'There was no body present in the event'
        )
    otp = body.get("otp", None)

    if not otp:
        return build_validation_result(
            False,
            'otp',
            'There was no OTP present in the body'
        )

    if not isvalid_otp(otp):
        return build_validation_result(
            False,
            'otp',
            'The OTP was invalid'
        )

# Visitor OTP Validation
def isvalid_otp(otp):
    if len(otp) > 5:
        return False
    return True

# Validate OTP from DynamoDB
def validate_user_otp(otp, phone_number):
    dynamodb = boto3.resource('dynamodb', region_name=app_region)
    passcodes_table = dynamodb.Table(passcodes_table_name)
    response = passcodes_table.get_item(
        Key={
            "otp": otp,
            "phone_number": phone_number
        })
    
    print("Response -----")
    print(response['item']['otp'])
    
    if(otp == response['item']['otp']):
        return True  # OTP matched with DB OTP
    return False  # OTP doesn't match with DB OTP

# Grant visitor access through the SmartDoor
def authorise_user(phone_number):
    dynamodb = boto3.resource('dynamodb', region_name=app_region)
    passcodes_table = dynamodb.Table(visitors_table_name)
    response = passcodes_table.get_item(
        Key={
            "phone_number": phone_number
        })

    # Return name of the user from DB using phone_number
    print("Response: -----")
    print(response['item']['name'])
    username = response['item']['name']
    return username

def build_response(status_code, body):
    response = {}
    response["statusCode"] = status_code
    response["body"] = json.dumps(body)
    response["headers"] = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    return response
