#!/usr/bin/env python3
"""
A simple test harness for manually testing the Lambda function locally.
This script creates mock API Gateway events and calls the Lambda handler directly.
"""

import os
import sys
import json
from pprint import pprint

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set required environment variables for testing
os.environ['S3_BUCKET_NAME'] = 'lestes-tech-media-store'

# Import the Lambda handler after setting environment variables
from lambda_function import lambda_handler

def create_api_event(path, http_method='GET', path_params=None, query_params=None):
    """
    Create a mock API Gateway event
    """
    event = {
        'httpMethod': http_method,
        'path': path,
        'pathParameters': path_params or {},
        'queryStringParameters': query_params or {},
        'headers': {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }
    return event

def print_response(response):
    """
    Pretty print the Lambda response
    """
    print("\n--- Response ---")
    print(f"Status Code: {response.get('statusCode')}")
    print("Headers:")
    for key, value in response.get('headers', {}).items():
        print(f"  {key}: {value}")
    print("\nBody:")
    try:
        body = json.loads(response.get('body', '{}'))
        pprint(body)
    except:
        print(response.get('body', '{}'))
    print("---------------\n")

def test_get_image():
    """
    Test getting an image by filename
    """
    print("\nTesting GET /images/img.png")
    event = create_api_event(
        path='/images/img.png',
        path_params={'filename': 'img.png'}
    )
    response = lambda_handler(event, {})
    print_response(response)

def test_get_blog_by_id():
    """
    Test getting a blog by ID
    """
    print("\nTesting GET /blogs/123")
    event = create_api_event(
        path='/blogs/123',
        path_params={'id': '123'}
    )
    response = lambda_handler(event, {})
    print_response(response)

def test_get_blogs_by_date():
    """
    Test getting blogs by date range
    """
    print("\nTesting GET /blogs?start=2024-01-01&end=2024-12-31")
    event = create_api_event(
        path='/blogs',
        query_params={
            'start': '2024-01-01',
            'end': '2024-12-31'
        }
    )
    response = lambda_handler(event, {})
    print_response(response)

def main():
    """
    Run all tests
    """
    print("=== Starting Lambda Test Harness ===")
    
    # Run tests
    test_get_image()
    test_get_blog_by_id()
    test_get_blogs_by_date()
    
    print("=== Test Harness Complete ===")

if __name__ == "__main__":
    main()
