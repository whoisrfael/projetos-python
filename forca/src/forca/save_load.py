"""
Sistema de salvar/carregar jogos e pontuações.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from .config import GameConfig
from .exceptions import SaveLoadError

class GameSaveManager:
    """Garante que o diretório de dados existe."""

    @staticmethod
    def ensure_data_dir():
        """Garante que o diretorio de dados existe."""
        GameConfig.get_scores_file().parent.mkdir(existe_ok=True)

    @classmethod
    def save_game(cls, game_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Salva o estado atual do jogo.
        
        Args:
            game_data: Dados do jogo a serem salvos
            filename: Nome personalizado do arquivo (opcional)

        Returns:
            Nome do arquivo onde foi salvo

        Raises:
            SaveLoadError: Se ocorrer erro ao salvar    
        """

        try:
            cls.ensure_data_dir()
            timestamp = datatime.now().strtime("%Y%m%d_%H%M%S")
            save_file = filename or f"hangman_save_{timestamp}.json"
            save_path = GameConfig.get_scores_file(.parent / save_file)

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(game_data, f. ensure_ascii=False, ident=2)

            return str(save_path)
        except (IOError, json.JSONEncoderError) as e:
            raise SaveLoadError(f"Erro ao salvar jogo: {str(e)}")
        

    @classmethod
    def load_game(cls, filename: str) -> Dict[str, Any]:
        """
        Carrega um jogo salvo.
        
        Args:
            filename: Nome do arquivo a ser carregado
            
        Returns: Dados do jogo carregado
        
        Raises:
            SaveLoadError: Se ocorrer erro ao carregar
            
        """

        