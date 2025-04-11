import os
import json
import pandas as pd
from pathlib import Path
from core.analisador import AnalisadorCSV
from core.visualizacao import VisualizadorDados
from core.api_client import APIClient
from core.utils import validar_entrada, limpar_tela, carregar_configuracao, salvar_configuracao

class AnalisadorCSVApp:
    def __init__(self):
        self.analisador = AnalisadorCSV()
        self.visualizador = VisualizadorDados()
        self.api_client = APIClient()
        self.config = carregar_configuracao()
        self.df = None
        self.historico = []

    def menu_principal(self):
        while True:
            limpar_tela()
            print("=== ANALISADOR CSV AVANÇADO ===")
            print("\nMenu Principal:")
            print("1. Carregar dados")
            print("2. Analisar dados atuais")
            print("3. Visualizar dados")
            print("4. Manipular dados")
            print("5. Configurações")
            print("6. Sair")

            opcao = validar_entrada("Escolha uma opção: ", tipo=int, intervalo=(1, 6))

            if opcao == 1:
                self.menu_carregar_dados()
            elif opcao == 2:
                self.menu_analisar_dados()
            elif opcao == 3:
                self.menu_visualizacao()
            elif opcao == 4:
                self.menu_manipulacao()
            elif opcao == 5:
                self.menu_configuracao()
            elif opcao == 6:
                self.salvar_historico()
                print("Saindo... Obrigado por usar o Analisador CSV!")
                break

    def menu_carregar_dados(self):
        limpar_tela()
        print("=== CARREGAR DADOS ===")
        print("\nOpções:")
        print("1. Arquivo local")
        print("2. API pública")
        print("3. Exemplo integrado")
        print("4. Voltar")

        opcao = validar_entrada("Escolha: ", tipo=int, intervalo=(1, 4))

        try:
            if opcao == 1:
                caminho = input("Caminho do arquivo (CSV/Excel): ").strip()
                if not caminho:
                    print("Caminho inválido!")
                    return
                
                if caminho.endswith('.csv'):
                    self.df = self.analisador.carregar_csv(caminho)
                elif caminho.endswith(('.xls', '.xlsx')):
                    self.df = self.analisador.carregar_excel(caminho)
                else:
                    print("Formato não suportado!")
                    return
                
                self.registrar_historico(f"Carregado arquivo: {caminho}")
                print(f"\nDados carregados! Shape: {self.df.shape}")

            elif opcao == 2:
                self.menu_apis_publicas()
                
            elif opcao == 3:
                self.df = self.analisador.carregar_exemplo()
                self.registrar_historico("Carregado dataset de exemplo")
                print("\nDataset de exemplo carregado!")

        except Exception as e:
            print(f"\nErro ao carregar dados: {str(e)}")
        finally:
            input("\nPressione Enter para continuar...")

    def menu_apis_publicas(self):
        limpar_tela()
        print("=== APIS PÚBLICAS ===")
        print("\n1. COVID-19 (Our World in Data)")
        print("2. Dados Financeiros (Yahoo Finance)")
        print("3. Dados Climáticos (Open-Meteo)")
        print("4. Voltar")

        opcao = validar_entrada("Escolha: ", tipo=int, intervalo=(1, 4))

        try:
            if opcao == 1:
                pais = input("País (opcional, deixe vazio para todos): ")
                dias = validar_entrada("Número de dias (padrão 30): ", tipo=int, padrao=30)
                self.df = self.api_client.obter_dados_covid(pais, dias)
                self.registrar_historico(f"Dados COVID-19 - País: {pais or 'Todos'}, Dias: {dias}")

            elif opcao == 2:
                simbolo = input("Símbolo da ação (ex: AAPL): ").upper()
                dias = validar_entrada("Número de dias (padrão 30): ", tipo=int, padrao=30)
                self.df = self.api_client.obter_dados_financeiros(simbolo, dias)
                self.registrar_historico(f"Dados Financeiros - Ação: {simbolo}, Dias: {dias}")

            elif opcao == 3:
                local = input("Local (ex: -23.5505,-46.6333): ")
                dias = validar_entrada("Número de dias (padrão 7): ", tipo=int, padrao=7)
                self.df = self.api_client.obter_dados_climaticos(local, dias)
                self.registrar_historico(f"Dados Climáticos - Local: {local}, Dias: {dias}")

            if opcao in (1, 2, 3) and self.df is not None:
                print(f"\nDados obtidos! Shape: {self.df.shape}")

        except Exception as e:
            print(f"\nErro ao obter dados da API: {str(e)}")
        finally:
            input("\nPressione Enter para continuar...")

    def menu_analisar_dados(self):
        if not self.verificar_dados_carregados():
            return

        while True:
            limpar_tela()
            print("=== ANÁLISE DE DADOS ===")
            print(f"\nDataset atual: {len(self.df)} linhas × {len(self.df.columns)} colunas")
            
            print("\nOpções:")
            print("1. Estatísticas descritivas")
            print("2. Informações do dataset")
            print("3. Valores ausentes")
            print("4. Correlações")
            print("5. Análise de coluna específica")
            print("6. Voltar")

            opcao = validar_entrada("Escolha: ", tipo=int, intervalo=(1, 6))

            try:
                if opcao == 1:
                    print("\nEstatísticas Descritivas:")
                    print(self.analisador.estatisticas_descritivas(self.df))
                    
                elif opcao == 2:
                    print("\nInformações do Dataset:")
                    self.analisador.informacoes_dataset(self.df)
                    
                elif opcao == 3:
                    print("\nValores Ausentes:")
                    ausentes = self.analisador.contar_ausentes(self.df)
                    print(ausentes)
                    
                    if ausentes.sum() > 0:
                        if input("\nDeseja visualizar distribuição de ausentes? (s/n): ").lower() == 's':
                            self.visualizador.plot_ausentes(self.df)
                
                elif opcao == 4:
                    print("\nMatriz de Correlação:")
                    correlacoes = self.analisador.calcular_correlacoes(self.df)
                    print(correlacoes)
                    
                    if input("\nPlotar mapa de calor? (s/n): ").lower() == 's':
                        self.visualizador.plot_correlacao(self.df)
                
                elif opcao == 5:
                    coluna = self.selecionar_coluna("Selecione uma coluna para análise: ")
                    if coluna:
                        print(f"\nAnálise para coluna '{coluna}':")
                        print(self.analisador.analisar_coluna(self.df, coluna))
                        
                        if pd.api.types.is_numeric_dtype(self.df[coluna]):
                            if input("\nPlotar distribuição? (s/n): ").lower() == 's':
                                self.visualizador.plot_distribuicao(self.df, coluna)
                
                elif opcao == 6:
                    break

            except Exception as e:
                print(f"\nErro durante análise: {str(e)}")
            finally:
                input("\nPressione Enter para continuar...")

    def menu_visualizacao(self):
        if not self.verificar_dados_carregados():
            return

        while True:
            limpar_tela()
            print("=== VISUALIZAÇÃO DE DADOS ===")
            
            print("\nOpções:")
            print("1. Gráfico de linhas")
            print("2. Histograma")
            print("3. Dispersão")
            print("4. Boxplot")
            print("5. Gráfico de barras")
            print("6. Visualização personalizada")
            print("7. Voltar")

            opcao = validar_entrada("Escolha: ", tipo=int, intervalo=(1, 7))

            try:
                if opcao == 1:
                    coluna = self.selecionar_coluna("Selecione a coluna para eixo Y: ")
                    if coluna:
                        coluna_x = self.selecionar_coluna("Coluna para eixo X (opcional): ", obrigatorio=False)
                        self.visualizador.plot_linhas(self.df, coluna_y=coluna, coluna_x=coluna_x)
                
                elif opcao == 2:
                    coluna = self.selecionar_coluna("Selecione a coluna numérica: ")
                    if coluna:
                        bins = validar_entrada("Número de bins (padrão 10): ", tipo=int, padrao=10)
                        self.visualizador.plot_histograma(self.df, coluna, bins=bins)
                
                elif opcao == 3:
                    coluna_x = self.selecionar_coluna("Selecione a coluna para eixo X: ")
                    coluna_y = self.selecionar_coluna("Selecione a coluna para eixo Y: ")
                    if coluna_x and coluna_y:
                        self.visualizador.plot_dispersao(self.df, coluna_x, coluna_y)
                
                elif opcao == 4:
                    coluna = self.selecionar_coluna("Selecione a coluna numérica: ")
                    if coluna:
                        self.visualizador.plot_boxplot(self.df, coluna)
                
                elif opcao == 5:
                    coluna = self.selecionar_coluna("Selecione a coluna para eixo Y: ")
                    if coluna:
                        coluna_x = self.selecionar_coluna("Coluna para eixo X (opcional): ", obrigatorio=False)
                        self.visualizador.plot_barras(self.df, coluna_y=coluna, coluna_x=coluna_x)
                
                elif opcao == 6:
                    self.visualizador.plot_personalizado(self.df)
                
                elif opcao == 7:
                    break

            except Exception as e:
                print(f"\nErro durante visualização: {str(e)}")
            finally:
                input("\nPressione Enter para continuar...")

    def menu_manipulacao(self):
        if not self.verificar_dados_carregados():
            return

        while True:
            limpar_tela()
            print("=== MANIPULAÇÃO DE DADOS ===")
            
            print("\nOpções:")
            print("1. Filtrar linhas")
            print("2. Selecionar colunas")
            print("3. Ordenar dados")
            print("4. Agrupar dados")
            print("5. Tratar valores ausentes")
            print("6. Aplicar função")
            print("7. Salvar dataset")
            print("8. Voltar")

            opcao = validar_entrada("Escolha: ", tipo=int, intervalo=(1, 8))

            try:
                if opcao == 1:
                    condicao = input("Digite a condição (ex: 'idade > 30'): ")
                    if condicao:
                        df_filtrado = self.analisador.filtrar_dados(self.df, condicao)
                        print(f"\nDataset filtrado! Novo shape: {df_filtrado.shape}")
                        if input("Substituir dataset atual? (s/n): ").lower() == 's':
                            self.df = df_filtrado
                            self.registrar_historico(f"Filtrado dados com condição: {condicao}")
                
                elif opcao == 2:
                    print("\nColunas disponíveis:")
                    for i, col in enumerate(self.df.columns, 1):
                        print(f"{i}. {col}")
                    
                    selecao = input("\nSelecione colunas (ex: 1,3-5 ou nomes separados por vírgula): ")
                    if selecao:
                        colunas = self.analisador.parse_selecao_colunas(self.df, selecao)
                        if colunas:
                            df_selecionado = self.df[colunas]
                            print(f"\nColunas selecionadas! Novo shape: {df_selecionado.shape}")
                            if input("Substituir dataset atual? (s/n): ").lower() == 's':
                                self.df = df_selecionado
                                self.registrar_historico(f"Selecionadas colunas: {', '.join(colunas)}")
                
                elif opcao == 3:
                    coluna = self.selecionar_coluna("Coluna para ordenar: ")
                    if coluna:
                        ascendente = input("Ordem crescente? (s/n): ").lower() != 'n'
                        self.df = self.analisador.ordenar_dados(self.df, coluna, ascendente)
                        self.registrar_historico(f"Dados ordenados por: {coluna} ({'asc' if ascendente else 'desc'})")
                        print("\nDados ordenados!")
                
                elif opcao == 4:
                    coluna = self.selecionar_coluna("Coluna para agrupar: ")
                    if coluna:
                        operacao = validar_entrada(
                            "Operação (soma, media, contagem, max, min): ", 
                            opcoes=['soma', 'media', 'contagem', 'max', 'min']
                        )
                        df_agrupado = self.analisador.agrupar_dados(self.df, coluna, operacao)
                        print(f"\nDados agrupados! Novo shape: {df_agrupado.shape}")
                        print(df_agrupado.head())
                        if input("Substituir dataset atual? (s/n): ").lower() == 's':
                            self.df = df_agrupado
                            self.registrar_historico(f"Dados agrupados por {coluna} com {operacao}")
                
                elif opcao == 5:
                    print("\nValores ausentes por coluna:")
                    print(self.analisador.contar_ausentes(self.df))
                    
                    estrategia = validar_entrada(
                        "Estratégia (remover, preencher, ignorar): ",
                        opcoes=['remover', 'preencher', 'ignorar']
                    )
                    
                    if estrategia == 'preencher':
                        valor = input("Valor para preencher (ou 'media', 'mediana', 'moda'): ")
                        try:
                            valor = float(valor)
                        except ValueError:
                            if valor not in ['media', 'mediana', 'moda']:
                                valor = 0
                    else:
                        valor = None
                    
                    df_tratado = self.analisador.tratar_ausentes(self.df, estrategia, valor)
                    print(f"\nDados tratados! Novo shape: {df_tratado.shape}")
                    if input("Substituir dataset atual? (s/n): ").lower() == 's':
                        self.df = df_tratado
                        self.registrar_historico(f"Tratados ausentes com: {estrategia} ({valor if valor else ''})")
                
                elif opcao == 6:
                    coluna = self.selecionar_coluna("Aplicar função na coluna: ")
                    if coluna:
                        funcao = input("Função a aplicar (ex: 'x*2', 'np.log(x)'): ")
                        if funcao:
                            self.df = self.analisador.aplicar_funcao(self.df, coluna, funcao)
                            self.registrar_historico(f"Aplicada função: {funcao} na coluna {coluna}")
                            print("\nFunção aplicada!")
                
                elif opcao == 7:
                    formato = validar_entrada(
                        "Formato (csv, excel, json): ",
                        opcoes=['csv', 'excel', 'json']
                    )
                    nome_arquivo = input(f"Nome do arquivo (sem extensão): ")
                    if nome_arquivo:
                        caminho = os.path.join('data', f"{nome_arquivo}.{formato}")
                        self.analisador.salvar_dados(self.df, caminho, formato)
                        self.registrar_historico(f"Dataset salvo como: {caminho}")
                        print(f"\nDataset salvo em: {caminho}")
                
                elif opcao == 8:
                    break

            except Exception as e:
                print(f"\nErro durante manipulação: {str(e)}")
            finally:
                input("\nPressione Enter para continuar...")

    def menu_configuracao(self):
        while True:
            limpar_tela()
            print("=== CONFIGURAÇÕES ===")
            
            print("\nOpções atuais:")
            print(f"1. Tema visual: {self.config.get('tema', 'claro')}")
            print(f"2. Salvar histórico: {'Sim' if self.config.get('salvar_historico', True) else 'Não'}")
            print(f"3. Diretório de dados: {self.config.get('diretorio_dados', 'data')}")
            print("4. Voltar")

            opcao = validar_entrada("Escolha: ", tipo=int, intervalo=(1, 4))

            try:
                if opcao == 1:
                    tema = validar_entrada(
                        "Tema (claro, escuro, azul): ",
                        opcoes=['claro', 'escuro', 'azul']
                    )
                    self.config['tema'] = tema
                    self.visualizador.set_tema(tema)
                    print("\nTema atualizado!")
                
                elif opcao == 2:
                    salvar = input("Salvar histórico? (s/n): ").lower() == 's'
                    self.config['salvar_historico'] = salvar
                    print("\nConfiguração atualizada!")
                
                elif opcao == 3:
                    diretorio = input("Novo diretório para dados: ").strip()
                    if diretorio:
                        os.makedirs(diretorio, exist_ok=True)
                        self.config['diretorio_dados'] = diretorio
                        print("\nDiretório atualizado!")
                
                elif opcao == 4:
                    salvar_configuracao(self.config)
                    break

            except Exception as e:
                print(f"\nErro ao atualizar configurações: {str(e)}")
            finally:
                input("\nPressione Enter para continuar...")

    def selecionar_coluna(self, mensagem, obrigatorio=True):
        print("\nColunas disponíveis:")
        for i, col in enumerate(self.df.columns, 1):
            print(f"{i}. {col} ({self.df[col].dtype})")
        
        while True:
            selecao = input(f"\n{mensagem}").strip()
            if not selecao and not obrigatorio:
                return None
            
            try:
                # Tentar por índice
                idx = int(selecao) - 1
                if 0 <= idx < len(self.df.columns):
                    return self.df.columns[idx]
            except ValueError:
                # Tentar por nome
                if selecao in self.df.columns:
                    return selecao
            
            print("Seleção inválida! Tente novamente.")

    def verificar_dados_carregados(self):
        if self.df is None or self.df.empty:
            print("\nNenhum dataset carregado! Por favor, carregue dados primeiro.")
            input("Pressione Enter para continuar...")
            return False
        return True

    def registrar_historico(self, acao):
        self.historico.append({
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'acao': acao,
            'shape': self.df.shape if self.df is not None else None
        })

    def salvar_historico(self):
        if self.config.get('salvar_historico', True) and self.historico:
            caminho = os.path.join(self.config.get('diretorio_dados', 'data'), 'historico.json')
            try:
                with open(caminho, 'w') as f:
                    json.dump(self.historico, f, indent=2)
            except Exception as e:
                print(f"Erro ao salvar histórico: {str(e)}")

if __name__ == "__main__":
    app = AnalisadorCSVApp()
    app.menu_principal()