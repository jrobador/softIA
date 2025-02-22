import json
import re
from openai import OpenAI
import sys
sys.path.append('c:/Github/softIA')

from data_generation.utils import load_config

async def score_qa_pair(entrada: str, salida: str) -> dict:
    """
    Puntúa un par de preguntas y respuestas utilizando el modelo de recompensa Nemotron-4 340B.

    Args:
    entrada (str): La pregunta/entrada del usuario.
    salida (str): La respuesta del asistente.

    Devuelve:
    dict: Un diccionario con las métricas de utilidad del modelo de recompensa.
    """
    config = load_config('config/config.yaml')
    client = OpenAI(
        api_key=config['api']['api_key'],
        base_url=config['api']['base_url'],
    )

    messages = [
        {"role": "user", "content": entrada},
        {"role": "assistant", "content": salida}
    ]

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-4-340b-reward",
            messages=messages
        )

        print(response)

        metrics = {
            "helpfulness": 0.0,
            "correctness": 0.0,
            "coherence": 0.0,
            "complexity": 0.0,
            "verbosity": 0.0
        }

        logprobs_content = response.choices[0].logprobs.content

        for item in logprobs_content:
            token = item.token.strip().lower()
            logprob = item.logprob
            if token == 'helpfulness':
                metrics["helpfulness"] = logprob
            elif token == 'correctness':
                metrics["correctness"] = logprob
            elif token == 'coherence':
                metrics["coherence"] = logprob
            elif token == 'complexity':
                metrics["complexity"] = logprob
            elif token == 'verbosity':
                metrics["verbosity"] = logprob

        return metrics
    except Exception as e:
        print(f"Error en el scoring: {e}")
        return {
            "helpfulness": 0.0,
            "correctness": 0.0,
            "coherence": 0.0,
            "complexity": 0.0,
            "verbosity": 0.0
        }
    
if __name__ == "__main__":
    # Test the scoring function
    entrada = "How can I reset my account password?"
    salida = "To reset your password, go to the login page, click on 'Forgot my password' and follow the instructions sent to your registered email."
    
    import asyncio
    metrics = asyncio.run(score_qa_pair(entrada, salida))
    print(f"Scoring metrics for QA pair:")
    for metric, value in metrics.items():
        print(f"  {metric.capitalize()}: {value}")
    