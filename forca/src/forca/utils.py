"""
Módulo com funções utilitárias para o jogo da forca.
"""

import random
from typing import List, Set
from .exceptions import InvalidLetterError, RepeatedLetterError

def select_random_word(word_list: List[str]) -> str:
    """Seleciona uma palavra aleatória da lista fornecida."""
    if not word_list:
        raise ValueError("A lista de palavras não pode estar vazia.")
    return random.choice(word_list).lower()

def validate_letter(letter: str, attempted_letters: Set[str]) -> None:
    """Valida se a letra fornecida é válida e não foi tentada antes."""
    if len(letter) != 1 or not letter.isalpha():
        raise InvalidLetterError("Por favor, digite uma única letra válida.")
    if letter.lower() in attempted_letters:
        raise RepeatedLetterError("Você já tentou esta letra antes.")

def display_word(word: str, correct_letters: Set[str]) -> str:
    """Exibe a palavra com as letras adivinhadas e underscores."""
    return ' '.join([char if char in correct_letters else '_' for char in word])

def get_hint(word: str, correct_letters: Set[str]) -> str:
    """
    Retorna uma dica sobre a palavra (uma letra ainda não adivinhada).
    
    Args:
        word: A palavra a ser adivinhada
        correct_letters: Letras já adivinhadas
        
    Returns:
        Uma dica no formato "A palavra contém a letra: X"
    """
    missing_letters = [char for char in set(word) if char not in correct_letters]
    if not missing_letters:
        return "Você já descobriu todas as letras!"
    
    hint_letter = random.choice(missing_letters)
    return f"A palavra contém a letra: {hint_letter.upper()}"