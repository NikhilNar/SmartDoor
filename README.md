# SmartDoor

SmartDoor is a distributed system that authenticates people and provides them with access to a virtual door using AWS services like Kinesis Video Streams, Amazon Rekognition and rest of the AWS stack.

## Architecture

![SmartDoor](https://github.com/NikhilNar/SmartDoor/blob/master/architecture.png)

## Deoployment

### Package:
aws cloudformation package --template-file template.yml --s3-bucket cc-smartdoor --output-template-file output-template.yml

### Deploy
aws cloudformation deploy --template-file output-template.yml --capabilities CAPABILITY_IAM --stack-name smart-door

## Team

* [Nikhil Nar](https://github.com/NikhilNar)
* [Suraj Gaikwad](https://github.com/surajgovardhangaikwad)
* [Chinmay Wyawahare](https://github.com/gandalf1819)
