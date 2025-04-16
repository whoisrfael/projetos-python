"""
Módulo para exceções personalizadas do jogo da forca.
"""

class InvalidLetterError(Exception):
    """Exceção lançada quando uma letra inválida é fornecida."""
    pass

class GameOverError(Exception):
    """Exceção lançada quando uma ação é tentada em um jogo já encerrado."""
    pass

class RepeatedLetterError(Exception):
    """Exceção lançada quando uma letra já tentada é fornecida novamente."""
    pass

class SaveLoadError(Exception):
    """Exceção lançada quando ocorre um erro ao salvar ou carregar o jogo."""
    pass