"""
Configuração do jogo com suporte a dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Caminhos dos arquivos
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
ASSETS_DIR = BASE_DIR / 'assets'

# Carrega Variaveis de ambiente

load_dotenv(BASE_DIR / '.env')

class GameConfig:
    """Configurações personalizaveis do jogo."""

    # Dificuldade: Facil (8), médio (6), dificil (4)
    MAX_ATTEMPTS = int(os.getenv('MAX_ATTEMPTS', 6))

    # Cores no terminal (True/False)
    USE_COLORS = os.getenv('USE_COLORS', 'true').lower() == 'true'

    # Mostrar dica após N erros (0 para desativar)
    SHOW_HINT_AFTER = int(os.getenv('SHOW_HINT_AFTER'))

    # Idioma (pt/en)
    LANGUAGE = os.getenv('LANGUAGE', 'pt').lower()

    @classmethod
    def get_words_file(cls):
        """ Retorna o caminho do arquivo de palaras."""
        return DATA_DIR / 'words.txt'
    
    @classmethod
    def get_scores_file(cls):
        """Retorna o caminho do arquivo de pontuações."""
        return DATA_DIR / 'scores.json'

