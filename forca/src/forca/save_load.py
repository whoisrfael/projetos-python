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
                json.dump(game_data, f, ensure_ascii=False, ident=2)

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

        try:
            save_path = GameConfig.get_scores_file().parent / filename
            with open(save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise SaveLoadError(f"Erro ao carregar jogo: {str(e)}")
        
    
    @classmethod
    def update_score(cls, player_name: str, score: int, word: str) -> None:
        """
        Atualiza o placar de pontuações.
        
        Args:
            player_name: Noe do jogador
            score: Pontuação alcançada
            word: Palavras adivinhada ( ou nao)
        """
        
        try:
            cls.ensure_data_dir()
            score_file = GameConfig.get_scores_file()

            # Carrega pontuaçoes existentes ou cria uma nova
            if score_file.exists():
                with open(score_file, 'r', encoding='utf-8') as f:
                    scores = json.load(f)

            else:
                scores = []

            #Adiciona nova pontuação
            scores.append({
                "player": player_name,
                "score": score,
                "word": word,
                "date": datetime.now().isoformat()
            })

            # Mantem apenas as top 10
            scores.sort(key=lambda x: x['score'], reverse=True)
            scores = scores[:10]

            # Salva de volta
            with open(scores_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)

            
        except (IOError, json.JSONDecodeError, json.JSONDecodeError) as e:
            raise SaveLoadError(f"Erro ao atualizar pontuações: {str(e)}")
        


    @classmethod
    def list_saves(cls) -> list:
        """Lista todos os jogos salvos disponiveis."""
        try: 
            cls.ensure_data_dir()
            save_dir = GameConfig.get_scores_file().parent
            return [f.name for f in save_dir.glob("hangman_save_*.json")]
        except IOError as e:
            raise SaveLoadError(f"Erro ao listar jogos salvos: {str(e)}")


    

        