import { RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

export class AwsCdkProjectTemplateStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, 'DataBucket', {
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const putDynamoDBFunc = new PythonFunction(this, 'PutDynamoDBFunc', {
      entry: 'sam-lambda-dynamodb/hello_world',
      runtime: lambda.Runtime.PYTHON_3_11,
      index: 'app.py',
      handler: 'lambda_handler',
    });

    bucket.grantRead(putDynamoDBFunc);

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const testApiGW = new apigw.LambdaRestApi(this, 'TestApiGW', {
      handler: putDynamoDBFunc,
    });

    const testTable = new dynamodb.TableV2(this, 'TestTable', {
      partitionKey: {
        name: 'MainTestKey',
        type: dynamodb.AttributeType.STRING,
      },
    });

    testTable.grantWriteData(putDynamoDBFunc);
    putDynamoDBFunc.addEnvironment('BUCKET_NAME', bucket.bucketName);
    putDynamoDBFunc.addEnvironment('DYNAMODB_TABLE_NAME', testTable.tableName);
    putDynamoDBFunc.addEnvironment('READ_DATA_KEY', 'test.dat');
  }
}
