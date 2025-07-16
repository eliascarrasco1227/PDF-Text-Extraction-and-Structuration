class PromptReader:
    def __init__(self, prompt_path: str):
        self.prompt_path = prompt_path
    
    def read(self) -> str:
        """Lee y devuelve el contenido del prompt"""
        with open(self.prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    @property
    def preview(self) -> str:
        """Muestra las primeras 50 caracteres del prompt"""
        content = self.read()
        return f"{content[:50]}..." if len(content) > 50 else content