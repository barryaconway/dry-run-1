# Serverless Photo Upload Application

A serverless application for uploading and retrieving photos using AWS services. This application provides a simple way to store and manage photos in the cloud with a user-friendly web interface.

## Architecture

![Architecture Diagram](https://mermaid.ink/img/pako:eNp1kc1uwjAQhF9l5XOqhFCgUC6VeuqhPfVQcTHOBqwmduQ1KEKQ9947dgiUH3HyZb-Z2fVuQOmUhgxKvFq-Qs1Vw0XFtYFXrpvGcAGfXMJJKQQsZhO4Wy5gOp3A3WwOD7MFLJcPMF8-wuPTEyQJJPEYkjSFJMtgNB5DGkWQjUaQxTGM4wTSLIU4jmGUJJBEMaTZCNJRBkkcwTiJIYtTiJIYRnECaZJBHEWQZWOIkxFkcQZJnEIcJZDFGSRRCqM4hSxOIIlSiOMMkjCFNMogjlJIwxTiOIEsTCCLUojDGNIwgSyMIQ0TSMMYsjCBLIwhDRPIwgTSIIYsDCENEkiDCLIghjQIIQ1iyIIQ0iCCzA8h9SPIfB8y34fUDyH1I8j8ADLPh9QLIfV8yDwPUs-HzPMgdX3IXA9S14fMcSF1PMgcFzLbgcxxILUdyGwbMtuC1LIgsyxITQsyw4TUMCHTDUh1AzJNg1TTIdU0yFQVUlWFTFEgUxRIZRkyWYZMkiCTJEhFETJRhEwQIOMFyHgeMp6DjOPwH_Gd1Vc?type=png)

The application uses the following AWS services:

- **API Gateway**: HTTP API with two endpoints:
  - `POST /photos`: Upload a photo and its metadata
  - `GET /photos/{photoId}`: Retrieve a photo using a pre-signed URL

- **Lambda Functions**:
  - `UploadPhotoFunction`: Handles photo uploads, stores the photo in S3, and saves metadata to DynamoDB
  - `GetPhotoFunction`: Retrieves photo metadata from DynamoDB and generates a pre-signed URL for the S3 object

- **S3**: Private bucket for storing photos

- **DynamoDB**: Table for storing photo metadata with the following attributes:
  - `photoId` (Partition Key): Unique identifier for the photo
  - `fileName`: Original file name of the photo
  - `uploadTimestamp`: When the photo was uploaded
  - `s3Key`: S3 object key for the photo

## Prerequisites

- [AWS Account](https://aws.amazon.com/account/)
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Python 3.9+](https://www.python.org/downloads/)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/photo-app.git
cd photo-app
```

### 2. Install Dependencies

```bash
# Install Python dependencies for local development
pip install -r src/upload_photo/requirements.txt
pip install -r src/get_photo/requirements.txt

# Install test dependencies
pip install pytest pytest-mock
```

### 3. Run Tests

```bash
# Run unit tests
python -m pytest tests/unit/
```

### 4. Deploy the Application

```bash
# Build the SAM application
sam build

# Deploy to AWS (first time)
sam deploy --guided

# For subsequent deployments
sam deploy
```

During the guided deployment, you'll be prompted for:
- Stack Name: (e.g., photo-app)
- AWS Region: (e.g., us-east-1)
- Environment parameter: (dev or prod)
- Confirm changes before deployment: (Y/n)
- Allow SAM CLI IAM role creation: (Y/n)
- Disable rollback: (y/N)

### 5. Test the API

After deployment, SAM will output the API Gateway endpoint URL. You can use this URL to test the API:

```bash
# Example: Upload a photo
curl -X POST https://your-api-id.execute-api.your-region.amazonaws.com/photos \
  -H "Content-Type: application/json" \
  -d '{"fileName":"test.jpg","image":"base64encodedimage"}'

# Example: Get a photo
curl https://your-api-id.execute-api.your-region.amazonaws.com/photos/your-photo-id
```

### 6. Run the Frontend Locally

Open the `frontend/index.html` file in your browser to test the application locally. Update the `API_ENDPOINT` variable in the JavaScript code to point to your deployed API Gateway endpoint.

## Local Development

### Running Lambda Functions Locally

You can use SAM CLI to run the Lambda functions locally:

```bash
# Invoke the upload function
sam local invoke UploadPhotoFunction --event events/upload_event.json

# Invoke the get function
sam local invoke GetPhotoFunction --event events/get_event.json
```

### Starting the API Locally

```bash
sam local start-api
```

This will start a local API Gateway at http://127.0.0.1:3000 that you can use for testing.

## Project Structure

```
photo-app/
├── src/
│   ├── upload_photo/
│   │   ├── app.py            # Upload photo Lambda function
│   │   └── requirements.txt  # Dependencies for upload function
│   ├── get_photo/
│   │   ├── app.py            # Get photo Lambda function
│   │   └── requirements.txt  # Dependencies for get function
├── tests/
│   ├── unit/
│   │   ├── test_upload_photo.py  # Unit tests for upload function
│   │   └── test_get_photo.py     # Unit tests for get function
├── frontend/
│   └── index.html            # Simple HTML frontend for testing
├── template.yaml             # SAM template defining AWS resources
└── README.md                 # This file
```

## Security Considerations

- The S3 bucket is configured as private, and photos are only accessible via pre-signed URLs
- Lambda functions follow the principle of least privilege with specific IAM permissions
- API Gateway endpoints can be further secured with authentication mechanisms (e.g., AWS Cognito)

## Cleanup

To avoid incurring charges, delete the AWS resources when you're done:

```bash
sam delete
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.