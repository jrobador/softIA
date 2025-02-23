from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import os

class ModelServer:
    """
    Un servidor para manejar la carga y predicción del modelo.
    """
    _cache_modelo = {}
    _cache_tokenizador = {}
    
    def __init__(self, model_path: str):
        """
        Inicializa el ServidorModelo cargando el modelo y el tokenizador.
        
        Args:
            model_path (str): Ruta del directorio del modelo ajustado.
        
        Raises:
            FileNotFoundError: Si el directorio del modelo no existe.
            Exception: Si falla la carga del modelo o del tokenizador.
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        
        if not os.path.exists(model_path):
            self.logger.error(f"La ruta del modelo {model_path} no existe.")
            raise FileNotFoundError(f"La ruta del modelo {model_path} no existe.")
        
        try:
            # Cargar el tokenizador desde la caché o cargarlo y almacenarlo en caché
            if model_path in self._cache_tokenizador:
                self.tokenizador = self._cache_tokenizador[model_path]
                self.logger.info(f"Tokenizador cargado desde la caché para {model_path}.")
            else:
                self.tokenizador = AutoTokenizer.from_pretrained(model_path)
                self._cache_tokenizador[model_path] = self.tokenizador
                self.logger.info(f"Tokenizador cargado y almacenado en caché para {model_path}.")
            
            # Cargar el modelo desde la caché o cargarlo y almacenarlo en caché
            if model_path in self._cache_modelo:
                self.modelo = self._cache_modelo[model_path]
                self.logger.info(f"Modelo cargado desde la caché para {model_path}.")
            else:
                self.modelo = AutoModelForCausalLM.from_pretrained(model_path)
                self.modelo.eval()
                if torch.cuda.is_available():
                    self.modelo.to('cuda')
                self._cache_modelo[model_path] = self.modelo
                self.logger.info(f"Modelo cargado y almacenado en caché para {model_path}.")
        except Exception as e:
            self.logger.error(f"No se pudo cargar el modelo o el tokenizador: {str(e)}")
            raise e
    
    def predict(self, prompt: str, max_length: int = 1024, num_return_sequences: int = 1) -> str:
        """
        Genera una predicción basada en el texto de entrada (prompt).
        
        Args:
            prompt (str): El texto de entrada.
            longitud_maxima (int): La longitud máxima de la secuencia generada.
            num_secuencias (int): Número de secuencias a generar.
        
        Returns:
            str: La predicción generada.
        
        Raises:
            Exception: Si la predicción falla.
        """
        self.logger.info(f"Prompt recibido: {prompt}")
        try:
            entradas = self.tokenizador(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                entradas = {k: v.to('cuda') for k, v in entradas.items()}
            
            with torch.no_grad():
                salidas = self.modelo.generate(
                    **entradas,
                    max_length=max_length,
                    num_return_sequences=num_return_sequences,
                    no_repeat_ngram_size=2,
                    early_stopping=True
                )
            
            prediccion = self.tokenizador.decode(salidas[0], skip_special_tokens=True)
            self.logger.info(f"Predicción generada: {prediccion}")
            return prediccion
        except Exception as e:
            self.logger.error(f"La predicción falló: {str(e)}")
            raise e
