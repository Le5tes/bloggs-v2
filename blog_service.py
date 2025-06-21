import boto3
import os

def get_blog_by_id(blog_id):
    """
    Retrieve a single blog post by its ID from DynamoDB
    
    Args:
        blog_id (str): The unique identifier of the blog post to retrieve
        
    Returns:
        dict: The blog post data or None if not found
    """
    # Get table name from environment variable
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')
    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME environment variable must be set")
    
    # Create DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Get the blog post
    response = table.get_item(
        Key={
            'id': blog_id
        }
    )
    
    # Return the blog post if found
    if 'Item' in response:
        return response['Item']
    
    return None

def get_blogs_by_date_range(start_date, end_date):
    """
    Retrieve multiple blog posts within a date range from DynamoDB
    
    Args:
        start_date (str): The start date in ISO format (YYYY-MM-DD)
        end_date (str): The end date in ISO format (YYYY-MM-DD)
        
    Returns:
        list: A list of blog posts within the date range
    """
    # Get table name from environment variable
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')
    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME environment variable must be set")
    
    # Create DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Convert dates to ISO format if they aren't already
    # Our test is using simple YYYY-MM-DD format, but our data has full timestamps
    if 'T' not in start_date:
        start_date = f"{start_date}T00:00:00Z"
    if 'T' not in end_date:
        end_date = f"{end_date}T23:59:59Z"
    
    # Scan the table for blogs within the date range
    response = table.scan(
        FilterExpression="createdAt BETWEEN :start_date AND :end_date",
        ExpressionAttributeValues={
            ':start_date': start_date,
            ':end_date': end_date
        }
    )
    
    # Return the blogs
    return response.get('Items', [])
