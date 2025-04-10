import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    filename='password_generator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PasswordGenerator:
    """Classe principal do gerador de senhas seguras."""
    
    def __init__(self, root):
        """Inicializa a aplicação."""
        self.root = root
        self.setup_ui()
        self.setup_variables()
        self.create_widgets()
        self.setup_bindings()
        
        # Registrar início da aplicação
        logging.info("Aplicação iniciada")
    
    def setup_ui(self):
        """Configura a interface principal."""
        self.root.title("Gerador de Senhas Seguras Pro")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Definir estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TCheckbutton', background='#f0f0f0')
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        
        # Ícone (opcional)
        try:
            self.root.iconbitmap('icon.ico')  # Adicione um arquivo icon.ico se quiser
        except:
            pass
    
    def setup_variables(self):
        """Configura as variáveis de controle."""
        self.password_length = tk.IntVar(value=16)
        self.include_uppercase = tk.BooleanVar(value=True)
        self.include_lowercase = tk.BooleanVar(value=True)
        self.include_digits = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=True)
        self.exclude_similar = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.generated_password = tk.StringVar()
        self.password_strength = tk.StringVar(value="Força: -")
    
    def create_widgets(self):
        """Cria todos os widgets da interface."""
        try:
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title_label = ttk.Label(
                main_frame, 
                text="Gerador de Senhas Seguras", 
                style='Title.TLabel'
            )
            title_label.pack(pady=(0, 15))
            
            # Frame de configurações
            settings_frame = ttk.LabelFrame(
                main_frame, 
                text="Configurações", 
                padding=(12, 8)
            )
            settings_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Comprimento da senha
            length_frame = ttk.Frame(settings_frame)
            length_frame.pack(fill=tk.X, pady=5)
            ttk.Label(length_frame, text="Comprimento:").pack(side=tk.LEFT)
            
            self.length_slider = ttk.Scale(
                length_frame, 
                from_=8, to=64, 
                orient=tk.HORIZONTAL,
                variable=self.password_length,
                command=lambda e: self.update_length_display()
            )
            self.length_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            
            self.length_display = ttk.Label(length_frame, text="16")
            self.length_display.pack(side=tk.RIGHT, padx=5)
            
            # Opções de caracteres
            chars_frame = ttk.Frame(settings_frame)
            chars_frame.pack(fill=tk.X)
            
            ttk.Checkbutton(
                chars_frame, 
                text="Letras maiúsculas (A-Z)", 
                variable=self.include_uppercase,
                command=self.validate_options
            ).pack(anchor=tk.W)
            
            ttk.Checkbutton(
                chars_frame, 
                text="Letras minúsculas (a-z)", 
                variable=self.include_lowercase,
                command=self.validate_options
            ).pack(anchor=tk.W)
            
            ttk.Checkbutton(
                chars_frame, 
                text="Números (0-9)", 
                variable=self.include_digits,
                command=self.validate_options
            ).pack(anchor=tk.W)
            
            ttk.Checkbutton(
                chars_frame, 
                text="Símbolos (!@#$% etc)", 
                variable=self.include_symbols,
                command=self.validate_options
            ).pack(anchor=tk.W)
            
            # Opções avançadas
            advanced_frame = ttk.Frame(settings_frame)
            advanced_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Checkbutton(
                advanced_frame, 
                text="Excluir caracteres similares (1, l, I, etc)", 
                variable=self.exclude_similar,
                command=self.validate_options
            ).pack(anchor=tk.W)
            
            ttk.Checkbutton(
                advanced_frame, 
                text="Excluir caracteres ambíguos ({[]} etc)", 
                variable=self.exclude_ambiguous,
                command=self.validate_options
            ).pack(anchor=tk.W)
            
            # Botão de gerar
            self.generate_button = ttk.Button(
                main_frame, 
                text="Gerar Senha", 
                command=self.generate_password,
                style='Accent.TButton'
            )
            self.generate_button.pack(fill=tk.X, pady=(10, 5))
            
            # Frame de resultado
            result_frame = ttk.Frame(main_frame)
            result_frame.pack(fill=tk.X)
            
            # Exibição da senha
            self.password_entry = ttk.Entry(
                result_frame, 
                textvariable=self.generated_password,
                font=('Courier New', 12),
                state='readonly',
                width=30
            )
            self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Botão de copiar
            ttk.Button(
                result_frame, 
                text="Copiar", 
                command=self.copy_to_clipboard,
                width=8
            ).pack(side=tk.RIGHT, padx=(5, 0))
            
            # Indicador de força
            strength_frame = ttk.Frame(main_frame)
            strength_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(
                strength_frame, 
                textvariable=self.password_strength,
                font=('Arial', 9, 'bold')
            ).pack(side=tk.LEFT)
            
            # Botão de histórico (opcional)
            ttk.Button(
                strength_frame, 
                text="Histórico", 
                command=self.show_history,
                width=8
            ).pack(side=tk.RIGHT)
            
        except Exception as e:
            logging.error(f"Erro ao criar widgets: {str(e)}")
            messagebox.showerror("Erro", "Ocorreu um erro ao criar a interface.")
            self.root.destroy()
    
    def setup_bindings(self):
        """Configura os eventos de teclado."""
        self.root.bind('<Return>', lambda e: self.generate_password())
        self.root.bind('<Control-c>', lambda e: self.copy_to_clipboard())
    
    def update_length_display(self):
        """Atualiza o display do comprimento da senha."""
        self.length_display.config(text=str(self.password_length.get()))
    
    def validate_options(self):
        """Valida se pelo menos uma opção de caractere está selecionada."""
        try:
            if not any([
                self.include_uppercase.get(),
                self.include_lowercase.get(),
                self.include_digits.get(),
                self.include_symbols.get()
            ]):
                self.generate_button.config(state=tk.DISABLED)
            else:
                self.generate_button.config(state=tk.NORMAL)
        except Exception as e:
            logging.warning(f"Erro na validação: {str(e)}")
    
    def get_character_set(self):
        """Retorna o conjunto de caracteres baseado nas seleções."""
        try:
            characters = ""
            
            if self.include_uppercase.get():
                uppercase = string.ascii_uppercase
                if self.exclude_similar.get():
                    uppercase = uppercase.replace('I', '').replace('O', '')
                characters += uppercase
            
            if self.include_lowercase.get():
                lowercase = string.ascii_lowercase
                if self.exclude_similar.get():
                    lowercase = lowercase.replace('l', '').replace('o', '')
                characters += lowercase
            
            if self.include_digits.get():
                digits = string.digits
                if self.exclude_similar.get():
                    digits = digits.replace('1', '').replace('0', '')
                characters += digits
            
            if self.include_symbols.get():
                symbols = string.punctuation
                if self.exclude_ambiguous.get():
                    symbols = symbols.replace('{', '').replace('}', '').replace('[', '').replace(']', '')
                    symbols = symbols.replace('(', '').replace(')', '').replace('<', '').replace('>', '')
                characters += symbols
            
            if not characters:
                raise ValueError("Nenhum conjunto de caracteres selecionado")
                
            return characters
        except Exception as e:
            logging.error(f"Erro ao obter conjunto de caracteres: {str(e)}")
            raise
    
    def calculate_strength(self, password):
        """Calcula a força da senha."""
        try:
            length = len(password)
            strength = 0
            
            # Pontuação por comprimento
            if length >= 32: strength += 4
            elif length >= 24: strength += 3
            elif length >= 16: strength += 2
            elif length >= 12: strength += 1
            
            # Pontuação por diversidade de caracteres
            char_types = 0
            if any(c in string.ascii_lowercase for c in password): char_types += 1
            if any(c in string.ascii_uppercase for c in password): char_types += 1
            if any(c in string.digits for c in password): char_types += 1
            if any(c in string.punctuation for c in password): char_types += 1
            
            strength += char_types
            
            # Classificação
            if strength >= 6: return "Forte"
            elif strength >= 4: return "Média"
            elif strength >= 2: return "Fraca"
            else: return "Muito Fraca"
        except Exception as e:
            logging.warning(f"Erro ao calcular força: {str(e)}")
            return "Desconhecida"
    
    def generate_password(self):
        """Gera uma senha segura baseada nas configurações."""
        try:
            length = self.password_length.get()
            
            # Validar comprimento
            if length < 8 or length > 64:
                raise ValueError("O comprimento deve estar entre 8 e 64 caracteres")
            
            # Obter conjunto de caracteres
            characters = self.get_character_set()
            
            # Garantir que a senha contenha pelo menos um de cada tipo selecionado
            password_parts = []
            
            if self.include_uppercase.get():
                uppercase = string.ascii_uppercase
                if self.exclude_similar.get():
                    uppercase = uppercase.replace('I', '').replace('O', '')
                password_parts.append(random.choice(uppercase))
            
            if self.include_lowercase.get():
                lowercase = string.ascii_lowercase
                if self.exclude_similar.get():
                    lowercase = lowercase.replace('l', '').replace('o', '')
                password_parts.append(random.choice(lowercase))
            
            if self.include_digits.get():
                digits = string.digits
                if self.exclude_similar.get():
                    digits = digits.replace('1', '').replace('0', '')
                password_parts.append(random.choice(digits))
            
            if self.include_symbols.get():
                symbols = string.punctuation
                if self.exclude_ambiguous.get():
                    symbols = symbols.replace('{', '').replace('}', '').replace('[', '').replace(']', '')
                    symbols = symbols.replace('(', '').replace(')', '').replace('<', '').replace('>', '')
                password_parts.append(random.choice(symbols))
            
            # Completar o restante da senha
            remaining_length = length - len(password_parts)
            password_parts.extend(random.choice(characters) for _ in range(remaining_length))
            
            # Embaralhar a senha
            random.shuffle(password_parts)
            password = ''.join(password_parts)
            
            # Atualizar a interface
            self.generated_password.set(password)
            strength = self.calculate_strength(password)
            self.password_strength.set(f"Força: {strength}")
            
            # Registrar no log
            logging.info(f"Senha gerada: {password[:4]}... (força: {strength})")
            
            return password
            
        except ValueError as ve:
            messagebox.showerror("Erro de Validação", str(ve))
            logging.warning(f"Validação falhou: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar a senha: {str(e)}")
            logging.error(f"Erro ao gerar senha: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copia a senha gerada para a área de transferência."""
        try:
            password = self.generated_password.get()
            if not password:
                messagebox.showwarning("Aviso", "Nenhuma senha foi gerada ainda.")
                return
            
            pyperclip.copy(password)
            messagebox.showinfo("Copiado", "Senha copiada para a área de transferência!")
            logging.info("Senha copiada para clipboard")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível copiar a senha: {str(e)}")
            logging.error(f"Erro ao copiar senha: {str(e)}")
    
    def show_history(self):
        """Exibe o histórico de senhas geradas (simulação)."""
        try:
            # Em uma aplicação real, isso viria de um arquivo ou banco de dados
            messagebox.showinfo(
                "Histórico", 
                "Esta funcionalidade seria implementada para armazenar e exibir\n" +
                "o histórico de senhas geradas em um ambiente seguro."
            )
            logging.info("Histórico acessado")
        except Exception as e:
            logging.error(f"Erro ao acessar histórico: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        
        # Tentar carregar um tema (opcional)
        try:
            import sv_ttk
            sv_ttk.set_theme("light")
        except:
            pass
        
        app = PasswordGenerator(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Falha na inicialização: {str(e)}")
        messagebox.showerror("Erro Fatal", "O aplicativo não pôde ser iniciado.")