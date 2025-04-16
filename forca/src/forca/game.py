""" Módulo principal com a lógica do jogo da forca """

from typing import Set, Dict, Optional
import random
from .exceptions import InvalidLetterError, GameOverError, RepeatedLetterError
from .utils import validate_letter, display_word, get_hint
from .constants import HANGMAN_STATES
from .config import GameConfig
from .themes import HangmanTheme
from .save_load import GameSaveManager


class HangmanGame:
    """Classe principal que implementa a lógica do jogo da forca."""

    def __init__(self, word_list: Optional[list] = None, word: Optional[str] = None):
        """
        Inicializa um novo jogo.

        Args:
            word_list: Lista de palavras. Se None, usa a lista padrão.
            word: Palavra específica para o jogo (para testes ou carregar).
        """
        self.word_list = self._load_word_list() if word_list is None else word_list
        self.word = word.lower() if word else self._select_random_word()
        self.attempted_letters: Set[str] = set()
        self.incorrect_attempts = 0
        self.correct_letters: Set[str] = set()
        self.game_over = False
        self.player_name: Optional[str] = None
        self.start_time: Optional[float] = None
        self.hint_shown = False
        self.winner: Optional[bool] = None

    def _load_word_list(self) -> list:
        """Carrega a lista de palavras do arquivo configurado."""
        try:
            words_file = GameConfig.get_words_file()
            if words_file.exists():
                with open(words_file, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            return ["python", "programacao", "desenvolvimento"]
        except IOError:
            return ["python", "programacao", "desenvolvimento"]

    def _select_random_word(self) -> str:
        """Seleciona uma palavra aleatória da lista."""
        if not self.word_list:
            raise ValueError("A lista de palavras não pode estar vazia.")
        return random.choice(self.word_list).lower()

    def get_current_state(self) -> Dict:
        """Retorna o estado atual do jogo."""
        return {
            'displayed_word': HangmanTheme.display_word(self.word, self.correct_letters),
            'attempted_letters': sorted(self.attempted_letters),
            'remaining_attempts': GameConfig.MAX_ATTEMPTS - self.incorrect_attempts,
            'hangman_state': HangmanTheme.get_hangman_art(self.incorrect_attempts),
            'hint': self._get_hint() if self._should_show_hint() else None,
            'score': self.calculate_score(),
            'game_over': self.game_over,
            'winner': self.winner,
            'word': self.word if self.game_over else None
        }

    def _should_show_hint(self) -> bool:
        """Determina se deve mostrar uma dica."""
        return (
            GameConfig.SHOW_HINT_AFTER > 0
            and not self.hint_shown
            and self.incorrect_attempts >= GameConfig.SHOW_HINT_AFTER
        )

    def _get_hint(self) -> str:
        """Retorna uma dica sobre a palavra."""
        self.hint_shown = True
        return get_hint(self.word, self.correct_letters)

    def calculate_score(self) -> int:
        """Calcula a pontuação atual baseada no desempenho."""
        if not self.word:
            return 0

        base_score = 100
        letter_bonus = len(self.correct_letters) * 10
        attempt_penalty = self.incorrect_attempts * 15
        time_penalty = 0  # Poderia ser implementado com self.start_time

        score = base_score + letter_bonus - attempt_penalty - time_penalty
        return max(score, 0)

    def guess_letter(self, letter: str) -> None:
        """
        Processa uma tentativa de letra do jogador.

        Args:
            letter: letra a ser tentada

        Raises:
            GameOverError: Se o jogo já terminou
            InvalidLetterError: Se a letra for inválida
            RepeatedLetterError: Se a letra já foi tentada
        """
        if self.game_over:
            raise GameOverError("O jogo já terminou. Inicie um novo jogo.")

        letter = letter.lower()
        validate_letter(letter, self.attempted_letters)
        self.attempted_letters.add(letter)

        if letter in self.word:
            self.correct_letters.add(letter)
            if all(char in self.correct_letters for char in self.word):
                self._end_game(winner=True)
        else:
            self.incorrect_attempts += 1
            if self.incorrect_attempts >= GameConfig.MAX_ATTEMPTS:
                self._end_game(winner=False)

    def _end_game(self, winner: bool) -> None:
        """Finaliza o jogo e registra a pontuação se aplicável."""
        self.game_over = True
        self.winner = winner

        if self.player_name and self.winner:
            try:
                GameSaveManager.update_score(
                    self.player_name,
                    self.calculate_score(),
                    self.word
                )
            except Exception as e:
                print(f"Warning: Não foi possível salvar a pontuação. {str(e)}")

    def save_game(self, filename: Optional[str] = None) -> str:
        """
        Salva o estado atual do jogo.

        Args:
            filename: Nome personalizado do arquivo (opcional)

        Returns:
            Caminho do arquivo salvo
        """
        game_data = {
            'word': self.word,
            'attempted_letters': list(self.attempted_letters),
            'correct_letters': list(self.correct_letters),
            'incorrect_attempts': self.incorrect_attempts,
            'player_name': self.player_name,
            'timestamp': self.start_time
        }
        return GameSaveManager.save_game(game_data, filename)

    @classmethod
    def load_game(cls, filename: str) -> 'HangmanGame':
        """
        Carrega um jogo salvo.

        Args:
            filename: Nome do arquivo a ser carregado

        Returns:
            Instância do HangmanGame carregada
        """
        game_data = GameSaveManager.load_game(filename)
        game = cls(
            word=game_data['word'],
            word_list=None  # Não precisamos da lista para carregar
        )
        game.attempted_letters = set(game_data['attempted_letters'])
        game.correct_letters = set(game_data['correct_letters'])
        game.incorrect_attempts = game_data['incorrect_attempts']
        game.player_name = game_data.get('player_name')
        game.start_time = game_data.get('timestamp')
        return game

    def start_new_game(self) -> None:
        """Reinicia o jogo com uma nova palavra."""
        self.word = self._select_random_word()
        self.attempted_letters = set()
        self.correct_letters = set()
        self.incorrect_attempts = 0
        self.game_over = False
        self.winner = False
        self.hint_shown = False
        self.start_time = None
