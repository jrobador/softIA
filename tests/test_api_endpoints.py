import sys
import os
import io
import json
import requests
from reportlab.pdfgen import canvas

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Base URL for your running FastAPI server
API_BASE_URL = "http://127.0.0.1:8000"

def create_test_pdf(content=None):
    """Create a test PDF in memory"""
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    
    # Default content if none provided
    if content is None:
        content = [
            "Este es un documento de prueba para el sistema de RAG.",
            "Contiene información sobre productos de software.",
            "Los usuarios pueden solicitar soporte técnico para diversos problemas.",
            "El tiempo de respuesta promedio es de 24 horas para incidentes críticos."
        ]
    
    # Add content to PDF
    y_position = 750
    for line in content:
        c.drawString(50, y_position, line)
        y_position -= 40
    
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer
def test_upload_pdfs_endpoint():
    """Test the PDF upload endpoint with actual pdf_gatos.pdf"""
    print("=== Testing PDF Upload Endpoint with Real File ===")
    
    # Get path to pdf_gatos.pdf in project root
    pdf_path = os.path.join(project_root, "pdf_gatos.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return False

    endpoint = "/finetuning-rag/upload-pdfs"
    full_url = f"{API_BASE_URL}{endpoint}"
    print(f"Testing endpoint: {full_url}")
    print(f"Using PDF file: {pdf_path}")

    try:
        # Read the actual PDF file
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        # Make the API request
        use_case = "sistema de preguntas y respuestas sobre cuidado de gatos"
        
        files = [
            ("files", ("pdf_gatos.pdf", pdf_content, "application/pdf"))
        ]
        
        data = {
            "use_case": use_case
        }

        print("Sending request...")
        response = requests.post(full_url, files=files, data=data)

        # Check response
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API call successful - Status code: {response.status_code}")
            print(f"Response status: {result.get('estado', 'No status provided')}")
            
            if "conjunto_datos" in result and len(result["conjunto_datos"]) > 0:
                dataset = result["conjunto_datos"]
                print(f"Generated {len(dataset)} data samples")
                
                # Display sample data
                print("\nSample data:")
                for i, item in enumerate(dataset[:3]):  # Print first 3 examples
                    print(f"\nExample {i+1}:")
                    print(f"  Entrada: {item.get('entrada', '[No entrada field]')}")
                    salida = item.get('salida', '[No salida field]')
                    print(f"  Salida: {salida[:150]}..." if len(salida) > 150 else f"  Salida: {salida}")
                
                # Save results
                results_dir = os.path.join(project_root, "test_results")
                os.makedirs(results_dir, exist_ok=True)
                
                results_file = os.path.join(results_dir, "api_test_gatos_results.json")
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(dataset, f, ensure_ascii=False, indent=2)
                
                print(f"\nFull results saved to: {results_file}")
                return True
            else:
                print("⚠️ No data returned in the response")
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            print(f"Error details: {response.text}")
    
    except Exception as e:
        print(f"❌ Request failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return False

def test_module_import():
    """Test that we can import the necessary modules"""
    print("=== Testing Module Imports ===")
    try:
        # Try importing key modules
        from data_generation.data_generator import generate_synthetic_data
        print("✅ Successfully imported data_generator module")
        
        from data_generation.finetune_rag import router
        print("✅ Successfully imported finetune_rag module")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("\nCheck that your module structure matches your imports.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_module_import()
    print("\n")
    test_upload_pdfs_endpoint()