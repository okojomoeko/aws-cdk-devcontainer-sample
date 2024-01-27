import json
import boto3
import os
import csv
import logging
logger = logging.getLogger()
logger.setLevel("INFO")
# import requests

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')



def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
        bucket = os.environ["BUCKET_NAME"]
        key = os.environ["READ_DATA_KEY"]
        logger.info(key)
        logger.info(bucket)
        response = s3.get_object(Bucket=bucket, Key=key)
        logger.info(response)
        body = response["Body"].read().decode()
        lines = body.split("\n")
        logger.info(body)
        for line in lines:
            l = line.split(",")
            logger.info(l)
            if len(l) ==  2:
                dynamodb.put_item(TableName=os.environ["DYNAMODB_TABLE_NAME"],
                    Item = {
                        "MainTestKey": {
                            "S": l[0]
                        },
                        "SubTestKey": {
                            "S": l[1]
                        }
                    }
                )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Success!",
                # "location": ip.text.replace("\n", "")
            }),
        }
    except Exception as e:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Failed!",
                "error": str(e)
                # "location": ip.text.replace("\n", "")
            }),
        }
