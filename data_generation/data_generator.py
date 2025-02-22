import json
import re
from openai import OpenAI
from typing import List, Optional
from .utils import load_config

def generate_synthetic_data(use_case: str, 
                              num_samples: int = 100, 
                              few_shot_examples: Optional[List[dict]] = None) -> List[dict]:
    """
    Genera datos sintéticos para un caso de uso específico utilizando la API de IA/ML.

    Argumentos:
        use_case (str): El caso de uso específico para el cual generar el conjunto de datos.
        num_samples (int): El número de muestras de datos a generar. Por defecto es 100.
        few_shot_examples (Optional[List[dict]]): Una lista de ejemplos de datos para guiar la IA.
    
    Retorna:
        List[dict]: Una lista de muestras de datos que siguen la estructura definida.
    """
    config = load_config('config/config.yaml')
    client = OpenAI(
        api_key=config['api']['api_key'],
        base_url=config['api']['base_url'],
    )

    # Definir la instrucción base
    prompt = f"""
    Eres un asistente de IA especializado en generar conjuntos de datos de alta calidad para tareas de aprendizaje automático.
    
    **Caso de Uso:** {use_case}
    
    **Instrucciones:**
    - Genera un conjunto de datos con {num_samples} muestras.
    - Cada punto de datos debe ser un objeto JSON.
    - Sigue la estructura definida a continuación.
    - Asegúrate de que los datos sean diversos y cubran varios aspectos del caso de uso.
    - IMPORTANTE: Devuelve ÚNICAMENTE datos JSON válidos en el formato especificado a continuación.
    
    **Estructura del Conjunto de Datos:**
    ```json
    [
        {{
            "entrada": "texto de la pregunta aquí",
            "salida": "texto de la respuesta aquí"
        }},
        ...
    ]
    ```
    
    **Ejemplos Two-Shot:**
    ```json
    [
        {{
            "entrada": "¿Cómo puedo restablecer mi contraseña?",
            "salida": "Para restablecer tu contraseña, haz clic en 'Olvidé mi contraseña' en la página de inicio de sesión y sigue las instrucciones enviadas a tu correo electrónico."
        }},
        {{
            "entrada": "¿Cuál es la política de reembolso?",
            "salida": "Nuestra política de reembolso permite devolver productos dentro de los 30 días posteriores a la compra para obtener un reembolso completo, siempre que los artículos estén en su estado original."
        }}
    ]
    ```
    """
    
    # Agregar ejemplos pocos disparos si se proporcionan
    if few_shot_examples:
        ejemplos_json = json.dumps(few_shot_examples, indent=4, ensure_ascii=False)
        prompt += f"\n\n**Estos son los datos :**\n```json\n{ejemplos_json}\n```\n"

    # Agregar la instrucción para generar el conjunto de datos
    prompt += "\n\n**Conjunto de Datos Generado:**\nDevuelve ÚNICAMENTE JSON válido sin explicaciones ni comentarios."

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-4-340b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente de IA especializado en generar conjuntos de datos de alta calidad para tareas de aprendizaje automático. Devuelve únicamente JSON válido y bien formateado.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=4096,
            temperature=0.7,
        )

        mensaje = response.choices[0].message.content.strip()
        
        # Extraer JSON usando regex para encontrar cualquier contenido entre corchetes
        coincidencia_json = re.search(r'\[(.*?)\]', mensaje, re.DOTALL)
        if coincidencia_json:
            json_str = f"[{coincidencia_json.group(1)}]"
            datos = json.loads(json_str)
        else:
            # Intentar encontrar directamente el array JSON
            coincidencia_json = re.search(r'\[\s*\{.*\}\s*\]', mensaje, re.DOTALL)
            if coincidencia_json:
                datos = json.loads(coincidencia_json.group(0))
            else:
                # Si no se encuentra un array JSON, intentar extraer objetos JSON individuales
                patron_objeto = r'\{\s*"entrada"\s*:\s*".*?"\s*,\s*"salida"\s*:\s*".*?"\s*\}'
                coincidencias = re.findall(patron_objeto, mensaje, re.DOTALL)
                if coincidencias:
                    datos = []
                    for coincidencia in coincidencias:
                        try:
                            obj = json.loads(coincidencia)
                            datos.append(obj)
                        except json.JSONDecodeError:
                            continue
                else:
                    # Último recurso: limpiar la respuesta e intentar nuevamente
                    mensaje_limpio = mensaje.replace('```json', '').replace('```', '')
                    try:
                        # Buscar el primer '[' y el último ']'
                        inicio_idx = mensaje_limpio.find('[')
                        fin_idx = mensaje_limpio.rfind(']')
                        if inicio_idx != -1 and fin_idx != -1:
                            json_str = mensaje_limpio[inicio_idx:fin_idx+1]
                            datos = json.loads(json_str)
                        else:
                            raise ValueError("No se encontraron delimitadores de array JSON en la respuesta.")
                    except Exception:
                        raise ValueError(f"No se pudo analizar el JSON de la respuesta de la API: {mensaje_limpio[:100]}...")

        # Asegurar que tenemos una lista de diccionarios con la estructura correcta
        if not isinstance(datos, list):
            raise ValueError("Los datos generados no son una lista de diccionarios.")
        
        datos_validos = []
        for item in datos:
            if isinstance(item, dict) and "entrada" in item and "salida" in item:
                datos_validos.append(item)
            
        if not datos_validos:
            raise ValueError("No se encontraron elementos de datos válidos en la respuesta.")
            
        return datos_validos
        
    except Exception as e:
        # Proporcionar un conjunto de datos de respaldo con ejemplos mínimos
        print(f"Error al generar el conjunto de datos: {str(e)}")
        return [
            {
                "entrada": f"¿Qué es {use_case}?",
                "salida": f"Esta es una respuesta de muestra sobre {use_case}."
            },
            {
                "entrada": f"Dime más sobre {use_case}.",
                "salida": f"Aquí tienes información adicional sobre {use_case}."
            }
        ]
