from fastapi import APIRouter, HTTPException
from data_generation.data_generator import generate_synthetic_data
from finetuning.finetune import finetune_model
from deployment.serve_model import ModelServer
from deployment.utils import get_latest_model_path
import yaml
import os
import json

router = APIRouter()

@router.post("/train", summary="Entrenar un modelo ajustado según un caso de uso")
async def train(use_case: str):
    try:
        # Generar datos sintéticos
        data = generate_synthetic_data(use_case)
        if not data:
            raise ValueError("No se generaron datos para el caso de uso proporcionado.")

        # Ajustar el modelo
        config = yaml.safe_load(open('config/config.yaml'))
        output_dir = os.path.join(config['model']['finetuned_model_dir'], f"finetuned_{use_case.replace(' ', '_')}")
        os.makedirs(output_dir, exist_ok=True)

        finetune_model(data, output_dir)

        return {"status": "ajuste fino completado", "model_path": output_dir}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/chat", summary="Chatear con un modelo ajustado específico")
async def chat(model_name: str, message: str):
    try:
        config = yaml.safe_load(open('config/config.yaml'))
        model_dir = config['model']['finetuned_model_dir']
        model_path = os.path.join(model_dir, model_name) if model_name else get_latest_model_path(model_dir)
        
        server = ModelServer(model_path)
        response = server.predict(message)
        return {"response": response, "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", summary="Listar todos los modelos ajustados disponibles")
async def list_models():
    try:
        config = yaml.safe_load(open('config/config.yaml'))
        model_dir = config['model']['finetuned_model_dir']
        if not os.path.exists(model_dir):
            return {"models": []}
            
        models = [d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]
        model_details = []
        
        for model in models:
            model_path = os.path.join(model_dir, model)
            created_time = os.path.getctime(model_path)
            metrics_file = os.path.join(model_path, "training_metrics.json")
            metrics = {}
            if os.path.exists(metrics_file):
                with open(metrics_file, "r") as f:
                    metrics = json.load(f)
                    
            model_details.append({
                "name": model,
                "created": created_time,
                "metrics": metrics
            })
            
        return {"models": model_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/training/status/{task_id}", summary="Obtener el estado del entrenamiento")
async def training_status(task_id: str):
    # Implementar un método para verificar el estado del entrenamiento usando task_id
    # Se podría utilizar un seguimiento de estado basado en archivos o una base de datos
    try:
        status_file = f"training_status_{task_id}.json"
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                status = json.load(f)
            return status
        return {"status": "desconocido", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
