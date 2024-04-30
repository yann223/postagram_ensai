#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, TerraformAsset, AssetType
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.default_vpc import DefaultVpc
from cdktf_cdktf_provider_aws.default_subnet import DefaultSubnet
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction
from cdktf_cdktf_provider_aws.lambda_permission import LambdaPermission
from cdktf_cdktf_provider_aws.lambda_event_source_mapping import LambdaEventSourceMapping
from cdktf_cdktf_provider_aws.data_aws_caller_identity import DataAwsCallerIdentity
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket
from cdktf_cdktf_provider_aws.s3_bucket_cors_configuration import S3BucketCorsConfiguration, S3BucketCorsConfigurationCorsRule
from cdktf_cdktf_provider_aws.s3_bucket_notification import S3BucketNotification, S3BucketNotificationLambdaFunction
from cdktf_cdktf_provider_aws.dynamodb_table import DynamodbTable, DynamodbTableAttribute
class ServerlessStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        AwsProvider(self, "AWS", region="us-east-1")

        account_id = DataAwsCallerIdentity(self, "account_id").account_id
        
        bucket = S3Bucket(
            self, "s3_bucket",
            bucket_prefix = "my-cdtf-bucket-postgram-yanis",
            acl="private",
            force_destroy=True,
            versioning={"enabled":True}
            )

        S3BucketCorsConfiguration(
            self, "cors",
            bucket=bucket.id,
            cors_rule=[S3BucketCorsConfigurationCorsRule(
                allowed_headers = ["*"],
                allowed_methods = ["GET", "HEAD", "PUT"],
                allowed_origins = ["*"]
            )]
            )
        dynamo_table = DynamodbTable(
            self, "DynamodDB-table",
            name="postgram_yanis",
            hash_key="PK",
            range_key="SK",
            attribute=[
                DynamodbTableAttribute(name="PK",type="S" ),
                DynamodbTableAttribute(name="SK",type="S" ),
                DynamodbTableAttribute(name="map", type="S"),
                DynamodbTableAttribute(name="open_timestamp", type="S")
            ],
            billing_mode="PROVISIONED",
            read_capacity=5,
            write_capacity=5
        )

        # Packagage du code
        code = TerraformAsset(
            self, "code",
            path="./lambda",
            type= AssetType.ARCHIVE
        )

        lambda_function = LambdaFunction(self,
                "lambda",
                function_name="postgram_yanis",
                runtime="python3.12",
                memory_size=128,
                timeout=120,
                role=f"arn:aws:iam::{account_id}:role/LabRole",
                filename= code.path,
                handler="lambda_function.lambda_handler",
                environment={"variables":{"out_queue_url": "${aws_sqs_queue.output_queue.id}"}}
            )
        
        LambdaEventSourceMapping(
            self, "event_source_mapping",
            event_source_arn=bucket.arn,
            function_name=lambda_function.arn
        )

        permission = LambdaPermission()

        notification = S3BucketNotification()

        TerraformOutput()

        TerraformOutput()

app = App()
ServerlessStack(app, "cdktf_serverless")
app.synth()

