import boto3

def get_dynamodb_client():
    """
    Create and return a DynamoDB client
    """
    return boto3.client('dynamodb')

def get_dynamodb_resource():
    """
    Create and return a DynamoDB resource
    """
    return boto3.resource('dynamodb')
