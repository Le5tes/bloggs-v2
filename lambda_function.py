import json
from utils.response import format_response, redirect
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
        
        elif http_method == 'POST':
            # Create a new blog post (requires authentication)
            try:
                # Extract the authorization token from headers
                headers = event.get('headers', {})
                auth_header = headers.get('Authorization') or headers.get('authorization')
                
                if not auth_header or not auth_header.startswith('Bearer '):
                    return format_response(401, {'error': 'Missing or invalid authorization header'})
                
                token = auth_header.split(' ')[1]
                
                # Parse the request body
                body = event.get('body', '{}')
                if isinstance(body, str):
                    blog_data = json.loads(body)
                else:
                    blog_data = body
                
                # Post the blog
                blog_service.post_blog(blog_data, token)
                
                return format_response(201, {'message': 'Blog created successfully'})
                
            except ValueError as e:
                # Authentication or validation error
                return format_response(401, {'error': str(e)})
            except json.JSONDecodeError:
                return format_response(400, {'error': 'Invalid JSON in request body'})
            except Exception as e:
                return format_response(500, {'error': 'Internal server error'})
    
    elif path.startswith('/images'):
        if http_method == 'GET' and 'filename' in path_parameters:
            filename = path_parameters['filename']
            image = image_service.get_image_by_filename(filename)
            if image:
                return redirect(303, image['url'])
            return format_response(404, {'error': 'Image not found'})
    
    # Default response for unhandled routes
    return format_response(404, {'error': 'Not Found'})
