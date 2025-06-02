import json
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import uuid

# Add the Lambda function directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/upload_photo'))

# Import the Lambda function
import app

class TestUploadPhotoFunction(unittest.TestCase):
    """Test cases for the upload_photo Lambda function"""

    @patch('app.s3_client')
    @patch('app.photos_table')
    @patch('uuid.uuid4')
    def test_successful_upload(self, mock_uuid, mock_table, mock_s3):
        """Test successful photo upload"""
        # Mock UUID generation
        mock_uuid_value = "12345678-1234-5678-1234-567812345678"
        mock_uuid.return_value = uuid.UUID(mock_uuid_value)
        
        # Create test event
        test_event = {
            'body': json.dumps({
                'image': 'base64encodedimage',
                'fileName': 'test_image.jpg'
            })
        }
        
        # Mock S3 and DynamoDB responses
        mock_s3.put_object.return_value = {}
        mock_table.put_item.return_value = {}
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['photoId'], mock_uuid_value)
        
        # Verify S3 was called with correct parameters
        mock_s3.put_object.assert_called_once()
        s3_args = mock_s3.put_object.call_args[1]
        self.assertEqual(s3_args['Key'], f"{mock_uuid_value}/test_image.jpg")
        
        # Verify DynamoDB was called with correct parameters
        mock_table.put_item.assert_called_once()
        ddb_args = mock_table.put_item.call_args[1]
        self.assertEqual(ddb_args['Item']['photoId'], mock_uuid_value)
        self.assertEqual(ddb_args['Item']['fileName'], 'test_image.jpg')
        self.assertEqual(ddb_args['Item']['s3Key'], f"{mock_uuid_value}/test_image.jpg")

    @patch('app.s3_client')
    @patch('app.photos_table')
    def test_missing_body(self, mock_table, mock_s3):
        """Test handling of missing request body"""
        # Create test event with missing body
        test_event = {}
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing request body', json.loads(response['body'])['error'])
        
        # Verify S3 and DynamoDB were not called
        mock_s3.put_object.assert_not_called()
        mock_table.put_item.assert_not_called()

    @patch('app.s3_client')
    @patch('app.photos_table')
    def test_missing_required_fields(self, mock_table, mock_s3):
        """Test handling of missing required fields"""
        # Create test event with missing fields
        test_event = {
            'body': json.dumps({
                'image': 'base64encodedimage'
                # Missing fileName
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing required fields', json.loads(response['body'])['error'])
        
        # Verify S3 and DynamoDB were not called
        mock_s3.put_object.assert_not_called()
        mock_table.put_item.assert_not_called()

    @patch('app.s3_client')
    @patch('app.photos_table')
    def test_s3_error_handling(self, mock_table, mock_s3):
        """Test handling of S3 errors"""
        # Create test event
        test_event = {
            'body': json.dumps({
                'image': 'base64encodedimage',
                'fileName': 'test_image.jpg'
            })
        }
        
        # Mock S3 to raise an exception
        mock_s3.put_object.side_effect = Exception("S3 error")
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Internal server error', json.loads(response['body'])['error'])
        
        # Verify DynamoDB was not called
        mock_table.put_item.assert_not_called()

if __name__ == '__main__':
    unittest.main()