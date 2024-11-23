import json
import boto3
import logging
import time
import requests
from flask import Flask, jsonify, abort
from flask_cors import CORS
from sklearn.metrics import confusion_matrix

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://br1.api.riotgames.com"

def get_team_100_win(match_id, api_key):
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        json = response.json()['info']
        times = json['teams']
        time_100_win = times[0]['win']
        return 1 if time_100_win else 0
    return None

def get_resultados_partidas(api_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket='resultado-partidas', Key='previstas.json')
    dados = json.load(response['Body'])
    contador = 0
    for  partida in dados:
        if partida['previsao_real'] == None:
            real = get_team_100_win(partida['id'], api_key)
            partida['previsao_real'] = real 
            logger.info(f"Partida {partida['id']} atualizada!")
            contador += 1
            if contador > 98:
                logger.info("vou aguardar...")
                time.sleep(120)
                contador = 0

    s3.put_object(Bucket='resultado-partidas', Key='previstas.json', Body=json.dumps(dados, indent=4))
    logger.info("Atualizei S3")

def calcular_metrica_confusao_por_modelo(dados, nome_modelo):
    previsoes = []
    reais = []
    
    for obj in dados:
        if nome_modelo in obj and "previsao_real" in obj and obj['previsao_real'] is not None:
            previsao = obj[nome_modelo]
            real = obj["previsao_real"]
            previsoes.append(previsao)
            reais.append(real)    

    cm = confusion_matrix(reais, previsoes)
    vn = int(cm[0, 0]) 
    fp = int(cm[0, 1]) 
    fn = int(cm[1, 0]) 
    vp = int(cm[1, 1])

    return {
        f"{nome_modelo}_vn": vn,
        f"{nome_modelo}_fp": fp,
        f"{nome_modelo}_fn": fn,
        f"{nome_modelo}_vp": vp
    }

def gerar_matriz():
    try:
        dados = get_s3()

        resultado = {}
        
        modelos = [
            "previsao_modelo", 
            "privisao_modelo_rf_v2", 
            "previsao_modelo_log", 
            "previsao_modelo_svm"
        ]
        
        for modelo in modelos:
            metrics = calcular_metrica_confusao_por_modelo(dados, modelo)
            if metrics:
                resultado.update(metrics)

        put_s3(resultado)
    except Exception as e:
        logger.info(e)
def get_s3():
    s3 = get_s3_client()
    response = s3.get_object(Bucket='resultado-partidas', Key='previstas.json')
    dados = json.load(response['Body'])
    return dados

def put_s3(dado):
    s3 = get_s3_client()
    s3.put_object(Bucket='resultado-partidas', Key='matriz_confusao.json', Body=json.dumps(dado, indent=4))
    
def get_s3_client():
    return boto3.client('s3')
gerar_matriz()

def send_message_to_sqs(message_body, queue_url):
    session = boto3.Session()
    sqs = session.client('sqs',
        region_name='us-east-1' )
    
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=str(message_body)
        )
        logger.info(f'Mensagem enviada com sucesso! ID: {response["MessageId"]}')
    except Exception as e:
        logger.error(f'Erro ao enviar mensagem: {e}')
        logger.info(f'Erro ao enviar mensagem: {e}')


def get_json_previstas():
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket='resultado-partidas', Key='previstas.json')
    dados = json.load(response['Body'])
    return dados
def get_json_matriz():
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket='resultado-partidas', Key='matriz_confusao.json')
    dados = json.load(response['Body'])
    return dados


app = Flask(__name__)
CORS(app)

@app.route('/listen/<puuid>', methods=['GET'])
def predict(puuid):
    try:
        send_message_to_sqs(puuid, "https://sqs.us-east-1.amazonaws.com/060834380790/partias-para-prever")
        return jsonify(f"Sucesso ")

    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/listen1/<puuid>', methods=['GET','OPTIONS'])
def listen(puuid):
    try:
        send_message_to_sqs(puuid, "https://sqs.us-east-1.amazonaws.com/060834380790/partidas-para-prever-2")
        return jsonify(f"Sucesso ")

    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/listen2/<puuid>', methods=['GET','OPTIONS'])
def listen2(puuid):
    try:
        send_message_to_sqs(puuid, "https://sqs.us-east-1.amazonaws.com/060834380790/partidas-para-prever-3")
        return jsonify(f"Sucesso ")

    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/previstas', methods=['GET','OPTIONS'])
def previstas():
    try:        
        resposa = get_json_previstas()
        return jsonify(resposa)

    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/previstas/matriz', methods=['GET','OPTIONS'])
def matriz():
    try:    
        gerar_matriz()    
        resposa = get_json_matriz()
        return jsonify(resposa)

    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/previstas/atualizar/<api_key>', methods=['GET','OPTIONS'])
def atualizar(api_key):
    try:
        get_resultados_partidas(api_key)
        return jsonify("Ok")

    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        return jsonify({'error': str(e)}), 400
    
if __name__ == '__main__':
    logger.info("Iniciei")
    app.run(host='0.0.0.0', port=5000)



