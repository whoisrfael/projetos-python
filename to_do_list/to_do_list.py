import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class EnhancedTodoList:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Premium")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # Configurações
        self.data_file = "todo_data.json"
        self.backup_file = "todo_backup.json"
        self.max_backups = 3
        
        # Estilos
        self.setup_styles()
        
        # Carregar tarefas com tratamento de erro
        self.tasks = self.safe_load_tasks()
        
        # Interface
        self.setup_ui()
        self.update_task_list()
        
        # Bindings
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_styles(self):
        """Configura os estilos da interface"""
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5, font=('Arial', 10))
        self.style.configure('Completed.TLabel', foreground='#888888')
        self.style.configure('Pending.TLabel', foreground='#333333')
        self.style.configure('HighPriority.TLabel', foreground='#d62728')
        self.style.configure('MediumPriority.TLabel', foreground='#ff7f0e')
        self.style.configure('LowPriority.TLabel', foreground='#2ca02c')
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de entrada
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.task_var = tk.StringVar()
        ttk.Label(input_frame, text="Nova Tarefa:").pack(side=tk.LEFT)
        self.task_entry = ttk.Entry(input_frame, textvariable=self.task_var, width=30)
        self.task_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        # Frame de prioridade
        priority_frame = ttk.Frame(main_frame)
        priority_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(priority_frame, text="Prioridade:").pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(value="Média")
        priorities = ["Alta", "Média", "Baixa"]
        for prio in priorities:
            ttk.Radiobutton(
                priority_frame, 
                text=prio, 
                variable=self.priority_var, 
                value=prio
            ).pack(side=tk.LEFT, padx=5)
        
        # Frame de data
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="Prazo:").pack(side=tk.LEFT)
        self.due_date_var = tk.StringVar()
        self.due_date_entry = ttk.Entry(date_frame, textvariable=self.due_date_var, width=12)
        self.due_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="(DD/MM/AAAA)").pack(side=tk.LEFT)
        
        # Botão de adicionar
        ttk.Button(
            main_frame, 
            text="Adicionar Tarefa", 
            command=self.add_task
        ).pack(pady=5)
        
        # Frame da lista de tarefas
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para lista de tarefas
        self.task_tree = ttk.Treeview(
            list_frame, 
            columns=('completed', 'priority', 'due_date'), 
            show='headings',
            selectmode='browse'
        )
        
        # Configurar colunas
        self.task_tree.heading('#0', text='Tarefa')
        self.task_tree.column('#0', width=250, anchor=tk.W)
        
        self.task_tree.heading('completed', text='Status')
        self.task_tree.column('completed', width=80, anchor=tk.CENTER)
        
        self.task_tree.heading('priority', text='Prioridade')
        self.task_tree.column('priority', width=80, anchor=tk.CENTER)
        
        self.task_tree.heading('due_date', text='Prazo')
        self.task_tree.column('due_date', width=80, anchor=tk.CENTER)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("Concluir", self.complete_task, '#a6dba0'),
            ("Editar", self.edit_task, '#92c5de'),
            ("Excluir", self.delete_task, '#f4a582'),
            ("Limpar Tudo", self.clear_all_tasks, '#f7f7f7')
        ]
        
        for text, command, color in buttons:
            ttk.Button(
                action_frame, 
                text=text, 
                command=command,
                style='TButton'
            ).pack(side=tk.LEFT, padx=5, expand=True)
    
    def safe_load_tasks(self):
        """Carrega tarefas com tratamento robusto de erros"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return []
            return []
        except (json.JSONDecodeError, IOError) as e:
            # Tenta carregar do backup em caso de erro
            try:
                if os.path.exists(self.backup_file):
                    with open(self.backup_file, 'r') as f:
                        data = json.load(f)
                        messagebox.showwarning(
                            "Aviso", 
                            "Erro ao carregar arquivo principal. Usando backup."
                        )
                        return data if isinstance(data, list) else []
            except:
                pass
            return []
    
    def safe_save_tasks(self):
        """Salva tarefas com backup e tratamento de erros"""
        try:
            # Primeiro salva em um arquivo temporário
            temp_file = self.data_file + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.tasks, f, indent=4)
            
            # Cria backup antes de substituir
            if os.path.exists(self.data_file):
                self.rotate_backups()
                os.replace(self.data_file, self.backup_file)
            
            # Substitui o arquivo principal
            os.replace(temp_file, self.data_file)
            
        except Exception as e:
            messagebox.showerror(
                "Erro", 
                f"Não foi possível salvar as tarefas: {str(e)}"
            )
    
    def rotate_backups(self):
        """Rotaciona backups para manter apenas os últimos X"""
        if not os.path.exists(self.backup_file):
            return
            
        for i in range(self.max_backups-1, 0, -1):
            src = f"{self.backup_file}.{i}"
            dst = f"{self.backup_file}.{i+1}"
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
        
        if os.path.exists(self.backup_file):
            os.rename(self.backup_file, f"{self.backup_file}.1")
    
    def validate_date(self, date_str):
        """Valida o formato da data"""
        try:
            if not date_str.strip():
                return True
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def add_task(self):
        """Adiciona uma nova tarefa com validação"""
        task_text = self.task_var.get().strip()
        priority = self.priority_var.get()
        due_date = self.due_date_var.get().strip()
        
        if not task_text:
            messagebox.showwarning("Aviso", "Por favor, digite uma descrição para a tarefa.")
            self.task_entry.focus()
            return
        
        if due_date and not self.validate_date(due_date):
            messagebox.showwarning("Aviso", "Formato de data inválido. Use DD/MM/AAAA.")
            self.due_date_entry.focus()
            return
        
        new_task = {
            "text": task_text,
            "completed": False,
            "priority": priority,
            "due_date": due_date,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.tasks.append(new_task)
        self.safe_save_tasks()
        self.update_task_list()
        
        # Limpa os campos de entrada
        self.task_var.set("")
        self.due_date_var.set("")
        self.task_entry.focus()
    
    def update_task_list(self):
        """Atualiza a exibição da lista de tarefas"""
        self.task_tree.delete(*self.task_tree.get_children())
        
        # Ordena tarefas: não completas primeiro, depois por prioridade e data
        sorted_tasks = sorted(self.tasks, key=lambda x: (
            x['completed'], 
            {'Alta': 0, 'Média': 1, 'Baixa': 2}[x['priority']],
            x['due_date'] if x['due_date'] else '9999-99-99'
        ))
        
        for task in sorted_tasks:
            status = "Concluída" if task['completed'] else "Pendente"
            priority = task['priority']
            due_date = task['due_date'] if task['due_date'] else "-"
            
            item = self.task_tree.insert(
                '', 
                tk.END, 
                text=task['text'],
                values=(status, priority, due_date)
            )
            
            # Aplica estilos com base no status e prioridade
            tags = []
            if task['completed']:
                tags.append('completed')
            else:
                tags.append(f'{priority.lower().replace("é", "e")}_priority')
            
            self.task_tree.item(item, tags=tags)
    
    def get_selected_task(self):
        """Retorna a tarefa selecionada ou None"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione uma tarefa.")
            return None
        
        item = self.task_tree.item(selection[0])
        task_text = item['text']
        
        # Encontra a tarefa correspondente na lista
        for task in self.tasks:
            if task['text'] == task_text:
                return task, self.tasks.index(task)
        
        return None
    
    def complete_task(self):
        """Marca a tarefa como concluída"""
        result = self.get_selected_task()
        if result:
            task, index = result
            if task['completed']:
                messagebox.showinfo("Info", "Esta tarefa já está concluída.")
                return
            
            task['completed'] = True
            task['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.safe_save_tasks()
            self.update_task_list()
    
    def edit_task(self):
        """Edita a tarefa selecionada"""
        result = self.get_selected_task()
        if not result:
            return
            
        task, index = result
        
        # Janela de edição
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Editar Tarefa")
        edit_win.transient(self.root)
        edit_win.grab_set()
        
        ttk.Label(edit_win, text="Descrição:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        desc_entry = ttk.Entry(edit_win, width=30)
        desc_entry.grid(row=0, column=1, padx=5, pady=5)
        desc_entry.insert(0, task['text'])
        
        ttk.Label(edit_win, text="Prioridade:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        priority_var = tk.StringVar(value=task['priority'])
        priorities = ["Alta", "Média", "Baixa"]
        for i, prio in enumerate(priorities):
            ttk.Radiobutton(
                edit_win, 
                text=prio, 
                variable=priority_var, 
                value=prio
            ).grid(row=1, column=1+i, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(edit_win, text="Prazo (DD/MM/AAAA):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        due_date_entry = ttk.Entry(edit_win, width=12)
        due_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        due_date_entry.insert(0, task['due_date'] if task['due_date'] else "")
        
        def save_changes():
            new_text = desc_entry.get().strip()
            new_priority = priority_var.get()
            new_due_date = due_date_entry.get().strip()
            
            if not new_text:
                messagebox.showwarning("Aviso", "A descrição não pode estar vazia.")
                return
                
            if new_due_date and not self.validate_date(new_due_date):
                messagebox.showwarning("Aviso", "Formato de data inválido. Use DD/MM/AAAA.")
                return
            
            # Atualiza a tarefa
            task['text'] = new_text
            task['priority'] = new_priority
            task['due_date'] = new_due_date if new_due_date else ""
            task['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.safe_save_tasks()
            self.update_task_list()
            edit_win.destroy()
        
        ttk.Button(edit_win, text="Salvar", command=save_changes).grid(row=3, column=0, columnspan=4, pady=10)
        
        desc_entry.focus()
    
    def delete_task(self):
        """Exclui a tarefa selecionada após confirmação"""
        result = self.get_selected_task()
        if not result:
            return
            
        task, index = result
        
        if messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir a tarefa:\n\n\"{task['text']}\"?"
        ):
            del self.tasks[index]
            self.safe_save_tasks()
            self.update_task_list()
    
    def clear_all_tasks(self):
        """Remove todas as tarefas após confirmação"""
        if not self.tasks:
            messagebox.showinfo("Info", "Não há tarefas para limpar.")
            return
            
        if messagebox.askyesno(
            "Confirmar Limpeza", 
            "Tem certeza que deseja remover TODAS as tarefas?\nEsta ação não pode ser desfeita."
        ):
            self.tasks = []
            self.safe_save_tasks()
            self.update_task_list()
    
    def on_close(self):
        """Executa ao fechar a janela"""
        self.safe_save_tasks()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedTodoList(root)
    
    # Configurar tags para estilização
    app.task_tree.tag_configure('completed', foreground='#888888')
    app.task_tree.tag_configure('alta_priority', foreground='#d62728')
    app.task_tree.tag_configure('media_priority', foreground='#ff7f0e')
    app.task_tree.tag_configure('baixa_priority', foreground='#2ca02c')
    
    root.mainloop()