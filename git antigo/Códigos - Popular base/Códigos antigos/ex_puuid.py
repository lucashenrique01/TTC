import pandas as pd
import requests
from tkinter import Tk, filedialog
import json
from datetime import datetime

# Função para escolher o arquivo XLSX
def escolher_arquivo_xlsx():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do Tkinter
    arquivo = filedialog.askopenfilename(title="Escolha o arquivo XLSX", filetypes=[("Arquivos XLSX", "*.xlsx")])
    return arquivo

# Função para chamar a API e obter dados
def obter_puuids(matchid, api_key):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={api_key}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        return buscar_puuid(dados)
    else:
        print(f"Erro ao obter dados para matchId {matchid}: {resposta.status_code}")
        return []

# Função para buscar recursivamente o campo "puuid" no JSON
def buscar_puuid(dados):
    puuids = []

    if isinstance(dados, dict):  # Se os dados são um dicionário
        for chave, valor in dados.items():
            if chave == 'puuid':  # Se encontrou a chave "puuid"
                puuids.append(valor)
            elif isinstance(valor, (dict, list)):  # Se o valor é outro dict ou uma lista, busca recursivamente
                puuids.extend(buscar_puuid(valor))

    elif isinstance(dados, list):  # Se os dados são uma lista
        for item in dados:
            puuids.extend(buscar_puuid(item))

    return puuids

# Função para salvar os PUUIDs em um arquivo Excel
def salvar_puuids_em_excel(puuids):
    data_hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"puuids_{data_hora_atual}.xlsx"
    df = pd.DataFrame(puuids, columns=["PUUID"])
    df.to_excel(nome_arquivo, index=False)
    print(f"Arquivo salvo como: {nome_arquivo}")

# Função principal
def main():
    arquivo_xlsx = escolher_arquivo_xlsx()
    if not arquivo_xlsx:
        print("Nenhum arquivo foi selecionado.")
        return

    api_key = 'RGAPI-8e90acce-4dd4-4207-8a06-c137b5489dfc'
    df = pd.read_excel(arquivo_xlsx)
    puuids = []

    for index, row in df.iterrows():
        matchid = row['matchId']  # Ajuste o nome da coluna conforme necessário
        puuids.extend(obter_puuids(matchid, api_key))

    # Salvando os resultados em um arquivo Excel
    salvar_puuids_em_excel(puuids)

if __name__ == "__main__":
    main()
