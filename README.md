# Image Duplicate Detection Service

This project implements a service for detecting duplicate images by converting images into vector representations and storing them in a vector database for duplicate search.

## Features

- **Image Upload API**: Uploads images in various formats and converts them into vector representations.
- **Duplicate Search API**: Searches for duplicate images based on previously uploaded image vectors.
- **Tech Stack**:
  - **PyTorch** for image processing and vectorization using pre-trained model (ResNet).
  - **FastAPI** for building the RESTful API service.
  - **Pinecone DB** as the vector database for storing and querying image vectors.

## API Endpoints

### 1. Add Images

**Endpoint**: `POST /images`

**Request**:
- Accepts a list of images in the following formats:
  - `multipart/form-data`
  - Base64-encoded images
  - URLs of images
- Maximum image size: **10 MB**
- Supported formats: **JPEG, PNG**

**Response**:
- Returns a `request_id` (unique identifier) for tracking and future duplicate searches.
- Number of successfully added images.

### 2. Search for Duplicates

**Endpoint**: `GET /duplicates/{request_id}`

**Request**:
- Path parameter: `request_id` to identify the images for which to search duplicates.

**Response**:
- A list of duplicate images or a message indicating that no duplicates were found.

## Setup and Installation

### Prerequisites
- **Docker** and **Docker Compose** installed on your system.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/DenkoProg/image_duplicate_detection_service
   cd image_duplicate_detection_service
   ```
2. Build and start the service:
   ```bash
   docker-compose up --build
   ```
3. Access the API at `http://localhost:8000`

## Running Tests

To run the test suite inside the Docker container:
```bash
docker-compose run app pytest
```

## Project Structure
- **app/**: Main application code.
- **tests/**: Test suite for the application.
- **Dockerfile**: Container setup.
- **docker-compose.yml**: Automated container orchestration.

## Additional Information
- **Image Processing**: Images are converted to vector representations using pre-trained models from PyTorch.
- **Vector Database**: Pinecone DB stores and retrieves vectors efficiently for duplicate detection.

