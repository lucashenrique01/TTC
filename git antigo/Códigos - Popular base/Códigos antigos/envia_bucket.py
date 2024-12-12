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
    pasta = filedialog.askdirectory(title="Escolha a pasta com os arquivos JSON")
    return pasta

# Função para enviar arquivos JSON ao bucket S3
def enviar_arquivos_json(bucket_name, pasta_local):
    # Verifica se a pasta existe
    if not os.path.exists(pasta_local):
        print("Pasta não encontrada.")
        return
    
    # Percorre os arquivos na pasta escolhida
    for arquivo in os.listdir(pasta_local):
        if arquivo.endswith('.json'):
            caminho_arquivo = os.path.join(pasta_local, arquivo)
            
            # Envia o arquivo JSON para o bucket S3
            s3_client.upload_file(caminho_arquivo, bucket_name, arquivo)
            print(f"Arquivo {arquivo} enviado para o bucket {bucket_name}")
        else:
            print(f"{arquivo} não é um arquivo JSON. Ignorado.")

# Exemplo de uso
bucket_name = 'match-info'
pasta_local = escolher_pasta()  # Abre uma janela para escolher a pasta com os JSONs

if pasta_local:
    enviar_arquivos_json(bucket_name, pasta_local)
else:
    print("Nenhuma pasta foi selecionada.")
