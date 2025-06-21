import json

def format_response(status_code, body):
    """
    Format the API Gateway response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # CORS support
        },
        'body': json.dumps(body)
    }
