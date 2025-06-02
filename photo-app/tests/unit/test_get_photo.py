import json
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the Lambda function directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/get_photo'))

# Import the Lambda function
import app

class TestGetPhotoFunction(unittest.TestCase):
    """Test cases for the get_photo Lambda function"""

    @patch('app.s3_client')
    @patch('app.photos_table')
    def test_successful_retrieval(self, mock_table, mock_s3):
        """Test successful photo retrieval"""
        # Mock photo ID
        photo_id = "12345678-1234-5678-1234-567812345678"
        
        # Create test event
        test_event = {
            'pathParameters': {
                'photoId': photo_id
            }
        }
        
        # Mock DynamoDB response
        mock_table.get_item.return_value = {
            'Item': {
                'photoId': photo_id,
                'fileName': 'test_image.jpg',
                'uploadTimestamp': 1609459200,  # 2021-01-01 00:00:00
                's3Key': f"{photo_id}/test_image.jpg"
            }
        }
        
        # Mock S3 presigned URL
        presigned_url = "https://example-bucket.s3.amazonaws.com/test-image.jpg?signature=abc123"
        mock_s3.generate_presigned_url.return_value = presigned_url
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['photoId'], photo_id)
        self.assertEqual(response_body['fileName'], 'test_image.jpg')
        self.assertEqual(response_body['uploadTimestamp'], 1609459200)
        self.assertEqual(response_body['downloadUrl'], presigned_url)
        
        # Verify DynamoDB was called with correct parameters
        mock_table.get_item.assert_called_once_with(Key={'photoId': photo_id})
        
        # Verify S3 was called with correct parameters
        mock_s3.generate_presigned_url.assert_called_once()
        s3_args = mock_s3.generate_presigned_url.call_args[1]
        self.assertEqual(s3_args['Params']['Key'], f"{photo_id}/test_image.jpg")

    @patch('app.s3_client')
    @patch('app.photos_table')
    def test_missing_photo_id(self, mock_table, mock_s3):
        """Test handling of missing photo ID"""
        # Create test event with missing photo ID
        test_event = {
            'pathParameters': {}  # Missing photoId
        }
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing photoId parameter', json.loads(response['body'])['error'])
        
        # Verify DynamoDB and S3 were not called
        mock_table.get_item.assert_not_called()
        mock_s3.generate_presigned_url.assert_not_called()

    @patch('app.s3_client')
    @patch('app.photos_table')
    def test_photo_not_found(self, mock_table, mock_s3):
        """Test handling of non-existent photo"""
        # Mock photo ID
        photo_id = "nonexistent-id"
        
        # Create test event
        test_event = {
            'pathParameters': {
                'photoId': photo_id
            }
        }
        
        # Mock DynamoDB response for non-existent item
        mock_table.get_item.return_value = {}  # No Item in response
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 404)
        self.assertIn(f'Photo with ID {photo_id} not found', json.loads(response['body'])['error'])
        
        # Verify S3 was not called
        mock_s3.generate_presigned_url.assert_not_called()

    @patch('app.s3_client')
    @patch('app.photos_table')
    def test_s3_error_handling(self, mock_table, mock_s3):
        """Test handling of S3 errors"""
        # Mock photo ID
        photo_id = "12345678-1234-5678-1234-567812345678"
        
        # Create test event
        test_event = {
            'pathParameters': {
                'photoId': photo_id
            }
        }
        
        # Mock DynamoDB response
        mock_table.get_item.return_value = {
            'Item': {
                'photoId': photo_id,
                'fileName': 'test_image.jpg',
                'uploadTimestamp': 1609459200,
                's3Key': f"{photo_id}/test_image.jpg"
            }
        }
        
        # Mock S3 to raise an exception
        mock_s3.generate_presigned_url.side_effect = Exception("S3 error")
        
        # Call the Lambda function
        response = app.lambda_handler(test_event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Failed to generate download URL', json.loads(response['body'])['error'])

if __name__ == '__main__':
    unittest.main()