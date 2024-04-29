import json
import boto3
import os

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
