import os
import pytest
import boto3
from moto import mock_s3
from unittest import mock
import importlib
import sys

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
@pytest.fixture
def s3_client(aws_credentials):
    """Create a mock S3 client."""
    with mock_s3():
        yield boto3.client('s3', region_name='us-east-1')

@pytest.fixture
def setup_s3_bucket(s3_client):
    """Create a mock S3 bucket and add a test image."""
    bucket_name = 'test-blog-images'
    s3_client.create_bucket(Bucket=bucket_name)
    
    # Upload a test image
    s3_client.put_object(
        Bucket=bucket_name,
        Key='test-image.jpg',
        Body=b'fake image content'
    )
    
    # Set the bucket name in environment
    os.environ['S3_BUCKET_NAME'] = bucket_name
    
    return bucket_name

def test_get_image_by_filename_success(s3_client, setup_s3_bucket):
    """Test getting a presigned URL for an existing image."""
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import image_service
    
    # Patch the boto3.client to use our mocked version
    with mock.patch('boto3.client', return_value=s3_client):
        # Call the function
        result = image_service.get_image_by_filename('test-image.jpg')
        
        # Assertions
        assert result is not None
        assert 'url' in result
        assert 'expires_in' in result
        assert result['expires_in'] == 3600
        assert 'https://' in result['url']
        assert 'test-image.jpg' in result['url']

def test_get_image_by_filename_not_found(s3_client, setup_s3_bucket):
    """Test getting a presigned URL for a non-existent image."""
    # Import the module after environment variables are set
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import image_service
    
    # Patch the boto3.client to use our mocked version
    with mock.patch('boto3.client', return_value=s3_client):
        # Call the function with a non-existent image
        result = image_service.get_image_by_filename('non-existent-image.jpg')
        
        # The function should still return a URL (S3 generates presigned URLs
        # even for objects that don't exist yet)
        assert result is not None
        assert 'url' in result
        assert 'non-existent-image.jpg' in result['url']

def test_missing_bucket_env_var():
    """Test that an error is raised when S3_BUCKET_NAME is missing."""
    # Remove the environment variable
    if 'S3_BUCKET_NAME' in os.environ:
        del os.environ['S3_BUCKET_NAME']
    
    # Import should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        # First import the module (it might be in sys.modules already)
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        import image_service
        
        # Force a reload to trigger the initialization code again
        importlib.reload(image_service)
    
    assert "S3_BUCKET_NAME environment variable must be set" in str(excinfo.value)
