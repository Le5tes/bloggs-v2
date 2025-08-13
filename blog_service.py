import uuid
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
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')
    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME environment variable must be set")
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    print(f"Fetching blog with ID: '{blog_id}', Type: {type(blog_id)}")
    print(f"Using table: {table_name}")
    
    # Ensure blog_id is a string
    blog_id_str = str(blog_id)
    
    try:
        # First, we need to find the item's createdAt value
        # Since we can't query directly by just the partition key,
        # we'll use a query operation to find the matching item
        query_response = table.query(
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': blog_id_str
            }
        )
        
        # If we found a matching item
        if query_response['Count'] > 0:
            # Return the first (should be only) item
            return query_response['Items'][0]
        else:
            return None
            
    except Exception as e:
        print(f"DynamoDB Error: {str(e)}")
        raise

def filter_blogs(filters=None):
    """
    Flexible function to retrieve blog posts based on different filters
    
    Args:
        filters (dict): A dictionary of filters to apply to the query
                        Possible filters:
                        - journey (str): Filter by journey
                        - start (str): Filter by start date (ISO format)
                        - end (str): Filter by end date (ISO format)
                        
    Returns:
        list: A list of blog posts matching the filters
    """
    import datetime
    
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')
    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME environment variable must be set")
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    if filters is None:
        filters = {}
    
    def to_timestamp(date_str):
        if 'T' in date_str:
            dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.datetime.fromisoformat(f"{date_str}T00:00:00+00:00")
        return int(dt.timestamp() * 1000)  # Convert to milliseconds
        
    try:
        expression_values = {}
        filter_expressions = []
        
        if 'start' in filters:
            start_timestamp = to_timestamp(filters['start'])
            print(f"Converted {filters['start']} to {start_timestamp}")
            filter_expressions.append('createdAt >= :start')
            expression_values[':start'] = start_timestamp
            
        if 'end' in filters:
            end_str = filters['end'] 
            end_timestamp = to_timestamp(end_str) if 'T' in end_str else to_timestamp(f"{end_str}T23:59:59")
            print(f"Converted {filters['end']} to {end_timestamp}")
            filter_expressions.append('createdAt <= :end')
            expression_values[':end'] = end_timestamp
        
        if 'journey' in filters:
            query_params = {
                'IndexName': 'journey',
                'KeyConditionExpression': 'journey = :journey_val',
                'ExpressionAttributeValues': {
                    ':journey_val': filters['journey'],
                    **expression_values
                }
            }
            
            if filter_expressions:
                query_params['FilterExpression'] = ' AND '.join(filter_expressions)
                
            print(f"Executing query with params: {query_params}")
            response = table.query(**query_params)
            
        elif filter_expressions:
            scan_params = {
                'FilterExpression': ' AND '.join(filter_expressions),
                'ExpressionAttributeValues': expression_values
            }
            
            print(f"Executing scan with params: {scan_params}")
            response = table.scan(**scan_params)
            
        else:
            print("No filters specified, returning all items")
            response = table.scan()
        
        print(f"Found {response['Count']} blogs matching filters")
        return response.get('Items', [])
            
    except Exception as e:
        print(f"Error in filter_blogs: {str(e)}")
        raise

def post_blog(blog, token):
    import datetime
    import uuid
    from utils.auth import CognitoAuth
    
    auth = CognitoAuth(user_pool_id="eu-west-2_hidczk")
    user_payload = auth.verify_token(token)
    
    if not user_payload:
        raise ValueError("Invalid or missing authentication token")

    table_name = os.environ.get('DYNAMODB_TABLE_NAME')
    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME environment variable must be set")
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    blog['id'] = str(uuid.uuid4())
    blog['createdAt'] = int(datetime.datetime.now().timestamp())

    table.put_item(Item=blog)