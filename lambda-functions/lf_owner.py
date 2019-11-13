import json
import time
from random import randint

import boto3
from boto3.dynamodb.conditions import Key
import re

resources_prefix = "cc-smart-door-"
passcodes_table_name = resources_prefix + "passcodes"
visitors_table_name = resources_prefix + "visitors"

recognition_collection = "rekVideoBlog"
app_region = "us-west-2"


def handler(event, context):
    print("Event: {}".format(json.dumps(event)))
    body = json.loads(event.get("body", None))
    body = json.loads(body)
    print("Body type: {}".format(type(body)))
    print("Body: {}".format(body))
    validation_result = validate(body)
    if validation_result["isValid"]:
        v_name = body["v_name"]
        v_phone = body["v_number"]
        v_phone = clean_phone(v_phone)
        v_phone = format_phone(v_phone)
        image_url = body["image_url"]
        print("Name: {}".format(v_name))
        print("Phone: {}".format(v_phone))
        print("Image URL: {}".format(image_url))

        # Get bucket and key
        try:
            bucket, key = split_s3_path(image_url)
        except Exception:
            bucket, key = None, None
        if not bucket or not key:
            return build_response(500, {"message": "Error parsing S3 Link"})

        # Index the face and get the faceID
        face_id = index_face_and_get_face_id(bucket, key)

        if not face_id:
            return build_response(500, {"message": {'contentType': 'PlainText', 'content': "No face detected"}})

        # Store into DynamoDB Tables
        store_into_visitors(face_id, image_url, v_name, v_phone)
        store_into_passcodes(face_id)
        body = {"message": "This user is now authorised"}
        response = build_response(200, body)
    else:
        response = build_response(500, {"message": validation_result["message"]})

    return response


def validate(body):
    if not body:
        return build_validation_result(
            False,
            'body',
            'There was no body present in the event'
        )
    v_name = body.get("v_name", None)
    v_phone = body.get("v_number", None)
    v_phone = clean_phone(v_phone)
    image_url = body.get("image_url", None)

    if not v_name:
        return build_validation_result(
            False,
            'v_name',
            'There was no v_name present in the body'
        )
    if not v_phone:
        return build_validation_result(
            False,
            'v_number',
            'There was no v_number present in the body'
        )
    if not isvalid_phone(v_phone):
        return build_validation_result(
            False,
            'v_number',
            'The phone Number entered was invalid'
        )
    if not image_url:
        return build_validation_result(
            False,
            'image_url',
            'There was no image_url present in the body'
        )
    if "s3" not in image_url:
        return build_validation_result(
            False,
            'image_url',
            'This image_url is not a valid S3 URL'
        )
    return {'isValid': True}


def clean_phone(phone):
    phone = re.sub(r'[^0-9]', "", phone)
    if phone and phone[0] == '1':
        phone = phone[1:]
    return phone


def isvalid_phone(phone):
    if len(phone) > 11:
        return False
    if len(phone) == 11 and phone[0] != '1':
        return False
    if len(phone) != 10:
        return False
    return True


def format_phone(phone):
    us_prefix = "+1"
    return us_prefix + phone


def store_into_visitors(face_id, image, name, phone_number):
    dynamodb = boto3.resource('dynamodb', region_name=app_region)
    visitors_table = dynamodb.Table(visitors_table_name)
    visitors_table.put_item(
        Item={
            "faceId": face_id,
            "phone_number": phone_number,
            "name": name,
            "image": image
        })


def store_into_passcodes(face_id):
    sns_client = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb', region_name=app_region)
    visitors_table = dynamodb.Table(visitors_table_name)
    passcode_table = dynamodb.Table(passcodes_table_name)
    response = visitors_table.query(KeyConditionExpression=Key('faceId').eq(face_id))
    print("response =====")
    print(response['Items'])
    if len(response['Items']) > 0:
        phone_number = response['Items'][0]['phone_number']
        current_epoch_time = int(time.time())
        print("current_epoch_time ============")
        print(current_epoch_time)
        passcode_response = passcode_table.query(
            KeyConditionExpression=Key('phone_number').eq(phone_number),
            FilterExpression=Key('ttl').gt(current_epoch_time))
        if len(passcode_response['Items']) > 0:
            otp = passcode_response['Items'][0]['passcode']
        else:
            otp = randint(10 ** 4, 10 ** 5 - 1)
            response = passcode_table.put_item(
                Item={
                    "passcode": otp,
                    "phone_number": phone_number,
                    "ttl": int(time.time() + 5 * 60)
                })
        visit_url = "https://smartdoorb1.s3-us-west-2.amazonaws.com/views/html/wp2" \
                    ".html?phone=" + phone_number
        sns_client.publish(
            PhoneNumber=phone_number,
            Message="Please visit " + visit_url + " to get access to the door. Your otp is " + str(
                otp) + " and will expire in 5 minutes.")


# Hacky method of getting bucket and URL
# Will work only for URL of type:
# https://rekognitionb1.s3-us-west-2.amazonaws.com/kvs1_20191112-034321.jpg
def split_s3_path(s3_path):
    path_parts = s3_path.replace("https://", "").split("/")
    bucket = path_parts.pop(0).split(".").pop(0)
    key = "/".join(path_parts)
    return bucket, key


def build_response(status_code, body):
    response = {}
    response["statusCode"] = status_code
    response["body"] = json.dumps(body)
    response["headers"] = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    return response


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def index_face_and_get_face_id(bucket, key, image_id="1", region=app_region):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.index_faces(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key,
            }
        },
        CollectionId=recognition_collection,
        ExternalImageId=image_id,
        DetectionAttributes=(),
    )
    face_records = response['FaceRecords']
    if face_records and len(face_records) > 0:
        return face_records[0]['Face']['FaceId']
    else:
        return None
