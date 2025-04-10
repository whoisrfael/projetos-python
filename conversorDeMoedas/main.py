import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
import os

class ConversorMoedasAprimorado:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Moedas Aprimorado")
        self.root.geometry("500x600")
        self.root.minsize(450, 550)
        
        # Configurações
        self.cache_file = "cotacoes_cache.json"
        self.cache_expiry = 3600  # 1 hora em segundos
        self.api_url = "https://open.er-api.com/v6/latest/"
        
        # Variáveis
        self.moedas = self.carregar_moedas()
        self.valor_var = tk.DoubleVar(value=1.0)
        self.de_moeda_var = tk.StringVar(value="USD")
        self.para_moeda_var = tk.StringVar(value="BRL")
        self.resultado_var = tk.StringVar()
        self.taxa_var = tk.StringVar()
        self.ultima_atualizacao_var = tk.StringVar()
        self.historico = []
        
        # Cache
        self.cotacoes_cache = {}
        self.carregar_cache()
        
        # Interface
        self.criar_interface()
        
        # Atualizar dados inicial
        self.atualizar_cotacoes()
    
    def carregar_moedas(self):
        """Carrega a lista de moedas disponíveis"""
        moedas_padrao = ['USD', 'EUR', 'GBP', 'JPY', 'BRL', 'CAD', 'AUD', 'CNY', 'CHF']
        try:
            response = requests.get(f"{self.api_url}USD")
            if response.status_code == 200:
                data = response.json()
                return sorted(list(data['rates'].keys()))
            return moedas_padrao
        except:
            return moedas_padrao
    
    def carregar_cache(self):
        """Carrega o cache de cotações do arquivo"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cotacoes_cache = json.load(f)
            except:
                self.cotacoes_cache = {}
    
    def salvar_cache(self):
        """Salva o cache de cotações no arquivo"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cotacoes_cache, f)
    
    def obter_cotacoes(self, moeda_base):
        """Obtém as cotações da API ou do cache"""
        agora = datetime.now().timestamp()
        
        # Verifica se há cache válido
        if moeda_base in self.cotacoes_cache:
            cache_data = self.cotacoes_cache[moeda_base]
            if agora - cache_data['timestamp'] < self.cache_expiry:
                return cache_data['rates']
        
        # Se não, faz requisição à API
        try:
            response = requests.get(f"{self.api_url}{moeda_base}")
            if response.status_code == 200:
                data = response.json()
                if data['result'] == 'success':
                    self.cotacoes_cache[moeda_base] = {
                        'rates': data['rates'],
                        'timestamp': agora,
                        'data_consulta': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }
                    self.salvar_cache()
                    return data['rates']
            return None
        except requests.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar à API: {e}")
            return None
    
    def atualizar_cotacoes(self):
        """Atualiza as cotações e a interface"""
        moeda_base = self.de_moeda_var.get()
        cotacoes = self.obter_cotacoes(moeda_base)
        
        if cotacoes:
            self.ultima_atualizacao_var.set(
                f"Última atualização: {self.cotacoes_cache[moeda_base]['data_consulta']}"
            )
            self.converter_moeda()
        else:
            messagebox.showwarning("Aviso", "Não foi possível obter as cotações atuais")
    
    def converter_moeda(self):
        """Realiza a conversão de moedas"""
        try:
            valor = self.valor_var.get()
            de_moeda = self.de_moeda_var.get()
            para_moeda = self.para_moeda_var.get()
            
            if not valor or valor <= 0:
                messagebox.showwarning("Aviso", "Digite um valor válido para conversão!")
                return
            
            cotacoes = self.obter_cotacoes(de_moeda)
            if not cotacoes or para_moeda not in cotacoes:
                messagebox.showerror("Erro", "Moeda de destino não disponível")
                return
            
            taxa = cotacoes[para_moeda]
            resultado = valor * taxa
            
            self.resultado_var.set(f"{valor:.2f} {de_moeda} = {resultado:.2f} {para_moeda}")
            self.taxa_var.set(f"Taxa: 1 {de_moeda} = {taxa:.6f} {para_moeda}")
            
            # Adiciona ao histórico
            conversao = {
                'data': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'de': f"{valor:.2f} {de_moeda}",
                'para': f"{resultado:.2f} {para_moeda}",
                'taxa': f"1 {de_moeda} = {taxa:.6f} {para_moeda}"
            }
            self.historico.insert(0, conversao)
            self.atualizar_historico()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na conversão: {str(e)}")
    
    def inverter_moedas(self):
        """Inverte as moedas selecionadas"""
        de_moeda = self.de_moeda_var.get()
        para_moeda = self.para_moeda_var.get()
        self.de_moeda_var.set(para_moeda)
        self.para_moeda_var.set(de_moeda)
        self.atualizar_cotacoes()
    
    def atualizar_historico(self):
        """Atualiza a exibição do histórico"""
        self.historico_text.config(state=tk.NORMAL)
        self.historico_text.delete(1.0, tk.END)
        
        for idx, item in enumerate(self.historico[:10]):  # Mostra apenas os 10 últimos
            self.historico_text.insert(tk.END, 
                f"{item['data']}\n"
                f"{item['de']} → {item['para']}\n"
                f"Taxa: {item['taxa']}\n"
                f"{'-'*40}\n"
            )
        
        self.historico_text.config(state=tk.DISABLED)
    
    def criar_interface(self):
        """Cria a interface gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de conversão
        conv_frame = ttk.LabelFrame(main_frame, text="Conversão", padding=10)
        conv_frame.pack(fill=tk.X, pady=5)
        
        # Entrada de valor
        ttk.Label(conv_frame, text="Valor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        valor_entry = ttk.Entry(conv_frame, textvariable=self.valor_var, width=15, font=('Arial', 10))
        valor_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Moeda de origem
        ttk.Label(conv_frame, text="De:").grid(row=1, column=0, sticky=tk.W, pady=5)
        de_moeda_cb = ttk.Combobox(conv_frame, textvariable=self.de_moeda_var, 
                                  values=self.moedas, width=10, font=('Arial', 10))
        de_moeda_cb.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Moeda de destino
        ttk.Label(conv_frame, text="Para:").grid(row=2, column=0, sticky=tk.W, pady=5)
        para_moeda_cb = ttk.Combobox(conv_frame, textvariable=self.para_moeda_var, 
                                    values=self.moedas, width=10, font=('Arial', 10))
        para_moeda_cb.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Botão inverter
        inverter_btn = ttk.Button(conv_frame, text="↔ Inverter", command=self.inverter_moedas, width=10)
        inverter_btn.grid(row=1, column=2, rowspan=2, padx=10, pady=5, sticky=tk.NS)
        
        # Botão converter
        converter_btn = ttk.Button(conv_frame, text="Converter", command=self.converter_moeda)
        converter_btn.grid(row=3, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        # Resultado
        ttk.Label(conv_frame, textvariable=self.resultado_var, 
                 font=('Arial', 11, 'bold'), foreground='blue').grid(
                 row=4, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        ttk.Label(conv_frame, textvariable=self.taxa_var, 
                 font=('Arial', 9)).grid(
                 row=5, column=0, columnspan=3, pady=2, sticky=tk.W)
        
        ttk.Label(conv_frame, textvariable=self.ultima_atualizacao_var, 
                 font=('Arial', 8)).grid(
                 row=6, column=0, columnspan=3, pady=2, sticky=tk.W)
        
        # Botão atualizar
        atualizar_btn = ttk.Button(conv_frame, text="Atualizar Cotações", 
                                  command=self.atualizar_cotacoes)
        atualizar_btn.grid(row=7, column=0, columnspan=3, pady=5, sticky=tk.EW)
        
        # Frame de histórico
        hist_frame = ttk.LabelFrame(main_frame, text="Histórico (últimas 10 conversões)", padding=10)
        hist_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.historico_text = scrolledtext.ScrolledText(
            hist_frame, width=40, height=8, wrap=tk.WORD, 
            font=('Consolas', 9), state=tk.DISABLED)
        self.historico_text.pack(fill=tk.BOTH, expand=True)
        
        # Créditos
        ttk.Label(main_frame, text="Dados fornecidos por ExchangeRate-API", 
                 font=('Arial', 8)).pack(side=tk.BOTTOM, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorMoedasAprimorado(root)
    root.mainloop()
    