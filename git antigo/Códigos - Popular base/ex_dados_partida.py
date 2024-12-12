import requests
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError,ClientError
import time  # Importando o módulo time para utilizar o sleep
import requests
import pandas as pd
import json
from tkinter import Tk, filedialog


def get_s3_client():
    return boto3.client('s3',
        aws_access_key_id='ASIAQ4KQC7P3OYR3UFCU',
        aws_secret_access_key='sLayWrMf4z3E0z8A44izQ1ZfHd3C1rmcfB+z7sy/',
        aws_session_token='IQoJb3JpZ2luX2VjEC4aCXVzLXdlc3QtMiJHMEUCIQDQxupRJyf8CVuqPSjB45xrtTdV8uhD646jB5mj7oH8BQIgCKEXHyW08wz1p+K5mP8woY92BzrKAAdGfnwlF5vX+7IqswIIZxAAGgwwNjA4MzQzODA3OTAiDN1L6t9u8FMNxe9x0iqQArevtj360eIPtIGcYoFPR2sD4FupATcg5aeyD8spn6hxFoZUXv2VmUPUhzuEo0LiAat7SI0sKHLLAUaC+05QCGfGhUHnjN/9ptFjIPiYZL1BQJs6LRwqsXofx24+qvL4JPm1bYBpKU1dmdUyGvZBCkcLCBrZWF4DS4MhQtCoOv3pQypY/5I361lE+/gQSHkNIrvdG0DGTxgsv7aQo4MLOzbVoSC5ext2WN3pQ+6aq3jB5hMvYoenzwf5TU8FAzU1tkgQyQp14Lkl9AeDd2BZrd8jC7/mcpj2Vc7gmh2X/IxejqepiaUfX2dZG6UkMotIAs5Ir7htR7mQivv3ZcKV4bn9xZJAaDRb4wDk+ZScOZmHML+zsrcGOp0BE8Qy6qoh1jY41XV6Nmidn7BJW4Bx682Wr+ifrrA7DxT3y5HCrStRuai5Uc1HUh5wC1joLF69A1Udti11hdtCUJXo64SN/3v1WfYkawOUh090OqYDC16jKBI5w17RZiUmIp0zOdc3+2/0DFFgOLB2YWjoy2xo9izEp9Dy/BbBpByfr1o2nOHQfRIZJPbmv41OKhdZ+nO2xeoRfPuIpQ==',
        region_name='us-east-1')

# Função para escolher o arquivo XLSX
def escolher_arquivo_xlsx():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do Tkinter
    arquivo = filedialog.askopenfilename(title="Escolha o arquivo XLSX", filetypes=[("Arquivos XLSX", "*.xlsx")])
    return arquivo

# Função para fazer chamada à API e obter os 'puuids'
def obter_puuids(api_key, matchid):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        puuids = [participant['puuid'] for participant in data['info']['participants']]
        return puuids
    else:
        print(f"Erro ao acessar API para matchid {matchid}: {response.status_code}")
        return []

# Função para obter partidas usando o 'puuid'
def obter_partidas_por_puuid(api_key, puuid):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=100&api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        partidas = response.json()
        return partidas
    else:
        print(f"Erro ao acessar API para puuid {puuid}: {response.status_code}")
        return []
    
def get_match_info(matchid, api_key):
    if(check_if_object_exists(matchid)):
        return
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        match_info = json.dumps(response.json()).encode('utf-8')
        return match_info
    else:
        400
    
def check_if_object_exists(key):
    s3 = get_s3_client()       
    try:
        # Tenta buscar o objeto no bucket pela key
        s3.head_object(Bucket='match-info', Key=key)
        return True  
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise

def upload_to_s3(bucket_name, key, content):
    try:
        s3_client = get_s3_client()        
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
        
        print(f"Arquivo enviado com sucesso para {bucket_name}/{key}")
        
    except NoCredentialsError:
        print("Erro: Credenciais da AWS não encontradas.")
    except PartialCredentialsError:
        print("Erro: Credenciais da AWS incompletas.")
    except Exception as e:
        print(f"Erro ao enviar arquivo para o S3: {e}")

# Função principal para processar o arquivo XLSX e buscar puuids e partidas
def processar_matchids():
    count = 0
    # Escolhe o arquivo XLSX
    caminho_arquivo = escolher_arquivo_xlsx()
    
    # Lê o arquivo XLSX
    df = pd.read_excel(caminho_arquivo)
    
    # Supondo que a coluna que contém os 'matchIds' seja chamada 'matchId'
    matchids = df['matchId']
    
    # Sua API key da Riot
    api_key = "RGAPI-1ff6e87e-a55f-4720-ae1e-55f9c7c52432"
    
    # Itera sobre cada matchId e faz a chamada à API
    for matchid in matchids:
        puuids = obter_puuids(api_key, matchid)
        if puuids:
            for puuid in puuids:
                # print(f"PUUID para matchid {matchid}: {puuid}")
                
                # Faz a chamada à API para obter as partidas pelo puuid
                partidas = obter_partidas_por_puuid(api_key, puuid)
                
                if partidas:
                    for partida in partidas:
                        match_info = get_match_info(partida, api_key)
                        if match_info != 400:
                            print(f"Partida: {partida} - Puuid: {puuid} ")
                            upload_to_s3('match-info', partida + '.json', match_info)
                            print(count)
                            count += 1
                        else:
                            print(f'Next...')

        
    print(f"Total de partidas enviadas para o S3: {count}")

# Chama a função principal
processar_matchids()
