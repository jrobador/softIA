from transformers import Trainer, DataCollatorForLanguageModeling, EvalPrediction
from datasets import Dataset
import logging
import numpy as np
from typing import Dict, Optional
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from tqdm import tqdm

def prepare_trainer(
    model, 
    tokenizer, 
    training_args, 
    dataset: Dataset, 
    data_collator: Optional[callable] = None
) -> Trainer:
    """
    Prepares a Trainer with BLEU and ROUGE metrics.
    
    Args:
        model: The model to train
        tokenizer: The tokenizer to use
        training_args: Training arguments
        dataset: The dataset to train on
        data_collator: Optional custom data collator
        
    Returns:
        Trainer: Configured trainer instance
    """
    logger = logging.getLogger(__name__)
    
    if data_collator is None:
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
            pad_to_multiple_of=8  # Optimize for hardware
        )

    def compute_metrics(eval_pred: EvalPrediction) -> Dict[str, float]:
        """Computes BLEU and ROUGE metrics for evaluation."""
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        predictions, labels = eval_pred
        
        # Decode predictions and labels
        try:
            decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
            decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error decoding predictions: {e}")
            return {"error": -1.0}

        logger.info(f"Computing metrics for {len(decoded_preds)} samples...")

        # Calculate metrics with progress bar
        metrics = {
            "bleu": [],
            "rouge1": [],
            "rouge2": [],
            "rougeL": []
        }
        
        for pred, label in tqdm(zip(decoded_preds, decoded_labels), total=len(decoded_preds)):
            # Calculate BLEU
            try:
                bleu = sentence_bleu([label.split()], pred.split())
                metrics["bleu"].append(bleu)
            except Exception as e:
                logger.warning(f"Error calculating BLEU: {e}")
                
            # Calculate ROUGE scores
            try:
                rouge = scorer.score(pred, label)
                metrics["rouge1"].append(rouge['rouge1'].fmeasure)
                metrics["rouge2"].append(rouge['rouge2'].fmeasure)
                metrics["rougeL"].append(rouge['rougeL'].fmeasure)
            except Exception as e:
                logger.warning(f"Error calculating ROUGE: {e}")

        # Calculate averages
        return {
            "bleu": np.mean(metrics["bleu"]) if metrics["bleu"] else -1,
            "rouge1": np.mean(metrics["rouge1"]) if metrics["rouge1"] else -1,
            "rouge2": np.mean(metrics["rouge2"]) if metrics["rouge2"] else -1,
            "rougeL": np.mean(metrics["rougeL"]) if metrics["rougeL"] else -1
        }
    
    return Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics if training_args.evaluation_strategy != "no" else None
    )
