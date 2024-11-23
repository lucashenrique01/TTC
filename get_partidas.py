import requests
import time

API_KEY = '' #xispeke1
API_KEY_2 = '' 
API_KEY_3 = '' #xispeke23

partidas_postadas = []

while True:
    print("Vou tentar buscar partidas")
    postei = False
    response = requests.get(f"https://br1.api.riotgames.com/lol/spectator/v5/featured-games?api_key={API_KEY}")
    # response_2 = requests.get(f"https://br1.api.riotgames.com/lol/spectator/v5/featured-games?api_key={API_KEY_2}")
    # response_3 = requests.get(f"https://br1.api.riotgames.com/lol/spectator/v5/featured-games?api_key={API_KEY_3}")
    try:
        if response.status_code == 200:
            partidas = response.json()['gameList']
            # partidas_2 = response_2.json()['gameList']
            # partidas_3 = response_3.json()['gameList']
            if partidas:
                for i, partida in enumerate(partidas):
                    if partida['gameMode'] == 'CLASSIC':
                        id_partida = partida['gameId']
                        # id_partida_2 = partidas_2[i]['gameId']
                        # id_partida_3 = partidas_3[i]['gameId']
                        if id_partida:
                            print("Tem ranqueada!")
                            puuid = partida['participants'][0]['puuid']
                            response_back = requests.get(f"http://3.230.129.88:5000/listen/{puuid}")
                            if response_back.status_code == 200:
                                postei = True
                                partidas_postadas.append(id_partida)
                                print(f"Partida 1 {id_partida} - Postei {puuid}")
                            # puuid_2 = partidas_2[i]['participants'][0]['puuid']
                            # response_back2 = requests.get(f"http://3.230.129.88:5000/listen1/{puuid_2}")
                            # if response_back2.status_code == 200:
                            #     postei = True
                            #     partidas_postadas.append(id_partida_2)
                            #     print(f"Partida 2 {id_partida_2} - Postei {puuid_2}")
                            # puuid_3 = partidas_3[i]['participants'][0]['puuid']
                            # response_back3 = requests.get(f"http://3.230.129.88:5000/listen2/{puuid_3}")
                            # if response_back3.status_code == 200:
                            #     postei = True
                            #     partidas_postadas.append(id_partida_3)
                            #     print(f"Partida 3 {id_partida_3} - Postei {puuid_3}")
    except Exception as e:
        print(e)        
                    
    if response.status_code == 403:
        print("RENOVE API KEY")
        exit()
    tempo_aguardar = 520 if postei else 30
    print(f"Vou aguardar {tempo_aguardar} segundos para tentar novamente...")
    time.sleep(tempo_aguardar)