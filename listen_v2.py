import boto3
import time
from datetime import datetime
import pytz
import logging
import json
import requests
import numpy as np
import pickle
from statistics import mode, StatisticsError

BASE_URL = "https://br1.api.riotgames.com"
API_KEY = ''
MODEL_FILE = './modelo_random_forest3.pkl'
MODEL_FILE_RF_V2 = './modelo_random_forest_v2.pkl'
MODEL_FILE_log = './log_reg.pkl'
MODEL_FILE_svm = './svm.pkl'

timezone = pytz.timezone('America/Sao_Paulo')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model():
    try:
        with open(MODEL_FILE, 'rb') as model_file:
            model = pickle.load(model_file)
        logger.info("Modelo 1 carregado com sucesso!")
        with open(MODEL_FILE_RF_V2, 'rb') as model_file:
            model_rf_v2 = pickle.load(model_file)
        logger.info("Modelo 2 carregado com sucesso!")
        with open(MODEL_FILE_log, 'rb') as model_file:
            model_log_reg = pickle.load(model_file)
        logger.info("Modelo 3 carregado com sucesso!")
        with open(MODEL_FILE_svm, 'rb') as model_file:
            model_svm = pickle.load(model_file)
        logger.info("Modelo 4 carregado com sucesso!")
        return model, model_rf_v2, model_log_reg, model_svm
    except Exception as e:
        logger.error(f"Erro ao carregar o modelo: {e}")
        raise

model, model_rf_v2, model_log_reg, model_svm = load_model()


def calculate_mode(stat_list):
    try:
        return mode(stat_list)
    except StatisticsError:
        return sum(stat_list) / len(stat_list) if len(stat_list) > 0 else None

def extract_player_stats(match_history):
    kdas = []
    gold_per_minute = []
    vision_scores = []
    damage_per_minute = []
    
    for match in match_history:
        # print(match['challenges']['kda'])
        kda = match['challenges']['kda']
        kdas.append(kda)

        # Extrair ouro por minuto
        gpm = match['challenges']['goldPerMinute']
        gold_per_minute.append(gpm)

        # Extrair score de visão
        vision_score = match['visionScore']
        vision_scores.append(vision_score)

        #Extrar dano por minuto
        dpm = match['challenges']['damagePerMinute']
        damage_per_minute.append(dpm)

    return kdas, gold_per_minute, vision_scores, damage_per_minute

def get_match_detail(match_id, puuid, region='americas'):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={API_KEY}"
    response = requests.get(url)
    teams = []
    if response.status_code == 200:
        response = response.json()
        teams = response['info']['teams']
        for i, player in enumerate(response['info']['participants']):
            if player['puuid'] == puuid:
                time_pertencente = response['info']['participants'][i]['teamId']
                time_retornado = None
                for time in teams:
                    if time["teamId"] == time_pertencente:
                        time_retornado = time['objectives']
                return response['info']['participants'][i], time_retornado
        return None
    else:
        print(f"Erro ao buscar detalhes da partida {match_id}: {response.status_code}")
        return None
    
    
def get_match_history(puuid, region='americas'):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        match_ids = response.json()  # Retorna IDs das partidas
        match_details = []
        match_team_details = []        
       
        for match_id in match_ids:
            logger.info("pegando detalhe da partida")
            match_detail, teams = get_match_detail(match_id, puuid, region)
            if match_detail:
                match_details.append(match_detail)
                match_team_details.append(teams)
        
        return match_details, match_team_details  # Retorna detalhes completos das partidas
    else:
        logger.info(f"Erro ao buscar histórico de partidas: {response.status_code}")
        return None

def process_json(match_data):
    output_rows = []
    for player_data in match_data:
        match_history = player_data['matchHistory']
        kdas, gpm, vision_scores, dpm = extract_player_stats(match_history)

        # Calcular a moda para cada estatística
        kda_mode = calculate_mode(kdas)
        gpm_mode = calculate_mode(gpm)
        vision_score_mode = calculate_mode(vision_scores)
        dpm_mode = calculate_mode(dpm)

        output_row = [
            kda_mode,
            gpm_mode,
            vision_score_mode,
            dpm_mode
        ]        
        output_rows.append(output_row)
    
    return output_rows

def get_history(puuid):
    team_blue = []
    team_red = []
    objetivos_team_blue = []
    objetivos_team_red = []
    
    # Obter puuids dos jogadores de uma partida ao vivo
    puuids, players, match_id = get_live_match_puuids(puuid)
    logger.info("Vou pegar o histórico")
    
    if puuids:
        for i, puuid in enumerate(puuids): 
            if i == 3 or i == 7:
                logger.info("esperando para não dar time out...")
                time.sleep(120)   
            match_history, match_team_history = get_match_history(puuid)
            
            if match_history:
                player_data = {
                    "teamId": players[i]['teamId'],
                    "matchHistory": match_history
                }
                
                # Separar por time
                if players[i]['teamId'] == 100:
                    print("time 100")
                    team_blue.append(player_data)
                    print(f"Tamhno {len(match_team_history)}")
                    objetivos_team_blue.append(match_team_history)
                else:
                    print("time 200")
                    team_red.append(player_data)
                    objetivos_team_red.append(match_team_history)

        return team_red, team_blue, match_id, objetivos_team_red, objetivos_team_blue

def get_live_match_puuids(summoner_puuid):
    url = f"{BASE_URL}/lol/spectator/v5/active-games/by-summoner/{summoner_puuid}?api_key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        match_data = response.json()
        match_id = match_data['gameId']
        players = match_data['participants']
        puuids = [player['puuid'] for player in players]
        return puuids, players, match_id
    else:
        print(f"Erro ao buscar partida ao vivo: {response.status_code}")
        return None

