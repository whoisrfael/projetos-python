"""
Temas visuais e cores para o jogo.
"""

from .config import GameConfig

class Theme:
    """Classe base para temas visuais."""

    @staticmethod
    def color_text(text, color_code):
        """Aplica cor ao texto se estiver habilitado."""
        if GameConfig.USE_COLORS:
            return f"\003{color_code}m{text}\033[0m]"
        return text
    
    @classmethod
    def success(cls, text):
        return cls.color_text(text, '32')  # Verde
    
    @classmethod
    def error(cls, text):
        return cls.color_text(text, '31')  # Vermelho
    
    @classmethod
    def warning(cls, text):
        return cls.color_text(text, '33')  # Amarelo
    
    @classmethod
    def info(cls, text):
        return cls.color_text(text, '34')  # Azul
    
    @classmethod
    def highlight(cls, text):
        return cls.color_text(text, '1')  # Negrito
    
    @classmethod
    def title(cls, text):
        return cls.highlight(cls.info(text))
    
class HangmanTheme(Theme):
    """Tema especifico para o jogo da forca"""

    @classmethod
    def display_word(cls, word, correct_letters):
        """Exibe a palavra com formatação especial."""
        displayed = []
        for char in word:
            if char in correct_letters:
                displayed.append(cls.success(char.upper()))
            else:
                displayed.append('_')
        return ' '.join(displayed)
    
    @classmethod
    def get_hangman_art(cls, state):
        """Retorna a arte ASCII colorida."""
        from .constants import HANGMAN_STATES
        art = HANGMAN_STATES[state]
        if state >= len(HANGMAN_STATES) - 2:
            return cls.error(art)
        return art 
    
    