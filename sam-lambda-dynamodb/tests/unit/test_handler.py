import json

import pytest

import os
from moto import mock_aws
import boto3
import csv

from hello_world import app


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body": '{ "test": "body"}',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }

TEST_BUCKET_NAME = "example-bucket"
DYNAMODB_TABLE_NAME = "example-table"
READ_DATA_KEY = "test.dat"
TEST_REGION = "ap-northeast-1"

@pytest.fixture(autouse=True)
def mock_env():
    os.environ["BUCKET_NAME"] = TEST_BUCKET_NAME
    os.environ["DYNAMODB_TABLE_NAME"] = DYNAMODB_TABLE_NAME
    os.environ["READ_DATA_KEY"] = READ_DATA_KEY

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = TEST_REGION

@pytest.fixture(scope="function")
def setup_s3(aws_credentials):
    with mock_aws():
        s3client = boto3.client("s3")
        s3client.create_bucket(Bucket=TEST_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": TEST_REGION})
        s3client.upload_file(f"{os.path.dirname(__file__)}/test.dat", TEST_BUCKET_NAME, READ_DATA_KEY)
        yield


@pytest.fixture(scope="function")
def setup_s3_failed(aws_credentials):
    with mock_aws():
        s3client = boto3.client("s3")
        s3client.create_bucket(Bucket=TEST_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": TEST_REGION})
        s3client.upload_file(f"{os.path.dirname(__file__)}/test.dat", TEST_BUCKET_NAME, f"{READ_DATA_KEY}2")
        yield


@pytest.fixture(scope="function")
def setup_dynamodb(aws_credentials):
    with mock_aws():
        dynamodb = boto3.client("dynamodb")
        dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'MainTestKey',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'SubTestKey',
                    'AttributeType': 'S'
                },
            ],
            TableName="example-table",
            KeySchema=[
                {
                    'AttributeName': 'MainTestKey',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'SubTestKey',
                    'KeyType': 'HASH'
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


def test_lambda_handler_success(apigw_event,setup_s3,setup_dynamodb):

    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "Success!"

def test_lambda_handler_failed(apigw_event,setup_s3_failed,setup_dynamodb):
    """ S3 読み込むS3のデータがない(test/key2)場合にfailed
    """
    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 404
    assert "message" in ret["body"]
    assert data["message"] == "Failed!"