def somar_metrias(dados):
    kda_total = 0
    ouro_por_minuto_total = 0
    score_visao_total = 0
    
    for jogador in dados:
        kda_total += jogador[0]
        ouro_por_minuto_total += jogador[1]
        score_visao_total += jogador[2]
    
    return [kda_total, ouro_por_minuto_total, score_visao_total]

def send_message_to_sqs(message_body):
    # Cria uma sessão com as credenciais da AWS
    session = boto3.Session()
    
    # Cria um cliente SQS
    sqs = session.client('sqs', region_name='us-east-1')
    
    try:
        # Envia a mensagem
        response = sqs.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/060834380790/atualizar_json",
            MessageBody=str(message_body)
        )
        logger.info(f'Mensagem enviada com sucesso! ID: {response["MessageId"]}')
    except Exception as e:
        logger.error(f'Erro ao enviar mensagem: {e}')
        print(f'Erro ao enviar mensagem: {e}')

def somar_objetivos(lista):
    soma_baron = 0
    soma_dragon= 0
    soma_inhibitor = 0
    soma_tower = 0

    for partida in lista:
        for objetivo in partida:
            soma_baron += objetivo['baron']['kills']
            soma_dragon += objetivo['dragon']['kills']
            soma_inhibitor += objetivo['inhibitor']['kills']
            soma_tower += objetivo['tower']['kills']

    tamanho_lista = len(lista)

    if tamanho_lista > 0:
        media_baron = round(soma_baron / tamanho_lista)
        media_dragon = round(soma_dragon / tamanho_lista)
        media_inhibitor = round(soma_inhibitor / tamanho_lista)
        media_tower = round(soma_tower / tamanho_lista)
    else:
        media_baron = media_dragon = media_inhibitor = media_tower = 0  

    return [media_baron, media_dragon, media_inhibitor, media_tower]


def remove_dpm_from_result(processed_data):
    cleaned_data = [row[:-1] for row in processed_data]
    return cleaned_data

def listen_to_sqs(queue_url):
    # Cria uma sessão com as credenciais da AWS
    session = boto3.Session()
    
    # Cria um cliente SQS
    sqs = session.client('sqs', region_name='us-east-1')

    while True:
        try:
            # Recebe mensagens da fila
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
            )

            messages = response.get('Messages', [])
            s3 = boto3.client('s3')
            bucket_name = 'resultado-partidas'
            file_key = 'previstas.json'

            for message in messages:
                # Processa a mensagem (exemplo: imprime o corpo)
                print(f'Mensagem recebida: {message["Body"]}')
                red, blue, match_id, objetivos_red, objetivos_blue = get_history(message["Body"])
                logger.info("Dados coletados!")
                result_red = process_json(red)
                result_blue = process_json(blue)
                predict = remove_dpm_from_result(result_red)+remove_dpm_from_result(result_blue)
                team_100 = predict[:5]
                team_200 = predict[5:]
                soma_team_100 = somar_metrias(team_100)
                soma_team_200 = somar_metrias(team_200)
                logger.info("Vou somar objetivos!")
                pontos_objetivos_blue = somar_objetivos(objetivos_blue)
                pontos_objetivos_red = somar_objetivos(objetivos_red)
                logger.info("Montando Input v2!")
                predict_rf_v2 = result_red+result_blue
                predict_rf_v2.append(pontos_objetivos_blue)
                predict_rf_v2.append(pontos_objetivos_red)
                logger.info(predict_rf_v2)

                balanceado = all(np.isclose(soma_team_100, soma_team_200, atol=10))
                new_predict = [item for sublist in predict for item in sublist]
                new_predict_rf_v2 = [item for sublist in predict_rf_v2 for item in sublist]
                predictions = model.predict([new_predict])
                predictions_rf_v2 = model_rf_v2.predict([new_predict_rf_v2])
                predict_log = model_log_reg.predict([new_predict_rf_v2])
                predict_svm = model_svm.predict([new_predict_rf_v2])
                logger.info(f"Previsão feita: {predictions}")
                time_now = datetime.now(timezone)
                time_now_str = time_now.isoformat()
                logger.info(f"Data de coleta: {time_now_str}")
                json1 = {
                    "id": 'BR1_'+str(match_id),
		            "data_hora_coleta": time_now_str,
                    "previsao_modelo": int(predictions[0]),
                    "previsao_modelo_rf_v2" : int(predictions_rf_v2[0]),
                    "previsao_modelo_log" : int(predict_log[0]),
                    "previsao_modelo_svm": int(predict_svm[0]),
                    "previsao_real": None,
		            "input_modelo":new_predict,
                    "input_modelos_novos":predict_rf_v2,
                    "pontos_time_100":soma_team_100,
                    "pontos_time_200":soma_team_200,
                    "balanceado:":balanceado
                }

                # Adicionar o novo objeto à lista
                logger.info("Vou buscar o arquivo no S3 para atualizar")
                response = s3.get_object(Bucket=bucket_name, Key=file_key)
                dados = json.load(response['Body'])
                dados.append(json1)
                logger.info("Enviando arquivo atualizado para s3...")
                # Salvar de volta no S3
                response_s3 = s3.put_object(Bucket=bucket_name, Key=file_key, Body=json.dumps(dados, indent=4))
                logger.info(f"response s3: {response_s3}")
                logger.info("Enviado!")
                logger.info("Postei no SQS nova partida")
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                logger.info('Mensagem excluída da fila.')

        except Exception as e:
            logger.info(f'Erro ao receber/processar mensagens: {e}')

        time.sleep(101)



# Exemplo de uso
if __name__ == "__main__":
    queue_url = 'https://sqs.us-east-1.amazonaws.com/060834380790/partidas-para-prever-3'
    listen_to_sqs(queue_url)