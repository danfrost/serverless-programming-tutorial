import json
import hashlib
import logging
import boto3
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.info("The handler started")

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def upload(event, context):
    logger.info(event)

    jsondata = json.loads(event['body'])
    data = jsondata['data']

    data_hash = hashlib.sha1(data.encode('utf-8')).hexdigest()

    s3conn = boto3.resource('s3')
    s3conn.Bucket('dropbucketlxf').put_object(
                                    Key=data_hash + '.json',
                                    Body=json.dumps(data))

    body = {
        "message": "Uploaded file"
    }

    response = {
        "statusCode": 200,
        "body": "done"
    }
    return response

def scan(event, context):
    logger.info(event)

    object_key = event['Records'][0]['s3']['object']['key']
    tmpfilenamein = '/tmp/tmpfilein_' + object_key

    logger.info("We got file: " + object_key)
    logger.info("tmpfilenamein = " + tmpfilenamein)

    s3conn = boto3.resource('s3')

    s3conn.Bucket('dropbucketlxf').download_file(object_key, tmpfilenamein)
    bad_lines = []
    for line in open(tmpfilenamein, 'r'):
        if 'badthings' in line:
            bad_lines.append(line)

    logger.info("Got bad_lines = {}".format(bad_lines))
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('badones')

    for line in bad_lines:
        table.put_item(Item={'line': line})

    response = {
        "statusCode": 200,
        "body": "Completed scan"
    }

    return response

def get_bad_lines(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accounts')
    items = table.scan()
    response = {
        "responseCode": 200,
        "body": json.dumps(items)
    }
    return response
