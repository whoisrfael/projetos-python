import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from functools import wraps

def tratar_erros_api(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Erro na requisição HTTP: {str(e)}")
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Erro ao processar dados da API: {str(e)}")
    return wrapper

class APIClient:
    @tratar_erros_api
    def obter_dados_covid(self, pais=None, dias=30):
        """Obtém dados de COVID-19 de Our World in Data"""
        url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
        response = requests.get(url)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        df['date'] = pd.to_datetime(df['date'])
        
        # Filtrar por país se especificado
        if pais:
            df = df[df['location'].str.lower() == pais.lower()]
            if df.empty:
                raise ValueError(f"País '{pais}' não encontrado")
        
        # Filtrar por período
        data_corte = datetime.now() - timedelta(days=dias)
        df = df[df['date'] >= data_corte]
        
        return df
    
    @tratar_erros_api
    def obter_dados_financeiros(self, simbolo, dias=30):
        """Obtém dados financeiros do Yahoo Finance"""
        periodo1 = int((datetime.now() - timedelta(days=dias)).timestamp())
        periodo2 = int(datetime.now().timestamp())
        
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{simbolo}?period1={periodo1}&period2={periodo2}&interval=1d&events=history"
        
        response = requests.get(url)
        if response.status_code == 404:
            raise ValueError(f"Símbolo '{simbolo}' não encontrado")
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    
    @tratar_erros_api
    def obter_dados_climaticos(self, coordenadas, dias=7):
        """Obtém dados climáticos históricos do Open-Meteo"""
        try:
            lat, lon = map(float, coordenadas.split(','))
        except:
            raise ValueError("Coordenadas devem estar no formato 'lat,lon'")
        
        data_fim = datetime.now().strftime('%Y-%m-%d')
        data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
        
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={data_inicio}&end_date={data_fim}&hourly=temperature_2m,precipitation,weathercode,windspeed_10m"
        
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()
        
        # Converter para DataFrame
        df = pd.DataFrame({
            'datahora': pd.to_datetime(dados['hourly']['time']),
            'temperatura': dados['hourly']['temperature_2m'],
            'precipitacao': dados['hourly']['precipitation'],
            'codigo_tempo': dados['hourly']['weathercode'],
            'velocidade_vento': dados['hourly']['windspeed_10m']
        })
        
        return df