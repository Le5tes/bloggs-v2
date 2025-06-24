import json
from utils.response import format_response
import blog_service
import image_service

def lambda_handler(event, context):
    """
    Main handler for all routes of the blogging API
    """
    http_method = event.get('httpMethod')
    path = event.get('path', '')
    path_parameters = event.get('pathParameters', {}) or {}
    query_parameters = event.get('queryStringParameters', {}) or {}
    
    # Route handling logic
    if path.startswith('/blogs'):
        if http_method == 'GET':
            # Get blog by ID
            if 'id' in path_parameters:
                blog_id = path_parameters['id']
                blog = blog_service.get_blog_by_id(blog_id)
                if blog:
                    return format_response(200, blog)
                return format_response(404, {'error': 'Blog not found'})
            # Get blogs with filters (date range and/or journey)
            else:
                blogs = blog_service.filter_blogs(query_parameters)
                    
                return format_response(200, blogs)
    
    elif path.startswith('/images'):
        if http_method == 'GET' and 'filename' in path_parameters:
            filename = path_parameters['filename']
            image = image_service.get_image_by_filename(filename)
            if image:
                return format_response(303, image['url'], to_json=False)
            return format_response(404, {'error': 'Image not found'})
    
    # Default response for unhandled routes
    return format_response(404, {'error': 'Not Found'})
