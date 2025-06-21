# Bloggs API v2

A serverless API for a blogging application built with AWS Lambda and API Gateway.

## Structure

- `lambda_function.py`: Main handler for all API routes
- `blog_service.py`: Blog-related business logic
- `image_service.py`: Image-related business logic
- `utils/`: Utility functions
  - `response.py`: API response formatting
  - `dynamodb.py`: DynamoDB helpers

## API Endpoints

- `GET /blogs/{id}`: Get a single blog by ID
- `GET /blogs?start={start_date}&end={end_date}`: Get multiple blogs by date range
- `GET /images/{filename}`: Get an image by filename - returns a presigned url pointing to the image

## Functionality to be implemented
- logging in - use aws cognito
  - Need to be logged in to post new blogs, and post new images, but not to get blogs or images
- post endpoint for blogs
- post images - actually a get endpoint to presigned upload url
- get blogs by "journey"

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Deploy to AWS using your preferred method (AWS CLI, SAM, etc.)
