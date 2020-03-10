import os
import json

sni_file = os.listdir("./sni_result")
sni_ip = {} # sni_name: numbers

for item in sni_file:
    content = open("./sni_result/"+item, "r").read().strip()
    sni_list = content.split('\n')
    for ip_sni in sni_list:
        sni = ip_sni.split(",")[1].strip()
        if sni in sni_ip:
            pass
        else:
            sni_ip[sni] = ip_sni.split(",")[0].strip()

domain_sni = {
        'gmail': [],
        'facebook': [],
        'msn': [],
        'roblox': [],
        'riot': [],
        'epic': [],
        'cloudfront': [],
        'microsoft': [],
        'nyu': [],
        'bilibili': [],
        'spotify': [],
        'steam': [],
        'google': [],
        'icloud': [],
        'discord': [],
        'origin': [],
        'netflix': [],
        'apple': [],
        'battle': [],
        'skype': [],
        'nvidia': [],
        'twitter': [],
        'xbox': [],
        'leagueoflegends': [],
        'adobe': [],
        'qq': [],
        'slack': [],
        }

with open('sni_hottest', 'r') as f:
    sni_list = f.read().strip().split('\n')

domains = ['gmail', 'facebook', 'msn', 'roblox', 'riot', 'epic', 'cloudfront', 'microsoft', 'nyu', 
            'bilibili', 'spotify', 'steam', 'google', 'icloud', 'discord', 'origin', 'netflix', 
            'apple', 'battle', 'skype', 'nvidia', 'twitter', 'xbox', 'leagueoflegends', 'adobe', 'qq', 'slack']

for row in sni_list:
    sni = row.split('\t')[0]
    for domain in domains:
        if domain in sni:
            # domain_sni[domain].append(sni)
            domain_sni[domain].append({sni: sni_ip[sni]})
print(json.dumps(domain_sni))
with open('domain_sni.json', 'w') as f:
    json.dump(domain_sni, f)