import json
import time
import decimal
from random import randint

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

import re

resources_prefix = "cc-smart-door-"
passcodes_table_name = resources_prefix + "passcodes"
visitors_table_name = resources_prefix + "visitors-info"

# recognition_collection = "rekVideoBlog"
app_region = "us-west-2"

def handler(event, context):
    body = json.loads(event.get("body", None))
    print(body)

    print("Body type: {}".format(type(body)))
    print("Body: {}".format(body))
    validation_result = validate(body)
    if validation_result["isValid"]:
        otp = body["otp"]# get OTP from URL
        phone_number = body["phone_number"] # get phone from URL

        print("OTP: {}".format(otp))
        print("Phone: {}".format(phone_number))

        # Validate OTP for the phone number
        try:
            status_validation = validate_user_otp(otp, phone_number)
            print(status_validation)
            if(status_validation == True):
    
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
            print("Response(200) {}: -- ", response)
            return response
            
        except ClientError as e:
            print("ClientError:")
            print(e.response['Error']['Message'])
            
            if not otp or not phone_number:
                return build_response(500, {"message": "Error parsing S3 Link"})
            
    else:
        response = build_response(500, { "message": validation_result["message"] })
        print("Response(500) {}: -- ", response)
        return response
    


def validate(body):
    if not body:
        return build_validation_result(
            False,
            'body',
            'There was no body present in the event'
        )
    # otp = body.get("otp", None)
    otp = body["otp"]
    print(otp)
    # phone_number = body.get("phone", None)

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
    return {'isValid': True}

# Visitor OTP Validation
def isvalid_otp(otp):
    if len(otp) > 5:
        return False
    return True

# Validate OTP from DynamoDB
def validate_user_otp(otp, phone_number):
    dynamodb = boto3.resource('dynamodb', region_name=app_region)
    passcodes_table = dynamodb.Table(passcodes_table_name)
    print("OTP: --", otp)
    print("PhoneNumber: --", phone_number)
    try:
        response = passcodes_table.query(KeyConditionExpression=Key('phone_number').eq(phone_number) and Key('passcode').eq(otp))
        print("Response -----")
        print(response)
        return True
    except ValueError:
        print("Error! No reponse returned from API")
        return False
        
# Grant visitor access through the SmartDoor
def authorise_user(phone_number):
    dynamodb = boto3.resource('dynamodb', region_name=app_region)
    visitors_table = dynamodb.Table(visitors_table_name)
    try:
        response = visitors_table.query(KeyConditionExpression=Key('phone_number').eq(phone_number))
        # Return name of the user from DB using phone_number
        print("Response: -----")
        username = response['Items'][0]['name']
    except ValueError:
        print("Error! No username returned from API")
    
    print("Username {}:", username)
    return username

def build_response(status_code, body):
    response = {}
    response["statusCode"] = status_code
    response["body"] = json.dumps(body)
    response["headers"] = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    print("Response {}:", response["body"])
    return response
