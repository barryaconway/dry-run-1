# Serverless Photo Application

A serverless application for uploading, storing, and retrieving photos using AWS services.

## Architecture

![Architecture Diagram](https://via.placeholder.com/800x400?text=Serverless+Photo+App+Architecture)

### Components

1. **Frontend**
   - Simple HTML/CSS/JavaScript interface
   - Allows users to upload photos and retrieve them using their IDs

2. **API Gateway**
   - HTTP API with two endpoints:
     - `POST /photos`: Upload a photo and its metadata
     - `GET /photos/{photoId}`: Retrieve a photo by its ID

3. **Lambda Functions**
   - `UploadPhotoFunction`: Handles photo uploads, stores in S3, and saves metadata to DynamoDB
   - `GetPhotoFunction`: Retrieves photo metadata from DynamoDB and generates a pre-signed URL for S3 access

4. **Storage**
   - **S3**: Private bucket for storing photo files
   - **DynamoDB**: Table for storing photo metadata with the following attributes:
     - `photoId` (Partition Key): Unique identifier for the photo
     - `fileName`: Original file name
     - `uploadTimestamp`: When the photo was uploaded
     - `s3Key`: Location of the photo in S3

## Setup Instructions

### Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) installed and configured
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed
- Python 3.9 or later

### Deployment

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd photo-app
   ```

2. **Build the application**

   ```bash
   sam build
   ```

3. **Deploy the application**

   ```bash
   sam deploy --guided
   ```

   Follow the prompts to configure your deployment. For the first deployment, you'll need to provide:
   - Stack name (e.g., `photo-app`)
   - AWS Region
   - Environment parameter (dev, test, or prod)

4. **Note the outputs**

   After deployment, SAM will output important information:
   - API Gateway endpoint URL
   - S3 bucket name
   - DynamoDB table name

5. **Update the frontend**

   Open `frontend/index.html` and update the `API_URL` variable with your API Gateway endpoint URL:

   ```javascript
   const API_URL = 'https://your-api-id.execute-api.your-region.amazonaws.com/dev';
   ```

### Local Development

1. **Install dependencies**

   ```bash
   pip install -r src/upload_photo/requirements.txt
   pip install -r src/get_photo/requirements.txt
   ```

2. **Run unit tests**

   ```bash
   python -m unittest discover tests/unit
   ```

3. **Local API testing with SAM**

   ```bash
   sam local start-api
   ```

   This will start a local API Gateway instance that you can use for testing:
   - Upload: `http://localhost:3000/photos`
   - Get: `http://localhost:3000/photos/{photoId}`

4. **Testing the frontend locally**

   You can serve the frontend using any HTTP server, for example:

   ```bash
   cd frontend
   python -m http.server 8000
   ```

   Then open `http://localhost:8000` in your browser.

## Security Considerations

- The S3 bucket is configured as private, with no public access
- API Gateway endpoints use CORS to control access
- Lambda functions use least-privilege IAM roles
- Pre-signed URLs for S3 objects expire after 1 hour (configurable)

## Limitations and Future Improvements

- Currently, there's no authentication or user management
- File size is limited by API Gateway payload limits (10MB)
- No image processing or resizing capabilities
- Could add pagination for retrieving multiple photos

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request