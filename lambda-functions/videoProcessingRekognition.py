from __future__ import print_function


import base64
import json
import boto3
import time
import sys
sys.path.insert(1,'/opt')
import cv2
import datetime
from boto3.dynamodb.conditions import Key
from random import randint

def lambda_handler(event, context):
    print("event =======")
    print(event)
    streamName = "LiveRekognitionVideoAnalysisBlog"
    streamArn = "arn:aws:kinesisvideo:us-west-2:655546244197:stream/LiveRekognitionVideoAnalysisBlog/1572919264579"
    personDetected = False
    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        if personDetected is True:
            break
        payload = base64.b64decode(record['kinesis']['data'])
        result = json.loads(payload.decode('utf-8'))
        print(result['InputInformation'])
        if len(result['FaceSearchResponse']) >0:
            personDetected = True
            print("FaceSearchResponse not empty ="+ json.dumps(result['FaceSearchResponse']))
        else:
            continue
        faceResponse = result['FaceSearchResponse']
        frag_id = result['InputInformation']['KinesisVideo']['FragmentNumber'] 
        print("frag_id =", frag_id)
        
        kvs = boto3.client("kinesisvideo")
        # Grab the endpoint from GetDataEndpoint
        endpoint = kvs.get_data_endpoint(
            APIName="GET_HLS_STREAMING_SESSION_URL",
            StreamName=streamName
        )['DataEndpoint']
        
        # # Grab the HLS Stream URL from the endpoint
        kvam = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
        url = kvam.get_hls_streaming_session_url(
            StreamName=streamName,
            PlaybackMode="LIVE_REPLAY",
            HLSFragmentSelector={
                'FragmentSelectorType': 'PRODUCER_TIMESTAMP',
                'TimestampRange': {
                    'StartTimestamp': result['InputInformation']['KinesisVideo']['ProducerTimestamp']
                }
            }
        )['HLSStreamingSessionURL']
        vcap = cv2.VideoCapture(url)
        final_key='kvs1_'
        s3_client = boto3.client('s3')
        bucket ="rekognitionb1"
        while(True):
            # Capture frame-by-frame
            ret, frame = vcap.read()
        
            if frame is not None:
                # Display the resulting frame
                vcap.set(1, int(vcap.get(cv2.CAP_PROP_FRAME_COUNT)/2)-1)
                final_key=final_key+time.strftime("%Y%m%d-%H%M%S")+'.jpg'
                cv2.imwrite('/tmp/'+final_key,frame)
                s3_client.upload_file('/tmp/'+final_key, bucket, final_key)
                vcap.release()
                print('Image uploaded')
                break
            else:
                print("Frame is None")
                break
        
        # When everything done, release the capture
        vcap.release()
        cv2.destroyAllWindows()
        location = boto3.client('s3').get_bucket_location(Bucket=bucket)['LocationConstraint']
        s3ImageLink = "https://%s.s3-%s.amazonaws.com/%s" % (bucket, location, final_key)
        print("s3ImageLink ===="+s3ImageLink)
        
        snsClient = boto3.client('sns')
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        visitorsTable = dynamodb.Table('cc-smart-door-visitors')
        unknownFace = True
        for face in faceResponse:
            for matchedFace in face["MatchedFaces"]:
                print("matchedFace ===")
                print(matchedFace)
                print(matchedFace['Face']['FaceId'])
                faceId = matchedFace['Face']['FaceId']
                response = visitorsTable.query(KeyConditionExpression=Key('faceId').eq(faceId))
                print("response =====")
                print(response['Items'])
                if len(response['Items']) > 0:
                    phoneNumber = response['Items'][0]['phone_number']
                    passcodeTable = dynamodb.Table('cc-smart-door-passcodes')
                    currentEpochTime = int(time.time())
                    print("currentEpochTime ============")
                    print(currentEpochTime)
                    passcodeResponse = passcodeTable.query(KeyConditionExpression=Key('phone_number').eq(phoneNumber), FilterExpression=Key('ttl').gt(currentEpochTime))
                    if len(passcodeResponse['Items']) > 0:
                        otp = passcodeResponse['Items'][0]['passcode']
                    else:    
                        otp = randint(10**4, 10**5 - 1)    
                        response = passcodeTable.put_item(
                            Item ={
                                "passcode": otp,
                                "phone_number": phoneNumber,
                                "ttl": int(time.time() + 5*60)
                            })
                
                    snsClient.publish(
                        PhoneNumber = phoneNumber,
                        Message = "Please visit https://smartdoorb1.s3-us-west-2.amazonaws.com/views/html/wp2.html?phone="+phoneNumber+" to get access to the door. Your otp is "+ str(otp)+" and will expire in 5 minutes.")
                    unknownFace = False
                break
        if unknownFace:
            print("unknownFace =")
            snsClient.publish(
                PhoneNumber = '+16315683216',
                Message = "A new visitor has arrived. Use the link https://smartdoorb1.s3-us-west-2.amazonaws.com/views/html/wp1.html?image="+ s3ImageLink+" to approve or deny access.")
            unknownFace = False
        # print("dshdhjdjs==========")
            
        
    return 'Successfully processed {} records.'.format(len(event['Records']))
