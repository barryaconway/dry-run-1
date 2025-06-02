import json
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from botocore.exceptions import ClientError

# Add the Lambda function directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/get_photo'))

# Import the Lambda function
import app

class TestGetPhotoFunction(unittest.TestCase):
    """Test cases for the get_photo Lambda function"""

    @patch('app.s3_client')
    @patch('app.dynamodb.Table')
    def test_successful_retrieval(self, mock_table, mock_s3):
        """Test successful photo retrieval"""
        # Mock DynamoDB response
        mock_ddb_table = MagicMock()
        mock_table.return_value = mock_ddb_table
        mock_ddb_table.get_item.return_value = {
            'Item': {
                'photoId': 'test-photo-id',
                'fileName': 'test-image.jpg',
                'uploadTimestamp': '2023-01-01T12:00:00',
                's3Key': 'photos/test-photo-id/test-image.jpg'
            }
        }
        
        # Mock S3 presigned URL
        mock_presigned_url = 'https://test-bucket.s3.amazonaws.com/test-key?signature=abc123'
        mock_s3.generate_presigned_url.return_value = mock_presigned_url
        
        # Create test event
        test_event = {
            'pathParameters': {
                'photoId': 'test-photo-id'
            }
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify DynamoDB get_item was called with correct parameters
        mock_ddb_table.get_item.assert_called_once()
        key = mock_ddb_table.get_item.call_args[1]['Key']
        self.assertEqual(key['photoId'], 'test-photo-id')
        
        # Verify S3 generate_presigned_url was called with correct parameters
        mock_s3.generate_presigned_url.assert_called_once()
        call_args = mock_s3.generate_presigned_url.call_args[1]
        self.assertEqual(call_args['Params']['Bucket'], app.BUCKET_NAME)
        self.assertEqual(call_args['Params']['Key'], 'photos/test-photo-id/test-image.jpg')
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['photoId'], 'test-photo-id')
        self.assertEqual(body['fileName'], 'test-image.jpg')
        self.assertEqual(body['presignedUrl'], mock_presigned_url)
        
    def test_missing_photo_id(self):
        """Test handling of missing photoId parameter"""
        # Create test event with missing photoId
        test_event = {
            'pathParameters': {}
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Missing photoId parameter', body['error'])
        
    @patch('app.dynamodb.Table')
    def test_photo_not_found(self, mock_table):
        """Test handling of non-existent photo"""
        # Mock DynamoDB response for non-existent item
        mock_ddb_table = MagicMock()
        mock_table.return_value = mock_ddb_table
        mock_ddb_table.get_item.return_value = {}  # No Item in response
        
        # Create test event
        test_event = {
            'pathParameters': {
                'photoId': 'non-existent-id'
            }
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('not found', body['error'])
        
    @patch('app.dynamodb.Table')
    @patch('app.s3_client')
    def test_s3_exception(self, mock_s3, mock_table):
        """Test handling of S3 exceptions"""
        # Mock DynamoDB response
        mock_ddb_table = MagicMock()
        mock_table.return_value = mock_ddb_table
        mock_ddb_table.get_item.return_value = {
            'Item': {
                'photoId': 'test-photo-id',
                'fileName': 'test-image.jpg',
                'uploadTimestamp': '2023-01-01T12:00:00',
                's3Key': 'photos/test-photo-id/test-image.jpg'
            }
        }
        
        # Mock S3 client to raise an exception
        mock_s3.generate_presigned_url.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchBucket', 'Message': 'The bucket does not exist'}},
            'generate_presigned_url'
        )
        
        # Create test event
        test_event = {
            'pathParameters': {
                'photoId': 'test-photo-id'
            }
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Failed to generate pre-signed URL', body['error'])

if __name__ == '__main__':
    unittest.main()