import pandas as pd
import numpy as np
from functools import wraps
from datetime import datetime

def tratar_erros(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except pd.errors.EmptyDataError:
            raise ValueError("O arquivo está vazio ou mal formatado")
        except KeyError as e:
            raise ValueError(f"Coluna não encontrada: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro durante operação: {str(e)}")
    return wrapper

class AnalisadorCSV:
    @tratar_erros
    def carregar_csv(self, caminho):
        """Carrega um arquivo CSV com tratamento de erros"""
        return pd.read_csv(caminho)
    
    @tratar_erros
    def carregar_excel(self, caminho):
        """Carrega um arquivo Excel"""
        return pd.read_excel(caminho)
    
    def carregar_exemplo(self):
        """Carrega um dataset de exemplo"""
        return pd.DataFrame({
            'data': pd.date_range(start='2023-01-01', periods=100),
            'valor': np.random.normal(100, 15, 100),
            'categoria': np.random.choice(['A', 'B', 'C'], 100),
            'ativo': np.random.choice([True, False], 100)
        })
    
    @tratar_erros
    def estatisticas_descritivas(self, df):
        """Retorna estatísticas descritivas com tratamento para tipos não numéricos"""
        try:
            # Tenta primeiro com o parâmetro datetime_is_numeric (para pandas >= 1.1.0)
            return df.describe(include='all', datetime_is_numeric=True)
        except TypeError:
            try:
                # Fallback para versões mais recentes sem datetime_is_numeric
                return df.describe(include='all')
            except:
                # Fallback final para versões muito antigas
                return df.describe()

    @tratar_erros
    def informacoes_dataset(self, df):
        """Mostra informações sobre o dataset"""
        info = {
            'Colunas': len(df.columns),
            'Linhas': len(df),
            'Tipos de Dados': df.dtypes.value_counts().to_dict(),
            'Memória Usada': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }
        
        for k, v in info.items():
            print(f"{k}: {v}")

    @tratar_erros
    def contar_ausentes(self, df):
        """Conta valores ausentes por coluna"""
        return df.isnull().sum()

    @tratar_erros
    def calcular_correlacoes(self, df):
        """Calcula correlações entre colunas numéricas"""
        numericas = df.select_dtypes(include=[np.number])
        if numericas.empty:
            raise ValueError("Nenhuma coluna numérica para calcular correlações")
        return numericas.corr()

    @tratar_erros
    def analisar_coluna(self, df, coluna):
        """Analisa uma coluna específica"""
        if coluna not in df.columns:
            raise KeyError(f"Coluna '{coluna}' não encontrada")
        
        serie = df[coluna]
        analise = {
            'Tipo': str(serie.dtype),
            'Únicos': serie.nunique(),
            'Ausentes': serie.isnull().sum(),
            'Porcentagem Ausentes': f"{serie.isnull().mean() * 100:.2f}%"
        }
        
        if pd.api.types.is_numeric_dtype(serie):
            analise.update({
                'Média': serie.mean(),
                'Mediana': serie.median(),
                'Desvio Padrão': serie.std(),
                'Mínimo': serie.min(),
                'Máximo': serie.max()
            })
        elif pd.api.types.is_datetime64_any_dtype(serie):
            analise.update({
                'Data Mínima': serie.min(),
                'Data Máxima': serie.max()
            })
        elif pd.api.types.is_categorical_dtype(serie) or serie.dtype == object:
            analise['Valores Mais Frequentes'] = serie.value_counts().head(5).to_dict()
        
        return pd.Series(analise)

    @tratar_erros
    def filtrar_dados(self, df, condicao):
        """Filtra dados com uma condição"""
        return df.query(condicao, engine='python')

    @tratar_erros
    def parse_selecao_colunas(self, df, selecao):
        """Interpreta a seleção de colunas do usuário"""
        colunas = []
        
        # Por nomes separados por vírgula
        if all(item.strip() in df.columns for item in selecao.split(',')):
            return [col.strip() for col in selecao.split(',')]
        
        # Por índices ou intervalos (ex: 1,3-5)
        for item in selecao.split(','):
            item = item.strip()
            if '-' in item:
                inicio, fim = map(int, item.split('-'))
                colunas.extend(df.columns[inicio-1:fim])
            else:
                colunas.append(df.columns[int(item)-1])
        
        return list(set(colunas))  # Remove duplicatas

    @tratar_erros
    def ordenar_dados(self, df, coluna, ascendente=True):
        """Ordena os dados por uma coluna"""
        return df.sort_values(coluna, ascending=ascendente)

    @tratar_erros
    def agrupar_dados(self, df, coluna, operacao='media'):
        """Agrupa dados por uma coluna"""
        operacoes = {
            'soma': 'sum',
            'media': 'mean',
            'contagem': 'count',
            'max': 'max',
            'min': 'min'
        }
        return df.groupby(coluna).agg(operacoes[operacao])

    @tratar_erros
    def tratar_ausentes(self, df, estrategia='remover', valor=None):
        """Trata valores ausentes"""
        if estrategia == 'remover':
            return df.dropna()
        elif estrategia == 'preencher':
            if valor in ['media', 'mediana', 'moda']:
                return df.fillna(df.select_dtypes(include=[np.number]).agg(valor))
            return df.fillna(valor)
        return df

    @tratar_erros
    def aplicar_funcao(self, df, coluna, funcao):
        """Aplica uma função a uma coluna"""
        # Cria um ambiente seguro para eval
        safe_dict = {
            'np': np,
            'pd': pd,
            'df': df,
            'x': df[coluna]
        }
        
        # Remove funções perigosas
        for builtin in ['open', 'exec', 'eval', '__import__']:
            if builtin in safe_dict:
                del safe_dict[builtin]
        
        try:
            df[coluna] = eval(funcao, {'__builtins__': None}, safe_dict)
            return df
        except Exception as e:
            raise ValueError(f"Erro ao aplicar função: {str(e)}")

    @tratar_erros
    def salvar_dados(self, df, caminho, formato='csv'):
        """Salva dados em diferentes formatos"""
        if formato == 'csv':
            df.to_csv(caminho, index=False)
        elif formato == 'excel':
            df.to_excel(caminho, index=False)
        elif formato == 'json':
            df.to_json(caminho, orient='records', indent=2)