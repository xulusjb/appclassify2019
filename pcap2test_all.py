from scapy.all import *
from os import listdir
import time
import re 
class Parser:
    def __init__(self):
        self.addr_dic = {"gc": "calendar.google.com.", "tb":"www.tumblr.com.", \
                        "g": "www.google.com.", "y":"www.youtube.com.", \
                        "gd":"docs.google.com.", "gdr":"drive.google.com.", \
                        "gf":"www.google.com.", "tr":"translate.google.com.", \
                        "s":"open.spotify.com.", "a":"www.amazon.com.", \
                        "f": "www.facebook.com.", "t": "twitter.com.", \
                        "w": "en.wikipedia.org.", "r": "www.reddit.com.", \
                        "i":"www.instagram.com.", "so": "stackoverflow.com."}
        self.packet_num = 20
        self.payload_length = 99999999  # prevent the code to stop before accumulating packet_num packets
        self.wanted = 8000
        self.dest_ip = "0.0.0.0"
        self.mode = "p"  # p=all_payload, s= all_packetsize, i = interval time
        self.ip_founded = False
        self.count = 0
        self.result = []
        self.sizeresult = []
        self.intresult = []
        self.payload_result = b''
        self.previous_packet = None

    def parse_all_mode(self, file):
        total_result = []
        p = self.parse(file,mode = 'p')
        if not p:  # this data piece can not form data
        	return None
        total_result.append(p)
        total_result.append(self.sizeresult)
        total_result.append(self.intresult)
        return total_result
    
    def check_ip(self,ip):
        regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''
        if(re.search(regex, ip)):
            return True
        else:
            return False
        
    def parse(self, file, mode='p'):
        self.mode = mode
        self.count = 0
        self.ip_founded = False
        self.result = []
        self.sizeresult = []
        self.intresult = []
        self.payload_result = b''
        self.dest_ip =  "0.0.0.0"
        self.previous_packet = None
        
        scapy_cap = rdpcap(file)
        category = (file.split("/")[-1]).split("_")[0]
        i = 0
        for packet in scapy_cap:
            i += 1
            if packet.haslayer(DNSRR) and isinstance(packet.an, DNSRR) and packet.an.rrname.decode("utf-8") == self.addr_dic[category]:
                for x in range(packet[DNS].ancount):
                    candidate = packet[DNSRR][x].rdata
                    if type(candidate) is str and self.check_ip(candidate):
                        self.dest_ip =  candidate
                        break
                
                self.ip_founded = True
                

            if self.ip_founded and packet.haslayer(IP):
                # collect packet where dest.ip or sour.ip == self.dest_ip (~20)
                # tcp:6, udp:17
                if ((packet[IP].proto == 6) or (packet[IP].proto == 17)) and \
                    ((packet[IP].src == self.dest_ip) or (packet[IP].dst == self.dest_ip)):
                    switcher = {
                            'p': self.payload,
                            's': self.packet_size,
                            'i': self.packet_interval
                            # TODO: More mode and corresponding functions
                            }

                    switcher.get('p')(packet)
                    switcher.get('s')(packet)
                    switcher.get('i')(packet)
                
                if self.count >= self.packet_num:
                    if self.mode == 'p':

                        if len(self.payload_result) > self.wanted:
                            self.payload_result = self.payload_result[0:self.wanted]
                        else:
                            self.payload_result = self.payload_result + b'\x00' * (self.wanted - len(self.payload_result))
                        self.result = [i for i in self.payload_result]
                    return self.result


    def payload(self, packet):
        if packet[IP].proto == 6: # tcp
            # TCP packet
            if packet.haslayer(TLS):
                if packet.haslayer(TLSApplicationData):
                    payload = packet[TLSApplicationData].data
                    self.payload_result = self.payload_result + payload

            # TLS packet
            if packet.haslayer(SSLv2):
                if packet.haslayer(Raw):
                    payload = packet[Raw].load
                    self.payload_result = self.payload_result + payload


        if packet[IP].proto == 17: # udp
            payload = packet[Raw].load
            self.payload_result = self.payload_result + payload

    def packet_size(self, packet):
        self.sizeresult.append(len(packet))
        self.count += 1

    def packet_interval(self, packet):
        if self.previous_packet is None:
            self.previous_packet = packet
        else:
            delta = float(packet.time - self.previous_packet.time)
            self.intresult.append(delta)
            self.previous_packet = packet


if __name__=="__main__":
    load_layer("tls")
    parser = Parser()
    #parser.parse('so_1572536834.pcap', 'p')
    http2_category = ['a','f','i','r','s','so','t','w']
    #http2_category = ['a', 'f', 'i', 'r']
    #http2_category = ['so','s','t','w']
    http3_category = ['g','gc','gd','gdr','gf','tb','tr','y']
    total = 0
    for cate in http2_category:
        print(cate)
        total = 0
        file_list = listdir('./' + cate)
        pf= open(cate+"_p.txt","a")
        sf = open(cate+"_s.txt", "a")
        interf = open(cate+"_inter.txt", "a")
        for file in file_list:
            total+=1
            print(total)
            payload = parser.parse_all_mode("./"+cate+"/"+file)
            if payload:
                pf.write(" ".join(str(int(j)) for j in payload[0])+"\n")
                sf.write(" ".join(str(int(j)) for j in payload[1])+"\n")
                interf.write(" ".join(str(int(j*1000000)) for j in payload[2])+"\n")
        pf.close()
        sf.close()
        interf.close()