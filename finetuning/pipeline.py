from typing import List, Dict, Optional
import asyncio
import logging
import json
from pathlib import Path
from fastapi import UploadFile
from data_generation.data_generator import generate_synthetic_data
from .finetune import finetune_model
from finetuning.utils_functions import load_config

logger = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config = load_config(config_path)
        self.output_base_dir = Path(self.config['model']['finetuned_model_dir'])

    async def run(
        self,
        use_case: str,
        num_samples: int = 100,
        files: Optional[List[UploadFile]] = None
    ) -> Dict:
        """
        Ejecuta el pipeline completo de generación de datos y entrenamiento.
        """
        try:
            # Crear directorio de salida
            output_dir = self.output_base_dir / f"finetuned_{use_case.replace(' ', '_')}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generar datos
            logger.info(f"Generando datos para caso de uso: {use_case}")
            dataset = await generate_synthetic_data(
                use_case=use_case,
                num_samples=num_samples,
                files=files
            )

            if not dataset:
                raise ValueError("No se pudieron generar datos de entrenamiento")
            # Guardar dataset generado
            dataset_path = output_dir / "training_data.json"
            with open(dataset_path, 'w') as f:
                json.dump(dataset, f)
            logger.info(f"Dataset guardado en {dataset_path}")
            logger.info(f"Dataset guardado en {dataset_path}")

            # Iniciar entrenamiento asíncrono
            training_task = asyncio.create_task(
                self._train_model(dataset, str(output_dir), use_case)
            )

            return {
                "status": "training_started",
                "task_id": id(training_task),
                "output_dir": str(output_dir),
                "dataset_size": len(dataset)
            }

        except Exception as e:
            logger.error(f"Error en pipeline: {str(e)}", exc_info=True)
            raise

    async def _train_model(
        self, 
        dataset: List[Dict], 
        output_dir: str,
        use_case: str
    ) -> Dict:
        """
        Ejecuta el entrenamiento en un thread separado.
        """
        try:
            return await asyncio.to_thread(
                finetune_model,
                dataset,
                output_dir,
                use_case
            )
        except Exception as e:
            logger.error(f"Error en entrenamiento: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }