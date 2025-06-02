import json
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import uuid
from datetime import datetime

# Add the Lambda function directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/upload_photo'))

# Import the Lambda function
import app

class TestUploadPhotoFunction(unittest.TestCase):
    """Test cases for the upload_photo Lambda function"""

    @patch('app.s3_client')
    @patch('app.dynamodb.Table')
    @patch('uuid.uuid4')
    @patch('app.datetime')
    def test_successful_upload(self, mock_datetime, mock_uuid, mock_table, mock_s3):
        """Test successful photo upload"""
        # Mock UUID and datetime
        mock_photo_id = '12345678-1234-5678-1234-567812345678'
        mock_uuid.return_value = mock_photo_id
        mock_timestamp = '2023-01-01T12:00:00'
        mock_datetime.utcnow.return_value.isoformat.return_value = mock_timestamp
        
        # Mock DynamoDB table
        mock_ddb_table = MagicMock()
        mock_table.return_value = mock_ddb_table
        
        # Create test event
        test_event = {
            'body': json.dumps({
                'fileName': 'test-image.jpg',
                'image': 'SGVsbG8gV29ybGQ='  # Base64 encoded "Hello World"
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify S3 upload was called with correct parameters
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args[1]
        self.assertEqual(call_args['Bucket'], app.BUCKET_NAME)
        self.assertEqual(call_args['Key'], f'photos/{mock_photo_id}/test-image.jpg')
        self.assertEqual(call_args['ContentType'], 'image/jpg')
        
        # Verify DynamoDB put_item was called with correct parameters
        mock_ddb_table.put_item.assert_called_once()
        item = mock_ddb_table.put_item.call_args[1]['Item']
        self.assertEqual(item['photoId'], mock_photo_id)
        self.assertEqual(item['fileName'], 'test-image.jpg')
        self.assertEqual(item['uploadTimestamp'], mock_timestamp)
        self.assertEqual(item['s3Key'], f'photos/{mock_photo_id}/test-image.jpg')
        
        # Verify response
        self.assertEqual(response['statusCode'], 201)
        body = json.loads(response['body'])
        self.assertEqual(body['photoId'], mock_photo_id)
        self.assertEqual(body['fileName'], 'test-image.jpg')
        self.assertEqual(body['uploadTimestamp'], mock_timestamp)
        
    def test_missing_body(self):
        """Test handling of missing request body"""
        # Create test event with missing body
        test_event = {}
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Missing request body', body['error'])
        
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        # Create test event with missing fields
        test_event = {
            'body': json.dumps({
                'fileName': 'test-image.jpg'
                # Missing 'image' field
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Missing required fields', body['error'])
        
    @patch('app.s3_client')
    @patch('app.dynamodb.Table')
    def test_s3_exception(self, mock_table, mock_s3):
        """Test handling of S3 exceptions"""
        # Mock S3 client to raise an exception
        mock_s3.put_object.side_effect = Exception("S3 error")
        
        # Create test event
        test_event = {
            'body': json.dumps({
                'fileName': 'test-image.jpg',
                'image': 'SGVsbG8gV29ybGQ='
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Internal server error', body['error'])

if __name__ == '__main__':
    unittest.main()