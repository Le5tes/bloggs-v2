import os
import pytest
import boto3
from moto import mock_dynamodb
from unittest import mock
import importlib
import sys
import json
from datetime import datetime

# We'll import blog_service inside the tests after setting up the environment

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
@pytest.fixture
def dynamodb_client(aws_credentials):
    """Create a mock DynamoDB client."""
    with mock_dynamodb():
        yield boto3.client('dynamodb', region_name='us-east-1')

@pytest.fixture
def dynamodb_resource(aws_credentials):
    """Create a mock DynamoDB resource."""
    with mock_dynamodb():
        yield boto3.resource('dynamodb', region_name='us-east-1')
        
@pytest.fixture
def setup_blogs_table(dynamodb_resource):
    """Create a mock DynamoDB table and add a test blog post."""
    # Set up the environment variable for the table name
    table_name = 'test-blogs-table'
    os.environ['DYNAMODB_TABLE_NAME'] = table_name
    
    # Create the test table
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'date', 'AttributeType': 'S'},
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'date-index',
                'KeySchema': [
                    {'AttributeName': 'date', 'KeyType': 'HASH'},
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    # Add a test blog post
    test_blog = {
        'id': '123',
        'title': 'Test Blog Post',
        'body': 'This is a test blog post content.',
        'description': 'This is a test blog post summary.',
        'username': 'Test Author',
        'createdAt': '2024-06-15T15:00:00Z',
        'journey': 'test-journey',
        'tags': ['test', 'blog', 'example'],
        'image': 'test-image.png'
    }
    
    table.put_item(Item=test_blog)
    
    return table_name, test_blog

def test_get_blog_by_id_success(dynamodb_resource, setup_blogs_table):
    """Test successfully retrieving a blog by ID."""
    table_name, test_blog = setup_blogs_table
    
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Call the function
    result = blog_service.get_blog_by_id('123')
    
    # Assertions
    assert result is not None
    assert result['id'] == '123'
    assert result['title'] == 'Test Blog Post'
    assert result['body'] == 'This is a test blog post content.'
    assert result['description'] == 'This is a test blog post summary.'
    assert result['username'] == 'Test Author'
    assert result['createdAt'] == '2024-06-15T15:00:00Z'
    assert result['journey'] == 'test-journey'
    assert result['image'] == 'test-image.png'
    assert 'test' in result['tags']
    assert 'blog' in result['tags']

def test_get_blog_by_id_not_found(dynamodb_resource, setup_blogs_table):
    """Test retrieving a blog by ID that doesn't exist."""
    table_name, test_blog = setup_blogs_table
    
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Call the function with a non-existent ID
    result = blog_service.get_blog_by_id('non-existent-id')
    
    # Assertions
    assert result is None

@pytest.fixture
def setup_blogs_table_with_multiple_entries(dynamodb_resource):
    """Create a mock DynamoDB table with multiple blog posts for date range testing."""
    # Set up the environment variable for the table name
    table_name = 'test-blogs-table'
    os.environ['DYNAMODB_TABLE_NAME'] = table_name
    
    # Create the test table
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'createdAt', 'AttributeType': 'S'},
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'createdAt-index',
                'KeySchema': [
                    {'AttributeName': 'createdAt', 'KeyType': 'HASH'},
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    # Add multiple blog posts with different dates
    blog_posts = [
        {
            'id': '123',
            'title': 'Blog Post 1',
            'body': 'Content for blog post 1',
            'description': 'Summary for blog post 1',
            'username': 'Test Author',
            'createdAt': '2024-05-15T10:00:00Z',
            'journey': 'test-journey',
            'tags': ['test', 'blog'],
            'image': 'image1.png'
        },
        {
            'id': '124',
            'title': 'Blog Post 2',
            'body': 'Content for blog post 2',
            'description': 'Summary for blog post 2',
            'username': 'Test Author',
            'createdAt': '2024-06-01T14:00:00Z',
            'journey': 'test-journey',
            'tags': ['test', 'blog'],
            'image': 'image2.png'
        },
        {
            'id': '125',
            'title': 'Blog Post 3',
            'body': 'Content for blog post 3',
            'description': 'Summary for blog post 3',
            'username': 'Another Author',
            'createdAt': '2024-06-20T09:30:00Z',
            'journey': 'another-journey',
            'tags': ['blog'],
            'image': 'image3.png'
        },
        {
            'id': '126',
            'title': 'Blog Post 4',
            'body': 'Content for blog post 4',
            'description': 'Summary for blog post 4',
            'username': 'Another Author',
            'createdAt': '2024-07-05T16:45:00Z',
            'journey': 'another-journey',
            'tags': ['test'],
            'image': 'image4.png'
        }
    ]
    
    for post in blog_posts:
        table.put_item(Item=post)
    
    return table_name, blog_posts

def test_get_blogs_by_date_range(dynamodb_resource, setup_blogs_table_with_multiple_entries):
    """Test retrieving blogs within a date range."""
    table_name, blog_posts = setup_blogs_table_with_multiple_entries
    
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Call the function with a date range that should include 2 blog posts
    result = blog_service.get_blogs_by_date_range('2024-06-01', '2024-06-30')
    
    # Assertions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check that we got the right blog posts (ids 124 and 125)
    result_ids = [post['id'] for post in result]
    assert '124' in result_ids
    assert '125' in result_ids
    assert '123' not in result_ids
    assert '126' not in result_ids
