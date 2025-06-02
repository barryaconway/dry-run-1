import json
import os
import boto3
import logging
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
PHOTOS_TABLE = os.environ.get('PHOTOS_TABLE', 'Photos')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'photo-app-bucket')
URL_EXPIRATION = int(os.environ.get('URL_EXPIRATION', 3600))  # Default: 1 hour

def lambda_handler(event, context):
    """
    Lambda function to retrieve photo metadata and generate a pre-signed URL.
    
    This function:
    1. Extracts photoId from the path parameter
    2. Retrieves photo metadata from DynamoDB
    3. Generates a pre-signed URL for the S3 object
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with status code and body containing photo metadata and URL
    """
    try:
        logger.info("Processing get photo request")
        
        # Extract photoId from path parameters
        if 'pathParameters' not in event or not event['pathParameters'] or 'photoId' not in event['pathParameters']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing photoId parameter'})
            }
            
        photo_id = event['pathParameters']['photoId']
        
        # Get photo metadata from DynamoDB
        logger.info(f"Retrieving metadata for photo: {photo_id}")
        table = dynamodb.Table(PHOTOS_TABLE)
        response = table.get_item(
            Key={
                'photoId': photo_id
            }
        )
        
        # Check if photo exists
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Photo with ID {photo_id} not found'})
            }
            
        photo_metadata = response['Item']
        s3_key = photo_metadata['s3Key']
        
        # Generate pre-signed URL
        logger.info(f"Generating pre-signed URL for S3 object: {s3_key}")
        try:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': BUCKET_NAME,
                    'Key': s3_key
                },
                ExpiresIn=URL_EXPIRATION
            )
        except ClientError as e:
            logger.error(f"Error generating pre-signed URL: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Failed to generate pre-signed URL'})
            }
            
        # Return photo metadata with pre-signed URL
        result = {
            **photo_metadata,
            'presignedUrl': presigned_url
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving photo: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }