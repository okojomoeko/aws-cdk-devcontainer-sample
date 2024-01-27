import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as AwsCdkProjectTemplate from '../lib/aws-cdk-project-template-stack';

test('SQS Queue and SNS Topic Created', () => {
  const app = new cdk.App();
  // WHEN
  const stack = new AwsCdkProjectTemplate.AwsCdkProjectTemplateStack(
    app,
    'MyTestStack',
  );
  // THEN

  const template = Template.fromStack(stack);

  expect(template.toJSON()).toMatchSnapshot();
});
