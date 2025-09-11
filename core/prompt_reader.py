# prompt_reader.py
from core.logger_config import app_logger

class PromptReader:
    def __init__(self, prompt_path: str):
        self.prompt_path = prompt_path
        self.logger = app_logger
    
    def read(self) -> str:
        """Lee y devuelve el contenido del prompt"""
        try:
            self.logger.debug(f"Leyendo prompt desde: {self.prompt_path}")
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self.logger.debug(f"Prompt leído ({len(content)} caracteres)")
                return content
        except Exception as e:
            self.logger.error(f"Error al leer prompt: {str(e)}")
            raise
    
    @property
    def preview(self) -> str:
        """Muestra las primeras 50 caracteres del prompt"""
        try:
            content = self.read()
            preview = f"{content[:50]}..." if len(content) > 50 else content
            self.logger.debug(f"Preview del prompt: {preview}")
            return preview
        except Exception as e:
            self.logger.error(f"Error al obtener preview: {str(e)}")
            return "Error al leer prompt"