import boto3
import os
import shutil
import json
import datetime
import pprint 

import helper

# place the API key, account hex id, base url and platform into config.py
import config_edgecast as config
     
assert config.hex,"Error: missing hex account number"
assert config.token, "Error: missing API token"
assert config.base_url, "Error: missing base URL"
assert (config.platform in ['flash', 'small', 'large', 'adn']), "Error: bad or misssing delivery platform"
assert (config.lambda_region in ['us-east-2', 
                                'us-east-1', 
                                'us-west-1', 
                                'us-west-2', 
                                'ap-northeast-2', 
                                'ap-south-1', 
                                'ap-southeast-1', 
                                'ap-southeast-2', 
                                'ap-northeast-1', 
                                'ca-central-1', 
                                'eu-central-1', 
                                'eu-west-1', 
                                'eu-west-2', 
                                'sa-east-1' 
                                ]), "Error: bad or misssing AWS region"
# http://docs.aws.amazon.com/general/latest/gr/rande.html#lambda_region
assert config.sourcebucket, "Error: missing S3 bucket"


debug=False

lambda_region=config.lambda_region
lambda_function = 's3-purge-edgecast'
memory=1024
sourcebucket = config.sourcebucket
    
RoleName='Lambda_access_S3'
zipfileName='%s.zip' % lambda_function
handler='purge-edgecast.main'

iam = boto3.client('iam', region_name=lambda_region)
aws_lambda= boto3.client('lambda', region_name=lambda_region)      
aws_events= boto3.client('events', region_name=lambda_region)      
s3= boto3.client('s3', region_name=lambda_region)      
aws_logs= boto3.client('logs', region_name=lambda_region)      

boto_response=iam.get_user()
if debug: print pprint.pprint(boto_response)

accountid = boto_response["User"]["UserId"]
print "Account is %s" % accountid

role="arn:aws:iam::%s:role/service-role/%s" % (accountid, RoleName)

# Send all config strings as lambda variables
variables = {key:val for (key,val) in config.__dict__.items() if not "__" in key and type(val) is str}

helper.CreateZip(zipfileName, verbose=True)
print "Zip file %s created" % zipfileName


AssumeRolePolicy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            }
        }
    ]
}
try:
    boto_response = iam.get_role(
        RoleName=RoleName
    )
    if debug: print pprint.pprint(boto_response)
except:
    boto_response = iam.create_role(
        RoleName=RoleName,
        Path='/service-role/',
        AssumeRolePolicyDocument=json.dumps(AssumeRolePolicy),
        Description='Role to execute Lambda'
    )
    if debug: print pprint.pprint(boto_response)


role = boto_response['Role']['Arn']
print "Have Role %r" % role

policies = [
            'arn:aws:iam::aws:policy/AWSLambdaBasicExecuteRole', 
            'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
            ]
for policy in policies:             
    try:
        print "Adding policy", policy
        boto_response = iam.attach_role_policy(
            RoleName=RoleName,
            PolicyArn=policy
        )
        print "Policy added"
        if debug: print pprint.pprint(boto_response)
    except:
        pass

lambda_arn = "arn:aws:lambda:%s:%s:function:%s" % (lambda_region, accountid, lambda_function)

print "Creating function", lambda_function, "in region" , lambda_region
try: 
    boto_response=aws_lambda.create_function(
        FunctionName=lambda_function,
        Runtime='python2.7',
        Role=role,
        Handler=handler,
        Code={
            'ZipFile':  open(zipfileName, 'rb').read()
        },
        Description='Auto purge Edgecast from S3 bucket updates',
        Timeout=300,
        MemorySize=memory,
        Publish=True,
        Environment={
            'Variables': variables
        },
        Tags={
            'domain': 'admin'
        }
    )
    if debug: print pprint.pprint(boto_response)
except: 
    boto_response=aws_lambda.update_function_code(
        FunctionName=lambda_function,
        ZipFile=open(zipfileName, 'rb').read() , 
        Publish=True
        )
    if debug: print pprint.pprint(boto_response)
    print 'function %r in %s updated' % (lambda_function, lambda_region)
    
    boto_response=aws_lambda.update_function_configuration(
        FunctionName=lambda_function,
        Handler=handler,
        Timeout=300,
        MemorySize=memory,
        Environment={
            'Variables': variables
        }
        )
    if debug: print pprint.pprint(boto_response)
    
print "Function", lambda_arn, "in region" , lambda_region, "created"

permission_id = "%s_%s" % (sourcebucket.replace('.', '_'), lambda_function)

try:
    boto_response=aws_lambda.add_permission(
        FunctionName=lambda_function,
        StatementId=permission_id,
        Action="lambda:InvokeFunction",
        Principal='s3.amazonaws.com',
        SourceArn='arn:aws:events:::%s' % ( sourcebucket ) ,
        SourceAccount = accountid
    )
    if debug: print pprint.pprint(boto_response)
except:
    boto_response=aws_lambda.remove_permission(
        FunctionName=lambda_function,
        StatementId=permission_id
    )
    if debug: print pprint.pprint(boto_response)
    
    boto_response=aws_lambda.add_permission(
        FunctionName=lambda_function,
        StatementId=permission_id,
        Action="lambda:InvokeFunction",
        Principal='s3.amazonaws.com',
        SourceArn='arn:aws:events:::%s' % ( sourcebucket ) ,
        SourceAccount = accountid
    )
    if debug: print pprint.pprint(boto_response)

print "Added permisions for S3 bucket", sourcebucket, "to call lambda"
    
boto_response = s3.put_bucket_notification_configuration(
    Bucket=sourcebucket,
    NotificationConfiguration={
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': lambda_arn,
                'Events': [
                    's3:ObjectCreated:*'
                ]
            }
        ]
    }
)   
if debug: print pprint.pprint(boto_response)

print "Added trigger on S3 bucket", sourcebucket, "to call lambda"

try: 
    boto_response = aws_logs.create_log_group(
        logGroupName='/aws/lambda/{}'.format(lambda_function)
    )

    if debug: print pprint.pprint(boto_response)
except: 
    pass
    
print "Created log group", '/aws/lambda/{}'.format(lambda_function)

quit()

"""
to do: 
Add event notifications on errors

aws  logs    put-metric-filter ^
            --log-group-name "/aws/lambda/%lambda_function%"  ^
            --filter-name "%lambda_function%_errors_metric" ^
            --filter-pattern "\"Error error ERROR\"" ^
            --metric-transformations   metricValue=1,metricNamespace=UsageErrors,metricName=Runtime   ^
           --region %region%  ^
           --output json




aws cloudwatch  put-metric-alarm ^
       --alarm-name "%lambda_function%_UsageErrors"  ^
       --alarm-description "Alarm for %lambda_function%"   ^
       --actions-enabled ^
       --metric-name Runtime ^
       --namespace UsageErrors ^
       --statistic SampleCount ^
       --period 3600 ^
       --unit Count ^
       --evaluation-periods 1 ^
       --threshold 0 ^
       --comparison-operator GreaterThanThreshold ^
       --treat-missing-data notBreaching ^
       --dimensions "Name=LogGroupName,Value=/aws/lambda/%lambda_function%" ^
       --namespace "AWS/Logs" ^
       --alarm-actions  "arn:aws:sns:%region%:%accountid%:%SNS_NOTIFICATION%" ^
        --region %region%  ^
        --output json


"""