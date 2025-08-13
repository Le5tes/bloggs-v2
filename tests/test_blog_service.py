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
def setup_blogs_table_for_filtering(dynamodb_resource):
    """Create a mock DynamoDB table with multiple blog posts for flexible filtering testing."""
    # Set up the environment variable for the table name
    table_name = 'test-blogs-table'
    os.environ['DYNAMODB_TABLE_NAME'] = table_name
    
    # Create the test table with a GSI for journey
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'journey', 'AttributeType': 'S'},
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'journey',  # GSI for journey
                'KeySchema': [
                    {'AttributeName': 'journey', 'KeyType': 'HASH'},
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
    
    # Add multiple blog posts with different journeys and dates
    blog_posts = [
        {
            'id': '123',
            'title': 'Blog Post 1',
            'body': 'Content for blog post 1',
            'description': 'Summary for blog post 1',
            'username': 'Test Author',
            'createdAt': 1715318400000,  # 2024-05-10
            'journey': 'europe',
            'tags': ['travel', 'europe'],
            'image': 'image1.png'
        },
        {
            'id': '124',
            'title': 'Blog Post 2',
            'body': 'Content for blog post 2',
            'description': 'Summary for blog post 2',
            'username': 'Test Author',
            'createdAt': 1717396800000,  # 2024-06-03
            'journey': 'europe',
            'tags': ['travel', 'food'],
            'image': 'image2.png'
        },
        {
            'id': '125',
            'title': 'Blog Post 3',
            'body': 'Content for blog post 3',
            'description': 'Summary for blog post 3',
            'username': 'Another Author',
            'createdAt': 1720588800000,  # 2024-07-10
            'journey': 'asia',
            'tags': ['travel', 'asia'],
            'image': 'image3.png'
        },
        {
            'id': '126',
            'title': 'Blog Post 4',
            'body': 'Content for blog post 4',
            'description': 'Summary for blog post 4',
            'username': 'Another Author',
            'createdAt': 1722576000000,  # 2024-08-02
            'journey': 'asia',
            'tags': ['travel', 'food'],
            'image': 'image4.png'
        },
        {
            'id': '127',
            'title': 'Blog Post 5',
            'body': 'Content for blog post 5',
            'description': 'Summary for blog post 5',
            'username': 'Third Author',
            'createdAt': 1723267200000,  # 2024-08-10
            'journey': 'africa',
            'tags': ['travel', 'africa'],
            'image': 'image5.png'
        }
    ]
    
    for post in blog_posts:
        table.put_item(Item=post)
    
    return table_name, blog_posts

def test_filter_blogs_by_journey(dynamodb_resource, setup_blogs_table_for_filtering):
    """Test filtering blogs by journey."""
    table_name, blog_posts = setup_blogs_table_for_filtering
    
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Call the function with a filter for 'europe' journey
    result = blog_service.filter_blogs({'journey': 'europe'})
    
    # Assertions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check that we got the right blog posts (ids 123 and 124)
    result_ids = [post['id'] for post in result]
    assert '123' in result_ids
    assert '124' in result_ids
    assert '125' not in result_ids  # asia
    assert '126' not in result_ids  # asia
    assert '127' not in result_ids  # africa
    
    # Check specific values to confirm we have the correct data
    for post in result:
        assert post['journey'] == 'europe'
        assert 'travel' in post['tags']
        # Verify that body field is excluded for performance
        assert 'body' not in post

def test_filter_blogs_by_date_range(dynamodb_resource, setup_blogs_table_for_filtering):
    """Test filtering blogs by date range."""
    table_name, blog_posts = setup_blogs_table_for_filtering
    
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Call the function with a date range filter (June-July 2024)
    result = blog_service.filter_blogs({
        'start': '2024-06-01',
        'end': '2024-07-31'
    })
    
    # Assertions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check that we got the right blog posts (ids 124, 125)
    result_ids = [post['id'] for post in result]
    assert '123' not in result_ids  # May 10
    assert '124' in result_ids      # June 3
    assert '125' in result_ids      # July 10
    assert '126' not in result_ids  # August 2 (outside range)
    assert '127' not in result_ids  # August 10

def test_filter_blogs_by_journey_and_date_range(dynamodb_resource, setup_blogs_table_for_filtering):
    """Test filtering blogs by both journey and date range."""
    table_name, blog_posts = setup_blogs_table_for_filtering
    
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Call the function with both journey and date range filters
    result = blog_service.filter_blogs({
        'journey': 'asia',
        'start': '2024-07-01',
        'end': '2024-08-05'
    })
    
    # Assertions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check that we got the right blog posts (ids 125 and 126)
    result_ids = [post['id'] for post in result]
    assert '123' not in result_ids  # europe, May
    assert '124' not in result_ids  # europe, June
    assert '125' in result_ids      # asia, July 10
    assert '126' in result_ids      # asia, August 2
    assert '127' not in result_ids  # africa, August 10
    
    # Check specific values to confirm we have the correct data
    for post in result:
        assert post['journey'] == 'asia'

def test_filter_blogs_no_filters(dynamodb_resource, setup_blogs_table_for_filtering):
    """Test filtering blogs with no filters (should return all blogs)."""
    table_name, blog_posts = setup_blogs_table_for_filtering
    
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Call the function with no filters
    result = blog_service.filter_blogs({})
    
    # Assertions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 5  # Should return all 5 blogs
    
    # Another test with None as parameter
    result_none = blog_service.filter_blogs(None)
    assert result_none is not None
    assert isinstance(result_none, list)
    assert len(result_none) == 5  # Should also return all 5 blogs

def test_post_blog_authenticated(dynamodb_resource, setup_blogs_table_for_filtering, mocker):
    """Test posting a blog with valid authentication (happy path)."""
    table_name, blog_posts = setup_blogs_table_for_filtering
    
    valid_token = "dummy.jwt.token"
    
    mocker.patch('utils.auth.CognitoAuth.verify_token', return_value={
        'sub': 'user-123',
        'email': 'testuser@example.com',
        'username': 'testuser'
    })
    
    new_blog = {
        'title': 'New Blog Post',
        'body': 'This is the body of the new blog.',
        'description': 'A short description.',
        'journey': 'europe',
        'tags': ['travel', 'europe'],
        'image': 'new-image.png'
    }
    
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Get the table and mock its put_item method
    table = dynamodb_resource.Table(table_name)
    mock_put_item = mocker.patch.object(table, 'put_item')
    
    # Mock boto3.resource to return our test dynamodb_resource
    # and make sure Table() returns our mocked table
    mock_dynamodb_resource = mocker.MagicMock()
    mock_dynamodb_resource.Table.return_value = table
    mock_boto3_resource = mocker.patch('blog_service.boto3.resource', return_value=mock_dynamodb_resource)
    
    # Call the function to post a blog (to be implemented)
    blog_service.post_blog(new_blog, token=valid_token)
    
    # Assertions - check that put_item was called with the blog data
    mock_put_item.assert_called_once()
    put_item_args = mock_put_item.call_args[1]['Item']
    
    assert put_item_args['title'] == new_blog['title']
    assert put_item_args['body'] == new_blog['body']
    assert put_item_args['journey'] == new_blog['journey']
    assert put_item_args['tags'] == new_blog['tags']
    assert put_item_args['image'] == new_blog['image']
    assert 'id' in put_item_args
    assert 'createdAt' in put_item_args

def test_post_blog_unauthenticated(dynamodb_resource, setup_blogs_table_for_filtering, mocker):
    """Test posting a blog with invalid authentication (should fail)."""
    table_name, blog_posts = setup_blogs_table_for_filtering
    
    invalid_token = "invalid.jwt.token"
    
    # Mock the CognitoAuth.verify_token to return None (invalid token)
    mocker.patch('utils.auth.CognitoAuth.verify_token', return_value=None)
    
    new_blog = {
        'title': 'New Blog Post',
        'body': 'This is the body of the new blog.',
        'description': 'A short description.',
        'journey': 'europe',
        'tags': ['travel', 'europe'],
        'image': 'new-image.png'
    }
    
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import blog_service
    
    # Get the table and mock its put_item method
    table = dynamodb_resource.Table(table_name)
    mock_put_item = mocker.patch.object(table, 'put_item')
    
    # Mock boto3.resource to return our test dynamodb_resource
    mock_dynamodb_resource = mocker.MagicMock()
    mock_dynamodb_resource.Table.return_value = table
    mock_boto3_resource = mocker.patch('blog_service.boto3.resource', return_value=mock_dynamodb_resource)
    
    # Call the function with invalid token - should raise an exception
    with pytest.raises(ValueError, match="Invalid or missing authentication token"):
        blog_service.post_blog(new_blog, token=invalid_token)
    
    # Assertions - check that put_item was NOT called since authentication failed
    mock_put_item.assert_not_called()
