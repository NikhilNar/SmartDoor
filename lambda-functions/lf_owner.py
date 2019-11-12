import json

resources_prefix = "cc-smart-door-"
passcodes_table_name = resources_prefix + "passcodes"
visitors_table_name = resources_prefix + "visitors"


def validate(body):
    if not body:
        return build_validation_result(
            False,
            'body',
            'There was no body present in the event'
        )
    v_name = body.get("v_name", None)
    v_phone = body.get("v_number", None)
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
    if not image_url:
        return build_validation_result(
            False,
            'image_url',
            'There was no image_url present in the body'
        )
    return {'isValid': True}


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
        image_url = body["image_url"]
        print("Name: {}".format(v_name))
        print("Phone: {}".format(v_phone))
        print("Image URL: {}".format(image_url))
        body = {"message": "This user is now authorised"}
        
        response = build_response(200, body)
    else:
        response = build_response(500, {"message": validation_result["message"]})

    return response


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


def get_otp():
    pass
    # response = visitorsTable.query(KeyConditionExpression=Key('faceId').eq(faceId))
    # print("response =====")
    # print(response['Items'])
    # if len(response['Items']) > 0:
    #     phoneNumber = response['Items'][0]['phone_number']
    #     passcodeTable = dynamodb.Table('passcodes')
    #     currentEpochTime = int(time.time())
    #     print("currentEpochTime ============")
    #     print(currentEpochTime)
    #     passcodeResponse = passcodeTable.query(
    #         KeyConditionExpression=Key('phone_number').eq(phoneNumber),
    #         FilterExpression=Key('ttl').gt(currentEpochTime))
    #     if len(passcodeResponse['Items']) > 0:
    #         otp = passcodeResponse['Items'][0]['passcode']
    #     else:
    #         otp = randint(10 ** 4, 10 ** 5 - 1)
    #         response = passcodeTable.put_item(
    #             Item={
    #                 "passcode": otp,
    #                 "phone_number": phoneNumber,
    #                 "ttl": int(time.time() + 5 * 60)
    #             })
    #
    #     snsClient.publish(
    #         PhoneNumber=phoneNumber,
    #         Message="Please visit https://smartdoorb1.s3-us-west-2.amazonaws.com/views/html/wp2.html to get access to the door. Your otp is " + str(
    #             otp) + " and will expire in 5 minutes.")
    #     unknownFace = False
