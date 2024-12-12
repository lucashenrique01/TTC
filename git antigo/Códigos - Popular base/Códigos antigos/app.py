from funcoes import *
import sys

parametro = sys.argv[1]
json_matchsids = get_matchs(parametro)

if json_matchsids:
    for item in json_matchsids:
        upload_to_s3('matchts-ids',item, '')
        match_info = get_match_info(item)
        upload_to_s3('match-info',item+'.json',match_info)
