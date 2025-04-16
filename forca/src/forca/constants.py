"""
Módulo para constantes do jogo da forca.
"""

# Número máximo de tentativas
MAX_ATTEMPTS = 6

# Lista de palavras para o jogo (pode ser substituída por um arquivo ou API)
WORDS = [
    "python",
    "programacao",
    "desenvolvimento",
    "computador",
    "algoritmo",
    "interface",
    "terminal",
    "jogo",
    "forca",
    "software"
]

# Estados da forca (ASCII art)
HANGMAN_STATES = [
    """
     -----
     |   |
         |
         |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
         |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
     |   |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|   |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|\\  |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|\\  |
    /    |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    --------
    """
]