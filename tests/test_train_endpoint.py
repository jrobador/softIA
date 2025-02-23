import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import io
import os
from api.main import app

import sys
# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Create a test client
client = TestClient(app)

# Mock data and helper functions
def create_test_pdf():
    """Creates a mock PDF file in memory for testing"""
    return io.BytesIO(b"Mock PDF content")

def create_mock_upload_file(filename="test.pdf"):
    """Creates a mock UploadFile object"""
    return {
        "files": (filename, create_test_pdf(), "application/pdf")
    }

# Mock training pipeline response
mock_pipeline_response = {
    "status": "training_started",
    "task_id": 123456,
    "output_dir": "/path/to/output",
    "dataset_size": 100
}

@pytest.fixture
def mock_training_pipeline():
    """Fixture to mock the TrainingPipeline class"""
    with patch('api.routes.TrainingPipeline') as mock:
        pipeline_instance = Mock()
        pipeline_instance.run.return_value = mock_pipeline_response
        mock.return_value = pipeline_instance
        yield mock

@pytest.mark.asyncio
async def test_train_endpoint_basic():
    """Test the /train endpoint with basic parameters"""
    with patch('api.routes.training_pipeline') as mock_pipeline:
        mock_pipeline.run.return_value = mock_pipeline_response
        
        response = client.post(
            "/train",
            data={
                "use_case": "customer_support",
                "num_samples": 100
            }
        )
        
        assert response.status_code == 200
        assert response.json() == mock_pipeline_response
        mock_pipeline.run.assert_called_once_with(
            use_case="customer_support",
            num_samples=100,
            files=None
        )

@pytest.mark.asyncio
async def test_train_endpoint_with_files():
    """Test the /train endpoint with file uploads"""
    with patch('api.routes.training_pipeline') as mock_pipeline:
        mock_pipeline.run.return_value = mock_pipeline_response
        
        # Create test files
        files = [
            ("files", ("test1.pdf", create_test_pdf(), "application/pdf")),
            ("files", ("test2.pdf", create_test_pdf(), "application/pdf"))
        ]
        
        response = client.post(
            "/train",
            data={
                "use_case": "document_analysis",
                "num_samples": 50
            },
            files=files
        )
        
        assert response.status_code == 200
        assert response.json() == mock_pipeline_response
        assert mock_pipeline.run.call_count == 1

@pytest.mark.asyncio
async def test_train_endpoint_error_handling():
    """Test error handling in the /train endpoint"""
    with patch('api.routes.training_pipeline') as mock_pipeline:
        mock_pipeline.run.side_effect = Exception("Training pipeline error")
        
        response = client.post(
            "/train",
            data={
                "use_case": "customer_support",
                "num_samples": 100
            }
        )
        
        assert response.status_code == 500
        assert response.json() == {"detail": "Training pipeline error"}

@pytest.mark.asyncio
async def test_train_endpoint_invalid_samples():
    """Test the /train endpoint with invalid number of samples"""
    response = client.post(
        "/train",
        data={
            "use_case": "customer_support",
            "num_samples": -1  # Invalid number of samples
        }
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_train_endpoint_missing_use_case():
    """Test the /train endpoint with missing use case"""
    response = client.post(
        "/train",
        data={
            "num_samples": 100
        }
    )
    
    assert response.status_code == 422  # Validation error

def test_train_endpoint_integration():
    """Integration test for the /train endpoint"""
    # Create a real PDF file for testing
    pdf_content = b"%PDF-1.4\n%Test PDF content"
    test_pdf_path = "test_upload.pdf"
    
    try:
        # Create temporary test PDF
        with open(test_pdf_path, "wb") as f:
            f.write(pdf_content)
        
        with open(test_pdf_path, "rb") as pdf_file:
            files = [
                ("files", ("test_upload.pdf", pdf_file, "application/pdf"))
            ]
            
            response = client.post(
                "/train",
                data={
                    "use_case": "document_analysis",
                    "num_samples": 50
                },
                files=files
            )
            
            assert response.status_code == 200
            result = response.json()
            assert "status" in result
            assert "task_id" in result
            assert "output_dir" in result
            assert "dataset_size" in result
            
    finally:
        # Cleanup
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

if __name__ == "__main__":
    pytest.main([__file__])