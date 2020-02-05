from scapy.all import *
from os import listdir
import time
import re 
class Parser:
    def __init__(self):
        self.addr_dic = {"email": "smtp.gmail.com."}
        self.packet_num = 20
        self.payload_length = 99999999  # prevent the code to stop before accumulating packet_num packets
        self.wanted = 8000
        
    def parse_all_mode(self, file, mode='p'):
        print('Reading:', file)
        self.count = 0
        self.result = {}

        scapy_cap = rdpcap(file)
        category = (file.split("/")[-1]).split("_")[0]
        for packet in scapy_cap:
            self.count += 1
            # print(self.count)
            if packet.haslayer(IP):
                # collect packet where (dest.ip, src.ip, dest.port, src.port, tcp) are the same 
                # tcp:6, udp:17
                if (packet[IP].proto == 6 or packet[IP].proto == 17) and (packet[IP].src != '216.165.95.134' and packet[IP].dst != '216.165.95.134'):

                    if packet.haslayer(TCP):
                        info = (packet[IP].src, packet[IP].dst, packet[TCP].sport, packet[TCP].dport)
                        info_reverse = (packet[IP].dst, packet[IP].src, packet[TCP].dport, packet[TCP].sport)
                    else:
                        info = (packet[IP].src, packet[IP].dst, packet[UDP].sport, packet[UDP].dport)
                        info_reverse = (packet[IP].dst, packet[IP].src, packet[UDP].dport, packet[UDP].sport)

                    # print(info)
                    if not info in self.result and not info_reverse in self.result:
                        self.result[info] = {}
                        self.result[info]['sizeresult'] = []
                        self.result[info]['intresult'] = []
                        self.result[info]['payload_result'] = b''
                        self.result[info]['plength_result'] = []
                        self.result[info]['payload_inter_result'] = b''

                        self.result[info]['previous_packet'] = None
                        self.result[info]['previous_packet_pi'] = None
                        self.result[info]['count'] = 0
                        self.result[info]['finished'] = False

                    elif info in self.result:
                        self.append(packet, info)

                    elif info_reverse in self.result:
                        self.append(packet, info_reverse)

        return self.result

    def append(self, packet, info):
        if self.result[info]['finished'] == True:
            pass
        else:
            self.payload(packet, info)
            self.packet_size(packet, info)
            self.packet_interval(packet, info)
            self.result[info]['count'] += 1
        
            if self.result[info]['count'] >= self.packet_num and len(self.result[info]['payload_result']) > self.wanted:
                print(self.result[info]['count'])
                self.result[info]['payload_result'] = self.result[info]['payload_result'][0:self.wanted]
                a = [i for i in self.result[info]['payload_result']]
                self.result[info]['payload_result'] = [i for i in self.result[info]['payload_result']]
                self.result[info]['finished'] = True

    def payload(self, packet, info):
        interval = []
        if self.result[info]['previous_packet_pi'] is None:
            self.result[info]['previous_packet_pi'] = packet
        else:
            delta = int(float(packet.time - self.result[info]['previous_packet_pi'].time) * 1000000)
            interval = [delta // 1000000, (delta // 10000)%100, (delta // 100) %100, delta % 100]  # interval = [12,34,56,78]
            self.result[info]['previous_packet_pi'] = packet

        # packet.show()
        if packet[IP].proto == 6: # tcp
            # TLS
            if packet.haslayer(TLS):
                if packet.haslayer(TLSApplicationData):
                    payload = packet[TLSApplicationData].data
                    self.result[info]['payload_result'] = self.result[info]['payload_result'] + payload
                    self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + bytes(interval)  # directly add interval here
                    self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + payload

                    self.result[info]['plength_result'].append(len(payload))
                else:
                    self.result[info]['plength_result'].append(0)

            # TLS packet
            elif packet.haslayer(SSLv2):
                if packet.haslayer(Raw):
                    payload = packet[Raw].load
                    self.result[info]['payload_result'] = self.result[info]['payload_result'] + payload
                    self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + bytes(interval)  # directly add interval here
                    self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + payload

                    self.result[info]['plength_result'].append(len(payload))
                else:
                    self.result[info]['plength_result'].append(0)

            # TLS packets that can't be parsed by Scapy
            elif packet.haslayer(Raw):
                payload = packet[Raw].load
                self.result[info]['payload_result'] = self.result[info]['payload_result'] + payload
                self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + bytes(interval)  # directly add interval here
                self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + payload

                self.result[info]['plength_result'].append(len(payload))

        elif packet[IP].proto == 17: # udp
            if packet.haslayer(Raw):
                payload = packet[Raw].load
                self.result[info]['payload_result'] = self.result[info]['payload_result'] + payload
                self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + bytes(interval)  # directly add interval here
                self.result[info]['payload_inter_result'] = self.result[info]['payload_inter_result'] + payload

                self.result[info]['plength_result'].append(len(payload))

    def packet_size(self, packet, info):
        self.result[info]['sizeresult'].append(len(packet))

    def packet_interval(self, packet, info):
        if self.result[info]['previous_packet'] is None:
            self.result[info]['previous_packet'] = packet
        else:
            delta = float(packet.time - self.result[info]['previous_packet'].time)
            self.result[info]['intresult'].append(delta)
            self.result[info]['previous_packet'] = packet


if __name__=="__main__":
    load_layer("tls")
    parser = Parser()
    category = ['email', 'vpn_email', 'p2p', 'vpn_p2p']
    # category = ['p2p']
    total = 0
    for cate in category:
        print(cate)
        total = 0
        file_list = listdir('./result' + cate)
        pf= open("./data/"+cate+"_p.txt","a")
        sf = open("./data/"+cate+"_s.txt", "a")
        interf = open("./data/"+cate+"_inter.txt", "a")
        plf = open("./data/"+cate+"_pl.txt", "a")
        pif = open("./data/"+cate+"_pi.txt","a")
        for file in file_list:
            total+=1
            print(total)
            result = parser.parse_all_mode("./result/"+cate+"/"+file)
            if result:
                for i in result:
                    p_length = len(result[i]['payload_result'])
                    if p_length >= 1500 :
                        print(i)
                        print()
                        if p_length < 8000:
                            result[i]['payload_result'] = result[i]['payload_result'] + b'\x00' * (8000 - p_length)
                        pi_length = len(result[i]['payload_inter_result'])
                        if pi_length < 8000:
                            result[i]['payload_inter_result'] = result[i]['payload_inter_result'] + b'\x00' * (8000 - pi_length)

                        pf.write(" ".join(str(int(j)) for j in result[i]['payload_result'])+"\n")
                        sf.write(" ".join(str(int(j)) for j in result[i]['sizeresult'])+"\n")
                        interf.write(" ".join(str(int(j*1000000)) for j in result[i]['intresult'])+"\n")
                        plf.write(" ".join(str(int(j)) for j in result[i]['plength_result'])+"\n")
                        pif.write(" ".join(str(int(j)) for j in result[i]['payload_inter_result'])+"\n")  #payload
            else:
                pass
        pf.close()
        sf.close()
        interf.close()
        plf.close()
        pif.close()