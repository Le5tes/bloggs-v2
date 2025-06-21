import boto3
import os

# Get bucket name from environment variable - required
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
if not S3_BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME environment variable must be set")

# URL expiration time in seconds (default: 1 hour)
URL_EXPIRATION = int(os.environ.get('PRESIGNED_URL_EXPIRATION', 3600))

def get_image_by_filename(filename):
    """
    Generate a presigned URL for an image in S3 by its filename
    
    Args:
        filename (str): The name of the image file in S3
        
    Returns:
        dict: A dictionary containing the presigned URL or an error message
    """
    try:
        s3_client = boto3.client('s3')
        
        # Generate the presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': filename
            },
            ExpiresIn=URL_EXPIRATION
        )
        
        return {
            'url': presigned_url,
            'expires_in': URL_EXPIRATION
        }
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        return None
