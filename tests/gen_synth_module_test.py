#%%
import sys
import os
import json

# Add the project root to the Python path to enable imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Now import using absolute paths
from data_generation.data_generator import generate_synthetic_data

def test_generate_synthetic_data():
    """Test the synthetic data generation functionality"""
    print("=== Testing Synthetic Data Generator ===")
    
    try:
        # Simple test case
        use_case = "soporte técnico para productos de software"
        
        few_shot_examples = [
            {
                "entrada": "¿Cómo puedo restablecer la contraseña de mi cuenta?",
                "salida": "Para restablecer tu contraseña, ve a la página de inicio de sesión, haz clic en 'Olvidé mi contraseña' y sigue las instrucciones enviadas a tu correo electrónico registrado."
            },
            {
                "entrada": "El software se cierra inesperadamente durante el uso",
                "salida": "Si el software se cierra inesperadamente, intenta estos pasos: 1) Reinicia la aplicación, 2) Actualiza a la última versión, 3) Verifica que tu sistema cumpla con los requisitos mínimos, 4) Contacta a soporte técnico si el problema persiste."
            }
        ]
        
        print(f"Generating synthetic data for use case: '{use_case}'")
        print(f"Using {len(few_shot_examples)} few-shot examples")
        
        # Request fewer samples for testing purposes
        test_data = generate_synthetic_data(
            use_case=use_case,
            num_samples=5,  # Small number for quick testing
            few_shot_examples=few_shot_examples
        )
        
        # Check results
        if test_data and len(test_data) > 0:
            print(f"\n✅ Successfully generated {len(test_data)} examples")
            print("\nSample data:")
            for i, item in enumerate(test_data[:3]):  # Print first 3 examples
                print(f"\nExample {i+1}:")
                print(f"  Entrada: {item['entrada']}")
                print(f"  Salida: {item['salida'][:150]}..." if len(item['salida']) > 150 else f"  Salida: {item['salida']}")
            
            # Save the test results to a file
            results_dir = os.path.join(project_root, "test_results")
            os.makedirs(results_dir, exist_ok=True)
            
            results_file = os.path.join(results_dir, "synthetic_data_test_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            
            print(f"\nFull results saved to: {results_file}")
        else:
            print("❌ Failed: No data was generated")
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_synthetic_data()
# %%
