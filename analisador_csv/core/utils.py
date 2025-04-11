import os
import json
from pathlib import Path
import pandas as pd

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def validar_entrada(mensagem, tipo=str, intervalo=None, opcoes=None, padrao=None):
    while True:
        try:
            entrada = input(mensagem).strip()
            if not entrada and padrao is not None:
                return padrao
            
            if tipo == int:
                entrada = int(entrada)
                if intervalo and (entrada < intervalo[0] or entrada > intervalo[1]):
                    raise ValueError(f"Valor fora do intervalo {intervalo}")
            elif tipo == float:
                entrada = float(entrada)
            
            if opcoes and entrada not in opcoes:
                raise ValueError(f"Opção inválida. Deve ser uma de: {', '.join(opcoes)}")
            
            return entrada
        
        except ValueError as e:
            print(f"Entrada inválida: {str(e)}. Tente novamente.")

def carregar_configuracao():
    config_path = Path('config/settings.json')
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar configurações: {str(e)}")
    
    # Configurações padrão
    return {
        'tema': 'claro',
        'salvar_historico': True,
        'diretorio_dados': 'data'
    }

def salvar_configuracao(config):
    config_path = Path('config/settings.json')
    try:
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Erro ao salvar configurações: {str(e)}")

def criar_diretorios():
    Path('data').mkdir(exist_ok=True)
    Path('config').mkdir(exist_ok=True)