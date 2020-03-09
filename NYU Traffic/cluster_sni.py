import os
sni_file = os.listdir("./sni_result")

sni_dic = {} # sni_name: numbers

for item in sni_file:
    content = open("./sni_result/"+item, "r").read().strip()
    sni_list = content.split('\n')
    for ip_sni in sni_list:
        sni = ip_sni.split(",")[1].strip()
        if sni in sni_dic:
            sni_dic[sni] = sni_dic[sni] + 1
        else:
            sni_dic.update({sni:1})

f = open('sni_hottest', 'a')

i=0
for k, v in sorted(sni_dic.items(), key=lambda item: item[1], reverse=True):
    f.write("{0}\t{1}\n".format(k,v))
    i += 1
    if i > 1000:
        break

