import os
import json
import pandas as pd
from tkinter import Tk, filedialog
from datetime import datetime

# Função para escolher a pasta
def escolher_pasta():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do Tkinter
    pasta = filedialog.askdirectory(title="Escolha a pasta com os arquivos JSON")
    return pasta

# Função para buscar recursivamente o campo "matchId" no JSON
def buscar_matchid(dados):
    match_ids = []

    if isinstance(dados, dict):  # Se os dados são um dicionário
        for chave, valor in dados.items():
            if chave == 'matchId':  # Se encontrou a chave "matchId"
                match_ids.append(valor)
            elif isinstance(valor, (dict, list)):  # Se o valor é outro dict ou uma lista, busca recursivamente
                match_ids.extend(buscar_matchid(valor))

    elif isinstance(dados, list):  # Se os dados são uma lista
        for item in dados:
            match_ids.extend(buscar_matchid(item))

    return match_ids

# Função para ler os JSONs e pegar os valores de "matchId"
def processar_jsons(pasta):
    match_ids = []  # Lista para armazenar todos os matchIds

    for arquivo in os.listdir(pasta):
        if arquivo.endswith('.json'):
            caminho_arquivo = os.path.join(pasta, arquivo)
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                match_ids.extend(buscar_matchid(dados)[:10])  # Pegando as 10 primeiras ocorrências de "matchId"

    return match_ids

# Função principal
def main():
    pasta = escolher_pasta()
    if not pasta:
        print("Nenhuma pasta foi selecionada.")
        return

    match_ids = processar_jsons(pasta)

    if match_ids:
        # Pegando a data e hora atuais
        data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Definindo o nome do arquivo com a data e hora
        nome_arquivo = f'matchIds_{data_hora}.xlsx'
        
        # Salvando os matchIds em um arquivo Excel
        df = pd.DataFrame(match_ids, columns=['matchId'])
        df.to_excel(nome_arquivo, index=False)
        print(f"Arquivo Excel '{nome_arquivo}' gerado com sucesso!")
    else:
        print("Nenhum valor 'matchId' encontrado nos arquivos JSON.")

if __name__ == '__main__':
    main()
