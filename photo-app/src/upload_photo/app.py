import json
import os
import uuid
import base64
import boto3
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
PHOTOS_TABLE = os.environ.get('PHOTOS_TABLE', 'Photos')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'photo-app-bucket')

def lambda_handler(event, context):
    """
    Lambda function to handle photo uploads.
    
    This function:
    1. Receives photo data and metadata from API Gateway
    2. Uploads the photo to S3
    3. Stores metadata in DynamoDB
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with status code and body
    """
    try:
        logger.info("Processing upload request")
        
        # Parse request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing request body'})
            }
            
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Validate required fields
        if 'fileName' not in body or 'image' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields: fileName and image'})
            }
            
        file_name = body['fileName']
        image_data = body['image']
        
        # Remove header if present (e.g., "data:image/jpeg;base64,")
        if ';base64,' in image_data:
            image_data = image_data.split(';base64,')[1]
            
        # Decode base64 image
        decoded_image = base64.b64decode(image_data)
        
        # Generate unique photo ID
        photo_id = str(uuid.uuid4())
        
        # Generate S3 key
        s3_key = f"photos/{photo_id}/{file_name}"
        
        # Upload to S3
        logger.info(f"Uploading file to S3: {s3_key}")
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=decoded_image,
            ContentType=f"image/{file_name.split('.')[-1]}"  # Infer content type from extension
        )
        
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Store metadata in DynamoDB
        logger.info(f"Storing metadata in DynamoDB for photo: {photo_id}")
        table = dynamodb.Table(PHOTOS_TABLE)
        table.put_item(
            Item={
                'photoId': photo_id,
                'fileName': file_name,
                'uploadTimestamp': timestamp,
                's3Key': s3_key
            }
        )
        
        # Return success response
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'photoId': photo_id,
                'fileName': file_name,
                'uploadTimestamp': timestamp,
                's3Key': s3_key
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }