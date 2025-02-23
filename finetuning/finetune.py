import yaml
import logging
from pathlib import Path
from typing import List, Dict
from transformers import AutoModelForCausalLM, TrainingArguments, AutoTokenizer
from .trainer import prepare_trainer
from .utils_functions import preprocess_data, save_training_metrics
import huggingface_hub

def finetune_model(
    raw_data: List[Dict[str, str]], 
    output_dir: str, 
) -> None:
    """
    Fine-tunes the base model using the provided synthetic dataset.
    
    Args:
        raw_data: The synthetic dataset to use for fine-tuning.
        output_dir: Directory where the fine-tuned model will be saved.
        config_path: Path to the configuration file (default: 'config/config.yaml')
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
        RuntimeError: If fine-tuning process fails
    """
    # Ensure output directory exists
    config_path = 'config/config.yaml'
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(output_path / 'finetune.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Load and validate configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_file) as f:
            config = yaml.safe_load(f)
            
        # Validate essential configuration parameters
        required_keys = ['model', 'training', 'logging']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        hf_token = config['training'].get('token_hf')
        if not hf_token:
            raise ValueError("HuggingFace token not found in config. Please add 'token_hf' under 'training' section.")
        
        huggingface_hub.login(token=hf_token)

        # Load tokenizer and model
        logger.info(f"Loading tokenizer and model: {config['model']['base_model']}")
        tokenizer = AutoTokenizer.from_pretrained( 
            config['model']['base_model'],
            trust_remote_code=config['model'].get('trust_remote_code', False)
        )

        # Configure padding token
        if tokenizer.pad_token is None:
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            else:
                # Add a new padding token if no EOS token exists
                tokenizer.add_special_tokens({'pad_token': '<|eot_id|>'})
                logger.info("Added <|eot_id|> token to tokenizer")

        model = AutoModelForCausalLM.from_pretrained(
            config['model']['base_model'],
            trust_remote_code=config['model'].get('trust_remote_code', False),
            device_map="auto"  # Enable automatic device mapping
        )
        
        # Preprocess data
        logger.info("Preprocessing data...")
        dataset = preprocess_data(
            raw_data, 
            tokenizer,
            max_length=config['model'].get('max_length', 512)
        )
        
        # Define training arguments with improved defaults
        training_args = TrainingArguments(
            output_dir=str(output_path),
            num_train_epochs=config['finetuning']['epochs'],
            per_device_train_batch_size=config['finetuning']['batch_size'],
            learning_rate=float(config['finetuning']['learning_rate']),
            save_steps=config['finetuning']['save_steps'],
            save_total_limit=config['finetuning']['save_total_limit'],
            logging_dir=str(output_path / 'logs'),
            logging_steps=config['finetuning']['logging_steps'],
            evaluation_strategy=config['finetuning'].get('evaluation_strategy', 'no'),
            load_best_model_at_end=config['finetuning'].get('load_best_model_at_end', False),
            metric_for_best_model=config['finetuning'].get('metric_for_best_model', None),
            greater_is_better=config['finetuning'].get('greater_is_better', True),
            seed=config['finetuning'].get('seed', 42),
            fp16=config['finetuning'].get('fp16', True),  # Enable mixed precision finetuning
            gradient_accumulation_steps=config['finetuning'].get('gradient_accumulation_steps', 1),
            warmup_steps=config['finetuning'].get('warmup_steps', 0),
            weight_decay=config['finetuning'].get('weight_decay', 0.01),
            logging_first_step=True,
            report_to=["tensorboard"],
        )
        
        # Prepare trainer
        logger.info("Preparing trainer...")
        trainer = prepare_trainer(
            model, 
            tokenizer, 
            training_args, 
            dataset, 
            config['training'].get('data_collator', None)
        )
        
        # Start training
        logger.info("Starting training...")
        training_output = trainer.train()
        
        # Save model and tokenizer
        trainer.save_model(str(output_path))
        tokenizer.save_pretrained(str(output_path))
        logger.info(f"Model saved in {output_path}")
        
        # Save training metrics
        if hasattr(training_output, 'metrics'):
            save_training_metrics(training_output.metrics, str(output_path))
            logger.info("Training metrics saved.")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Fine-tuning failed: {str(e)}") from e