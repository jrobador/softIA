import logging
from pathlib import Path
from datasets import Dataset
from typing import List, Dict, Union
import json
from transformers import PreTrainedTokenizer
import torch
import yaml

def load_config(path: str) -> dict:
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def preprocess_data(
    raw_data: List[Dict[str, str]], 
    tokenizer: PreTrainedTokenizer, 
    max_length: int = 512
) -> Dataset:
    """
    Preprocesses raw data for model training.
    
    Args:
        raw_data: List of dictionaries with 'entrada' and 'salida' fields
        tokenizer: Pre-trained tokenizer for processing text
        max_length: Maximum sequence length (default: 512)
    
    Returns:
        Dataset: Dataset with input_ids, attention_mask and labels
        
    Raises:
        ValueError: If data structure is invalid or max_length <= 0
    """
    logger = logging.getLogger(__name__)
    
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    
    # Validate data structure
    if not raw_data:
        raise ValueError("raw_data cannot be empty")
        
    invalid_items = [i for i, item in enumerate(raw_data) 
                    if not isinstance(item, dict) or 
                    'entrada' not in item or 
                    'salida' not in item]
    
    if invalid_items:
        raise ValueError(f"Invalid items found at indices: {invalid_items}")

    # Format text for instruction-response
    formatted_texts = []
    for item in raw_data:
        instruction = item['entrada'].strip()
        response = item['salida'].strip()
        formatted_text = f"Instrucción: {instruction}\nRespuesta: {response}"
        formatted_texts.append(formatted_text)
    
    try:
        # Efficient tokenization with batching
        tokenized_data = tokenizer(
            formatted_texts,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt",
            return_attention_mask=True,
            return_special_tokens_mask=True
        )
        
        # Create dataset with proper typing
        dataset_dict = {
            "input_ids": tokenized_data["input_ids"],
            "attention_mask": tokenized_data["attention_mask"],
            "labels": tokenized_data["input_ids"].clone(),
            "special_tokens_mask": tokenized_data["special_tokens_mask"]
        }
        
        return Dataset.from_dict(dataset_dict)
        
    except Exception as e:
        logger.error(f"Tokenization error: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to tokenize data: {str(e)}") from e

def save_training_metrics(
    metrics: Dict[str, Union[float, int]], 
    output_dir: str
) -> None:
    """
    Saves training metrics to a JSON file in the output directory.
    
    Args:
        metrics: Dictionary of training metrics
        output_dir: Directory where to save the metrics
        
    Raises:
        IOError: If metrics cannot be written
    """
    logger = logging.getLogger(__name__)
    
    output_path = Path(output_dir)
    metrics_path = output_path / "training_metrics.json"
    
    try:
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert non-serializable types to serializable ones
        serializable_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, (int, float, str, bool)):
                serializable_metrics[k] = v
            elif isinstance(v, torch.Tensor):
                serializable_metrics[k] = v.item()
            else:
                serializable_metrics[k] = str(v)
        
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_metrics, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Training metrics saved to {metrics_path}")
        
    except Exception as e:
        logger.error(f"Failed to save training metrics: {str(e)}", exc_info=True)
        raise IOError(f"Could not save training metrics: {str(e)}") from e