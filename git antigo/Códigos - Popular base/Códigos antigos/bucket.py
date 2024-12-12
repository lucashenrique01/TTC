import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_s3_client():
    return boto3.client('s3',
        aws_access_key_id='ASIAQ4KQC7P3HR6IUXAS',
        aws_secret_access_key='tAmRACuqq9Qe3w4mqeMxJA7ZywhZv7kucWtTTVw7',
        aws_session_token='IQoJb3JpZ2luX2VjEKP//////////wEaCXVzLXdlc3QtMiJHMEUCIQCS4b7kdRGDBkoW2/eEW9Dm3kQ2PJ2KFZNQYmZNyrGSXQIgLB80pH9y8I0l2JxFtq40k80V+hBhLqsstHJ50ySyrFkqvAIIzP//////////ARAAGgwwNjA4MzQzODA3OTAiDO7Y+zavxkKdQeHhzCqQArSoJz0DjyX6xXzos2N7jO6UA6MzTdFqddOPAKRGyvGmf1CIpO4bgu7gBNivsix4wJQkhaYJKkvsjPvlpCsCI8oYSBHnxsXDo7SKI1hS6hAvKBovbMtNbXvyq4u+/+zcKp8MhaAJJsd1AsMHW3kK2IMdw1v3fMnKG1l6T7nsHYJeKS3hI0WMOARLcrAH4r+jqISeuWpEvBpAxfZ+alDwsPM5Yx4hFyGU7fRlbtVvoh3DlBP35r00oPtV5Qqxob9S/JM9hMSGwv1gnavvz2qZB7diAVJSty9AMORdII+TGdDQ1eBBUt5lb+p7/YI/YGdrzpzTSAPNGKTqmr5feWqr0lUJgFjsd8a6xahUolWA2H7nMIfvk7cGOp0BT7q/aDEdVlIKceTdy9Q8+LxBFqHkv5GSxudQOG+cSKOp7uATp96ZrJELaQN3NkOS6bB1lnDCkJUQ8I1YfnxvxkpD7G8auGT+bYGM78wQkbxRbV4uL48uPVFAo/VBxiLizPhysm9AF4437ZwU3Ws4cIvKJzTITUg/P4ZFLHFIU/32abQh+/eztHiQ0grzJLbdF059SxVIPqOU5MWK6A==',
        region_name='us-east-1')

def create_s3_bucket(bucket_name):
    try:
        # Obtém o cliente S3 com as credenciais fornecidas
        s3_client = get_s3_client()
        
        # Cria o bucket
        s3_client.create_bucket(Bucket=bucket_name)
        
        print(f'Bucket {bucket_name} criado com sucesso!')
    except NoCredentialsError:
        print('Credenciais da AWS não encontradas.')
    except PartialCredentialsError:
        print('Credenciais da AWS incompletas.')
    except Exception as e:
        print(f'Erro ao criar o bucket: {e}')
