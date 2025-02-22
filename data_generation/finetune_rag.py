import io
import logging
from typing import List
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
from data_generation.data_generator import generate_synthetic_data

router = APIRouter()
logger = logging.getLogger(__name__)

class RespuestaConjuntoDatos(BaseModel):
    estado: str
    conjunto_datos: List[dict]

@router.post(
    "/upload-pdfs",
    response_model=RespuestaConjuntoDatos,
    summary="Subir PDFs y generar un conjunto de datos para ajuste fino",
    description="""
    Sube uno o más documentos PDF. El sistema transcribirá el contenido de estos PDFs y generará un conjunto de datos estructurado
    basado en el caso de uso proporcionado. Este conjunto de datos se puede utilizar para ajustar el modelo LLaMA 3.1 405B.
    """
)
async def upload_pdfs(
    use_case: str = Form(..., description="El caso de uso específico para el cual se está generando el conjunto de datos."),
    files: List[UploadFile] = File(..., description="Uno o más archivos PDF a subir y procesar.")
) -> RespuestaConjuntoDatos:
    """
    Endpoint para subir archivos PDF, transcribir su contenido y generar un conjunto de datos para ajuste fino.

    Args:
        use_case (str): El caso de uso específico para el cual se genera el conjunto de datos.
        archivos (List[UploadFile]): Lista de archivos PDF subidos.

    Returns:
        RespuestaConjuntoDatos: Contiene el estado y el conjunto de datos generado.
    """
    logger.info(f"Se recibió una solicitud de subida para el caso de uso: '{use_case}' con {len(files)} archivos.")

    if not files:
        logger.error("No se subieron archivos.")
        raise HTTPException(status_code=400, detail="No se subieron archivos.")

    # Extraer texto de cada PDF
    textos_extraidos = []
    for archivo in files:
        if not archivo.filename.lower().endswith('.pdf'):
            logger.warning(f"Se omite el archivo no PDF: {archivo.filename}")
            continue
        try:
            contenido = await archivo.read()
            lector_pdf = PdfReader(io.BytesIO(contenido))
            texto = ""
            for num_pagina, pagina in enumerate(lector_pdf.pages):
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto += texto_pagina + "\n"
            if not texto.strip():
                logger.warning(f"No se encontró texto en el PDF: {archivo.filename}")
            textos_extraidos.append(texto)
            logger.info(f"Texto extraído de '{archivo.filename}'")
        except Exception as e:
            logger.error(f"No se pudo extraer texto de '{archivo.filename}': {str(e)}")
            raise HTTPException(status_code=500, detail=f"No se pudo extraer texto de '{archivo.filename}': {str(e)}")

    if not textos_extraidos:
        logger.error("No se extrajo texto válido de los PDFs subidos.")
        raise HTTPException(status_code=400, detail="No se extrajo texto válido de los PDFs subidos.")

    # Combinar todos los textos extraídos
    texto_combinado = "\n".join(textos_extraidos)
    logger.info("Texto combinado de todos los PDFs.")

    ejemplos_pocos_disparos = [
        {
            "entrada": "¿Cuál es el tema principal de los documentos subidos?", 
            "salida": f"Los documentos subidos tratan sobre los siguientes temas:\n{texto_combinado[:500]}..."  
        },
        {
            "entrada": "Proporcione un resumen de los puntos clave de los documentos subidos.", 
            "salida": f"Según los documentos subidos, estos son los puntos clave:\n{texto_combinado[:500]}..."  
        }
    ]

    try:
        # Generar conjunto de datos sintético utilizando el texto combinado y el caso de uso
        conjunto_datos = generate_synthetic_data(
            use_case=use_case,
            num_samples=5,  # Ajustar el número de muestras según sea necesario
            few_shot_examples=ejemplos_pocos_disparos  # Opcional: proporcionar ejemplos guía a la IA
        )
        logger.info(f"Conjunto de datos generado con {len(conjunto_datos)} muestras para el caso de uso: '{use_case}'")
    except Exception as e:
        logger.error(f"No se pudo generar el conjunto de datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"No se pudo generar el conjunto de datos: {str(e)}")

    return RespuestaConjuntoDatos(estado="Conjunto de datos generado exitosamente.", conjunto_datos=conjunto_datos)
