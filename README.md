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

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Deploy to AWS using your preferred method (AWS CLI, SAM, etc.)
