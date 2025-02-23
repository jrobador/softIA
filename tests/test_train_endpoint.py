import sys
import os
import json
import requests
import pytest

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_train_endpoint_with_real_pdf():
    """Test the /train endpoint with the real pdf_gatos.pdf file in a real environment"""
    print("\n=== Testing Train Endpoint with Real PDF ===")
    
    # Get path to pdf_gatos.pdf
    pdf_path = os.path.join(project_root, "pdf_gatos.pdf")
    
    # Verify that the PDF file exists
    assert os.path.exists(pdf_path), f"PDF file not found at {pdf_path}"
    
    endpoint = "/train"
    full_url = f"{API_BASE_URL}{endpoint}"
    print(f"Testing endpoint: {full_url}")
    print(f"Using PDF file: {pdf_path}")
    
    try:
        # Read the PDF file
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
            
            files = [
                ("files", ("pdf_gatos.pdf", pdf_content, "application/pdf"))
            ]
            
            # Send use_case as query parameter and num_samples as form data
            params = {
                "use_case": "Informacion sobre gatos"
            }
            
            form_data = {
                "num_samples": 5
            }
            
            print("Sending request...")
            response = requests.post(
                full_url, 
                params=params,  # Send use_case as query parameter
                files=files, 
                data=form_data  # Send num_samples as form data
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API call successful - Status code: {response.status_code}")
                
                # Verify the response structure
                assert isinstance(result, dict), "Response is not a dictionary"
                assert "status" in result, "No status in response"
                assert "task_id" in result, "No task_id in response"
                assert "output_dir" in result, "No output_dir in response"
                assert "dataset_size" in result, "No dataset_size in response"
                
                # Verify specific values
                assert result["dataset_size"] == 50, "Incorrect dataset size"
                assert result["status"] in ["training_started", "completed"], "Invalid status"
                assert os.path.exists(result["output_dir"]), "Output directory was not created"
                
                # Save test results
                test_results = {
                    "test_timestamp": str(pytest.timestamp()),
                    "pdf_name": "pdf_gatos.pdf",
                    "response": result,
                    "output_dir_exists": os.path.exists(result["output_dir"]),
                    "output_dir_contents": os.listdir(result["output_dir"]) if os.path.exists(result["output_dir"]) else []
                }
                
                results_dir = os.path.join(project_root, "test_results")
                os.makedirs(results_dir, exist_ok=True)
                
                results_file = os.path.join(results_dir, "api_test_gatos_results.json")
                with open(results_file, "w", encoding='utf-8') as f:
                    json.dump(test_results, f, ensure_ascii=False, indent=4)
                
                print(f"\nTest results saved to: {results_file}")
                return True
            else:
                print(f"❌ API call failed with status code: {response.status_code}")
                print(f"Error details: {response.text}")
                pytest.fail(f"API call failed with status code: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Request failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Test failed with error: {str(e)}")
        
    return False

if __name__ == "__main__":
    pytest.main([__file__])