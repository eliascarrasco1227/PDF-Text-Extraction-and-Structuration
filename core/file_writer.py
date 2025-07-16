import os
from datetime import datetime

class FileWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_with_timestamp(self, content: str) -> str:
        """Guarda con formato fecha/hora"""
        timestamp = datetime.now().strftime("%d/%m/%Y_%H:%M:%S")
        filename = f"respuesta_{timestamp}.txt"
        return self._save_file(content, filename)
    
    def save_with_counter(self, content: str) -> str:
        """Guarda con numeración secuencial"""
        counter = 1
        while os.path.exists(self._get_path(f"respuesta_{counter}.txt")):
            counter += 1
        return self._save_file(content, f"respuesta_{counter}.txt")
    
    def _save_file(self, content: str, filename: str) -> str:
        """Método interno para guardado"""
        path = self._get_path(filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def _get_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)