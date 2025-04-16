"""
Ponto de entrada principal para o jogo da forca.
"""

import sys
import time
from pathlib import Path
from .game import HangmanGame
from .exceptions import InvalidLetterError, RepeatedLetterError, SaveLoadError
from .themes import HangmanTheme
from .save_load import GameSaveManager
from .config import GameConfig

def clear_screen():
    """Limpa a tela do terminal."""
    print("\033c", end='')

def display_intro():
    """Exibe a introdução do jogo."""
    title = HangmanTheme.title("JOGO DA FORCA")
    print(f"\n{'*' * 30}")
    print(f"*{title.center(28)}*")
    print(f"{'*' * 30}\n")

def display_game_state(game_state):
    """Exibe o estado atual do jogo."""
    print(game_state['hangman_state'])
    print(f"\nPalavra: {game_state['displayed_word']}")

    if game_state['hint']:
        print(f"\nDica: {HangmanTheme.info(game_state['hint'])}")

    print(f"\nLetras tentadas: {', '.join(game_state['attempted_letters'])}")
    attempts = game_state['remaining_attempts']
    attempts_text = f"Tentativas restantes: {attempts}"
    if attempts <= 2:
        print(HangmanTheme.error(attempts_text))
    else:
        print(attempts_text)

    if 'score' in game_state and game_state['score'] > 0:
        print(f"Pontuação: {HangmanTheme.highlight(game_state['score'])}")

def get_player_name():
    """Obtém o nome do jogador."""
    name = input("\nDigite seu nome (ou deixe em branco para anônimo): ").strip()
    return name if name else "Anônimo"

def get_player_guess():
    """Obtém a tentativa do jogador."""
    while True:
        guess = input("\nDigite uma letra, 'salvar', 'sair' ou 'dica': ").strip().lower()

        if guess in ('sair', 'exit', 'quit'):
            return None
        if guess in ('salvar', 'save'):
            return 'save'
        if guess in ('dica', 'hint'):
            return 'hint'
        if guess and guess.isalpha():
            return guess[0]
        
        print(HangmanTheme.error("Entrada inválida. Por favor, digite uma letra ou comando."))

def show_saves_menu():
    """Exibe menu de jogos salvos e permite carregar um."""
    try:
        saves = GameSaveManager.list_saves()
        if not saves:
            print(HangmanTheme.info("\nNenhum jogo salvo encontrado."))
            return None
            
        print(HangmanTheme.info("\nJogos salvos disponíveis:"))
        for i, save in enumerate(saves, 1):
            print(f"{i}. {save}")
            
        print(f"{len(saves)+1}. Voltar")
        
        choice = input("\nEscolha um jogo para carregar (ou número para voltar): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(saves):
            return saves[int(choice)-1]
        return None
    except SaveLoadError as e:
        print(HangmanTheme.error(f"\nErro ao carregar jogos salvos: {str(e)}"))
        return None

def play_game():
    """Função principal que controla o fluxo do jogo."""
    clear_screen()
    display_intro()
    
    # Menu inicial
    print("1. Novo jogo")
    print("2. Carregar jogo")
    print("3. Sair")
    
    choice = input("\nEscolha uma opção: ").strip()
    if choice == '3':
        return
    elif choice == '2':
        save_file = show_saves_menu()
        if save_file:
            try:
                game = HangmanGame.load_game(save_file)
                print(HangmanTheme.success("\nJogo carregado com sucesso!"))
                time.sleep(1)
            except SaveLoadError as e:
                print(HangmanTheme.error(f"\nErro ao carregar: {str(e)}"))
                time.sleep(2)
                return play_game()
        else:
            return play_game()
    else:
        game = HangmanGame()
        game.player_name = get_player_name()
        game.start_time = time.time()
    
    # Loop principal do jogo
    while True:
        clear_screen()
        display_intro()
        
        game_state = game.get_current_state()
        display_game_state(game_state)
        
        if game.game_over:
            if game.winner:
                print(HangmanTheme.success("\nParabéns! Você ganhou!"))
            else:
                print(HangmanTheme.error(f"\nGame Over! A palavra era: {game.word.upper()}"))
            
            print("\nDeseja jogar novamente? (s/n)")
            choice = input().strip().lower()
            if choice == 's':
                game.start_new_game()
                game.player_name = get_player_name()
                game.start_time = time.time()
                continue
            break
        
        guess = get_player_guess()
        if guess is None:
            print("\nObrigado por jogar! Até a próxima!")
            break
        elif guess == 'save':
            try:
                save_path = game.save_game()
                print(HangmanTheme.success(f"\nJogo salvo em: {save_path}"))
                time.sleep(2)
            except SaveLoadError as e:
                print(HangmanTheme.error(f"\nErro ao salvar: {str(e)}"))
                time.sleep(2)
            continue
        elif guess == 'hint':
            if game_state['hint']:
                print(HangmanTheme.info(f"\nDica: {game_state['hint']}"))
                input("Pressione Enter para continuar...")
            else:
                print(HangmanTheme.warning("\nNenhuma dica disponível ainda. Continue tentando!"))
                time.sleep(1)
            continue
        
        try:
            game.guess_letter(guess)
        except (InvalidLetterError, RepeatedLetterError) as e:
            print(HangmanTheme.error(f"\nErro: {str(e)}"))
            input("Pressione Enter para continuar...")

if __name__ == '__main__':
    try:
        play_game()
    except KeyboardInterrupt:
        print("\nJogo interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(HangmanTheme.error(f"\nOcorreu um erro inesperado: {str(e)}"))
        sys.exit(1)