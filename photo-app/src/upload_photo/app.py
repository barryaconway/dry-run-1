import json
import boto3
import os
import uuid
import time
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
PHOTOS_TABLE = os.environ.get('PHOTOS_TABLE', 'Photos')
BUCKET_NAME = os.environ.get('PHOTOS_BUCKET')

# Initialize DynamoDB table resource
photos_table = dynamodb.Table(PHOTOS_TABLE)

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
        API Gateway response with upload status
    """
    try:
        # Parse request body
        if 'body' not in event or not event['body']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing request body'})
            }
            
        body = json.loads(event['body'])
        
        # Validate required fields
        if 'image' not in body or 'fileName' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields: image and fileName'})
            }
        
        # Extract image data and file name
        image_data = body['image']
        file_name = body['fileName']
        
        # Generate a unique photo ID
        photo_id = str(uuid.uuid4())
        
        # Generate S3 key
        s3_key = f"{photo_id}/{file_name}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_data,
            ContentType='image/jpeg'  # Assuming JPEG format, adjust as needed
        )
        
        # Get current timestamp
        current_time = int(time.time())
        
        # Store metadata in DynamoDB
        photos_table.put_item(
            Item={
                'photoId': photo_id,
                'fileName': file_name,
                'uploadTimestamp': current_time,
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
                'message': 'Photo uploaded successfully'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }