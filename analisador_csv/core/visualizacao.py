import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from functools import wraps

def configurar_plot(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            plt.figure(figsize=kwargs.pop('figsize', (10, 6)))
            result = f(*args, **kwargs)
            plt.title(kwargs.get('titulo', ''))
            plt.grid(kwargs.get('grid', True))
            plt.tight_layout()
            if kwargs.get('mostrar', True):
                plt.show()
            return result
        except Exception as e:
            plt.close()
            raise ValueError(f"Erro ao gerar visualização: {str(e)}")
    return wrapper

class VisualizadorDados:
    def __init__(self):
        self.tema = 'claro'
        self.set_tema(self.tema)
    
    def set_tema(self, tema):
        """Define o tema visual"""
        estilo_claro = None
        # Tentar encontrar um estilo claro disponível
        for estilo in ['seaborn-v0_8', 'seaborn', 'ggplot', 'bmh', 'classic']:
            if estilo in plt.style.available:
                estilo_claro = estilo
                break
        
        if estilo_claro is None:
            estilo_claro = 'default'
        
        temas = {
            'claro': estilo_claro,
            'escuro': 'dark_background',
            'azul': estilo_claro  # ou um estilo azulado específico
        }
        
        self.tema = tema
        try:
            plt.style.use(temas[tema])
        except:
            plt.style.use('default')
        
        # Configurar paleta de cores
        paletas = {
            'claro': 'viridis',
            'escuro': 'mako',
            'azul': 'Blues_r'
        }
        sns.set_palette(paletas.get(tema, 'viridis'))
    
    @configurar_plot
    def plot_linhas(self, df, coluna_y, coluna_x=None, **kwargs):
        """Gráfico de linhas"""
        if coluna_x:
            df.plot(x=coluna_x, y=coluna_y, kind='line', ax=plt.gca())
            plt.xlabel(coluna_x)
        else:
            df[coluna_y].plot(kind='line', ax=plt.gca())
        plt.ylabel(coluna_y)
        plt.title(kwargs.get('titulo', f'Gráfico de Linhas - {coluna_y}'))
    
    @configurar_plot
    def plot_histograma(self, df, coluna, bins=10, **kwargs):
        """Histograma"""
        df[coluna].hist(bins=bins, edgecolor='black')
        plt.xlabel(coluna)
        plt.ylabel('Frequência')
        plt.title(kwargs.get('titulo', f'Distribuição de {coluna}'))
    
    @configurar_plot
    def plot_dispersao(self, df, coluna_x, coluna_y, **kwargs):
        """Gráfico de dispersão"""
        sns.scatterplot(data=df, x=coluna_x, y=coluna_y)
        plt.xlabel(coluna_x)
        plt.ylabel(coluna_y)
        plt.title(kwargs.get('titulo', f'Dispersão: {coluna_x} vs {coluna_y}'))
    
    @configurar_plot
    def plot_boxplot(self, df, coluna, **kwargs):
        """Boxplot"""
        sns.boxplot(y=df[coluna])
        plt.ylabel(coluna)
        plt.title(kwargs.get('titulo', f'Boxplot de {coluna}'))
    
    @configurar_plot
    def plot_barras(self, df, coluna_y, coluna_x=None, **kwargs):
        """Gráfico de barras"""
        if coluna_x:
            df.plot(x=coluna_x, y=coluna_y, kind='bar', ax=plt.gca())
            plt.xlabel(coluna_x)
        else:
            df[coluna_y].value_counts().plot(kind='bar', ax=plt.gca())
        plt.ylabel(coluna_y)
        plt.title(kwargs.get('titulo', f'Gráfico de Barras - {coluna_y}'))
    
    @configurar_plot
    def plot_correlacao(self, df, **kwargs):
        """Mapa de calor de correlações"""
        corr = df.select_dtypes(include=[np.number]).corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', 
                   center=0, linewidths=.5, ax=plt.gca())
        plt.title(kwargs.get('titulo', 'Matriz de Correlação'))
    
    @configurar_plot
    def plot_ausentes(self, df, **kwargs):
        """Visualização de valores ausentes"""
        sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
        plt.title(kwargs.get('titulo', 'Valores Ausentes'))
    
    @configurar_plot
    def plot_distribuicao(self, df, coluna, **kwargs):
        """Distribuição com KDE"""
        sns.histplot(df[coluna], kde=True, bins=20)
        plt.xlabel(coluna)
        plt.title(kwargs.get('titulo', f'Distribuição de {coluna}'))
    
    def plot_personalizado(self, df):
        """Interface para criação de gráficos personalizados"""
        print("\nTipos de gráfico disponíveis:")
        tipos = ['linha', 'barra', 'histograma', 'dispersao', 'boxplot', 'area', 'pie']
        for i, tipo in enumerate(tipos, 1):
            print(f"{i}. {tipo.capitalize()}")
        
        tipo_idx = int(input("\nSelecione o tipo de gráfico: ")) - 1
        tipo_grafico = tipos[tipo_idx]
        
        colunas = df.select_dtypes(include=[np.number, 'datetime']).columns.tolist()
        print("\nColunas numéricas/datas disponíveis:")
        for i, col in enumerate(colunas, 1):
            print(f"{i}. {col}")
        
        coluna_y_idx = int(input("\nSelecione a coluna para eixo Y: ")) - 1
        coluna_y = colunas[coluna_y_idx]
        
        coluna_x = None
        if tipo_grafico in ['linha', 'barra', 'dispersao', 'area']:
            coluna_x_idx = input("Selecione a coluna para eixo X (opcional, deixe vazio para índice): ")
            if coluna_x_idx:
                coluna_x = colunas[int(coluna_x_idx)-1]
        
        titulo = input("Título do gráfico (opcional): ")
        
        # Configurações específicas
        kwargs = {'titulo': titulo or f"{tipo_grafico.capitalize()} de {coluna_y}"}
        
        if tipo_grafico == 'linha':
            self.plot_linhas(df, coluna_y, coluna_x, **kwargs)
        elif tipo_grafico == 'barra':
            self.plot_barras(df, coluna_y, coluna_x, **kwargs)
        elif tipo_grafico == 'histograma':
            bins = input("Número de bins (padrão 20): ")
            kwargs['bins'] = int(bins) if bins else 20
            self.plot_distribuicao(df, coluna_y, **kwargs)
        elif tipo_grafico == 'dispersao':
            if not coluna_x:
                print("Gráfico de dispersão requer coluna para eixo X!")
                return
            self.plot_dispersao(df, coluna_x, coluna_y, **kwargs)
        elif tipo_grafico == 'boxplot':
            self.plot_boxplot(df, coluna_y, **kwargs)
        elif tipo_grafico == 'area':
            self.plot_area(df, coluna_y, coluna_x, **kwargs)
        elif tipo_grafico == 'pie':
            self.plot_pizza(df, coluna_y, **kwargs)
    
    @configurar_plot
    def plot_area(self, df, coluna_y, coluna_x=None, **kwargs):
        """Gráfico de área"""
        if coluna_x:
            df.plot(x=coluna_x, y=coluna_y, kind='area', ax=plt.gca(), stacked=False)
            plt.xlabel(coluna_x)
        else:
            df[coluna_y].plot(kind='area', ax=plt.gca(), stacked=False)
        plt.ylabel(coluna_y)
    
    @configurar_plot
    def plot_pizza(self, df, coluna, **kwargs):
        """Gráfico de pizza"""
        counts = df[coluna].value_counts()
        counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=plt.gca())
        plt.ylabel('')
        plt.title(kwargs.get('titulo', f'Proporção de {coluna}'))