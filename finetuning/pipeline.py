from typing import List, Dict, Optional
import asyncio
import logging
import json
import io
from pathlib import Path
from fastapi import UploadFile
from PyPDF2 import PdfReader
from data_generation.data_generator import generate_synthetic_data
from .finetune import finetune_model
from finetuning.utils_functions import load_config

logger = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config = load_config(config_path)
        self.output_base_dir = Path(self.config['model']['finetuned_model_dir'])

    async def _extract_text_from_pdfs(self, files: List[UploadFile]) -> List[str]:
        """
        Extracts text from uploaded PDF files.
        """
        texts = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                logger.warning(f"Skipping non-PDF file: {file.filename}")
                continue
            try:
                content = await file.read()
                pdf_reader = PdfReader(io.BytesIO(content))
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    texts.append(text)
                    logger.info(f"Text extracted from '{file.filename}'")
                else:
                    logger.warning(f"No text found in PDF: {file.filename}")
            except Exception as e:
                logger.error(f"Could not extract text from '{file.filename}': {str(e)}")
                raise ValueError(f"PDF text extraction failed for {file.filename}: {str(e)}")
        
        return texts

    def _create_few_shot_examples(self, combined_text: str) -> List[Dict]:
        """
        Creates few-shot examples from the extracted text.
        """
        return [
            {
                "entrada": "¿Cuál es el tema principal de los documentos?",
                "salida": f"Los documentos tratan sobre los siguientes temas:\n{combined_text[:500]}..."
            },
            {
                "entrada": "Proporcione un resumen de los puntos clave.",
                "salida": f"Según los documentos, estos son los puntos clave:\n{combined_text[:500]}..."
            }
        ]

    async def run(
        self,
        use_case: str,
        num_samples: int = 100,
        files: Optional[List[UploadFile]] = None
    ) -> Dict:
        """
        Runs the complete pipeline for data generation and training.
        """
        try:
            # Create output directory
            output_dir = self.output_base_dir / f"finetuned_{use_case.replace(' ', '_')}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Process PDF files if provided
            few_shot_examples = None
            if files:
                # Extract text from PDFs
                extracted_texts = await self._extract_text_from_pdfs(files)
                if not extracted_texts:
                    raise ValueError("No valid text extracted from the provided PDFs")
                
                # Combine extracted texts
                combined_text = "\n".join(extracted_texts)
                
                # Create few-shot examples from the extracted text
                few_shot_examples = self._create_few_shot_examples(combined_text)
                logger.info("Created few-shot examples from PDF content")

            # Generate synthetic data
            logger.info(f"Generating data for use case: {use_case}")
            dataset = generate_synthetic_data(
                use_case=use_case,
                num_samples=num_samples,
                few_shot_examples=few_shot_examples
            )

            if not dataset:
                raise ValueError("Could not generate training data")

            # Save generated dataset
            dataset_path = output_dir / "training_data.json"
            with open(dataset_path, 'w') as f:
                json.dump(dataset, f)
            logger.info(f"Dataset saved to {dataset_path}")

            # Start async training
            training_task = asyncio.create_task(
                self._train_model(dataset, str(output_dir))
            )

            return {
                "status": "training_started",
                "task_id": id(training_task),
                "output_dir": str(output_dir),
                "dataset_size": len(dataset)
            }

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            raise

    async def _train_model(
        self, 
        dataset: List[Dict], 
        output_dir: str,
    ) -> Dict:
        """
        Executes the training in a separate thread.
        """
        try:
            return await asyncio.to_thread(
                finetune_model,
                dataset,
                output_dir
                )
        except Exception as e:
            logger.error(f"Training error: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }