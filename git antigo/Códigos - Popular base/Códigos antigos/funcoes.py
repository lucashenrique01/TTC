import requests
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError,ClientError

APIKEY = 'RGAPI-8e90acce-4dd4-4207-8a06-c137b5489dfc'

def get_matchs(puuid):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=100&api_key={APIKEY}"
    response = requests.get(url)
    if response.status_code == 200:
        upload_to_s3('puuids', puuid, '')
        return response.json()
    
def get_match_info(matchid):
    if(check_if_object_exists(matchid)):
        return
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={APIKEY}"
    response = requests.get(url)
    if response.status_code == 200:
        match_info = json.dumps(response.json()).encode('utf-8')
        return match_info
    
def get_s3_client():
    return boto3.client('s3',
        aws_access_key_id='ASIAQ4KQC7P3NPECR7AE',
        aws_secret_access_key='5GFnv2oVFlcNzur0rKWYkd9x81utUujpgsyXTKxP',
        aws_session_token='IQoJb3JpZ2luX2VjECoaCXVzLXdlc3QtMiJHMEUCIQD+DIn5evjjUL1dr6r+uuo4U8eDc7yd4iF0sB+LMPmFRwIgdm35AZO4MRzbqYTDg2UbtG35pMuC4STO4S+30BHHi08qswIIYxAAGgwwNjA4MzQzODA3OTAiDDWIk0LA/ZvhB/ybxSqQAtb5O+hbNqDF/ZmfTrCHMlbrB/wOfvH5cawluiBjb/LyQ4M4+twDuh+pX9yRPxKw3IS7zjnIThJ7SGGP11SCFY5oF6dDdNLH5no3LplUadPAek49WNbkHaKKKZB72SZGKw2r4Tr1cHyPqM6NyyQz6WlvuAiPxhx900M5dn8/DLKoFHmjgwQJECq2+3RrmQfk0RQ8UcDibtXjkxEnoARlyZPr9lP8z8mG0iP2qPRNCmx+RwVUJb4KdsMf/KYFfyD0L6YXPhVQjNXm997zbWkInl1hUTXMID3sQ2dE+eUfnlj8gH79YS2hTmsx/O0IbPy9Rd2iP73IxDxufZeQxJzfa5593dmp0hxtxxuzc3NYC20DMPPDsbcGOp0BzQlVVjZD1StRVI4Q/t1SIfLhA8aU2PJo85lisycqO3bcQF//KF2FyAwZzO9pMB9ZFEAf/W+GCN0egvcB/V80KKBBPfIP5S5/WxwUlvV/uPXAr+ON+z4COFLuXBC5CW02hxZOuMVTsKJfrJyEnf1Fr3lXWHcFHvf87OLBWLmGzjqTQZHPa+SOd9L/zTu5gfJmzlVT2wLo3h3NB3KwVg==',
        region_name='us-east-1')

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