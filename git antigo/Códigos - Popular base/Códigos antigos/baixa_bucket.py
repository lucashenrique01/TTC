import boto3
import os
from tkinter import Tk, filedialog

# Configura as credenciais AWS (certifique-se de que estão corretas ou configuradas no ambiente)
s3_client = boto3.client('s3',
    aws_access_key_id='ASIAQ4KQC7P3CRU2EDGJ',
    aws_secret_access_key='fav2aDeDUeG+A6XO+T9g/WO/Gc0BLZ3l4ro4rJXE',
    aws_session_token='IQoJb3JpZ2luX2VjEBkaCXVzLXdlc3QtMiJIMEYCIQCy2P3yRU5R71fZryz7yqUqtDmUTdHhm199wbFz1ZeMdwIhALyZkyVWJFnH5F8I5ENA9X3PfmvRlbVvHjMhhIsAlNivKrMCCFIQABoMMDYwODM0MzgwNzkwIgwOOEiuz0SfnPP8uU8qkAI3G/eIPMJJ+eZGhPs+6IqkXDDnqpOzXQBdu/AnbkK8E1gkxFa5Klio9xARDqBNMG1Xhu3Cl1A6gKC0rsE1bgmG2ppdRhwkANS0dtL6VGh9c6JFMX7Jze/QtjNP41yOuUzoxpA3Aqdmwqwfa08fB0IJBcsNzTdzuGgZQgdzWA6f2YbwhcQIINzENGqXntguJDbCK/NPfoZsl1uGfShYmoM2cASD8Pilq4mb4v48KRvVU3Ey62d31FCaCDaoMUIw3V2h9AUtM3xgr5XrSaD2aDuZZt0lwjFVr+xcttwVYrI0ixr4zkcBleLKHYxyJmODMftl+uFkdFqcH5KHAegGiNHDJv3v8qlqhwKKw9QUyHONHTD/4K23BjqcAaQfMIMvi5L+5k41krlft6C+Agvi5RiWpOlCzkQYe7zuRbDrUpFhvSJGuRvpMf6KnVXcCybQhSeed1ED5/siqpkSpXl4K/8uvqdJ8mF9hretly1D4iFBN2L7FW/t94/Z126qQFnSvAxFdKQZl4ySBWUsL6kjuaX9+HrrW74MeP/W/TS8YvLH/fF5Bz0KJhH7w+PJqL8KSo+k7NU8BQ==',
    region_name='us-east-1')

# Função para escolher a pasta usando Tkinter
def escolher_pasta():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do Tkinter
    pasta = filedialog.askdirectory(title="Escolha a pasta onde os arquivos JSON serão armazenados")
    return pasta

# Função para baixar arquivos JSON do bucket
def baixar_arquivos_json(bucket_name, pasta_local):
    # Lista os objetos dentro do bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    # Verifica se existem objetos no bucket
    if 'Contents' in response:
        for obj in response['Contents']:
            arquivo = obj['Key']
            
            # Baixa apenas os arquivos JSON
            if arquivo.endswith('.json'):
                # Define o caminho do arquivo na pasta de destino escolhida
                caminho_destino = os.path.join(pasta_local, os.path.basename(arquivo))  # Apenas o nome do arquivo
                
                # Cria diretórios locais se não existirem
                os.makedirs(pasta_local, exist_ok=True)
                
                # Baixa o arquivo
                s3_client.download_file(bucket_name, arquivo, caminho_destino)
                print(f"Arquivo {arquivo} baixado para {caminho_destino}")
    else:
        print("Nenhum objeto encontrado no bucket.")

# Exemplo de uso
bucket_name = 'match-info11'
pasta_local = escolher_pasta()  # Abre uma janela para escolher a pasta

if pasta_local:
    baixar_arquivos_json(bucket_name, pasta_local)
else:
    print("Nenhuma pasta foi selecionada.")
