from scapy.all import *
from os import listdir
from scapy.utils import hexdump
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
        self.result_pi = []
        self.result_px = []
        self.sizeresult = []
        self.intresult = []
        self.payload_result = b''
        self.payload_inter_result = b''
        self.payload_FFFFFF_result = b''
        self.plength_result = []
        self.previous_packet = None

    def parse_all_mode(self, file):
        total_result = []
        p, pi = self.parse(file,mode = 'p')
        if not p:  # this data piece can not form data
        	return None
        total_result.append(p)
        total_result.append(self.sizeresult)
        total_result.append(self.intresult)
        total_result.append(self.plength_result)
        total_result.append(pi)
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
        self.result_pi = []
        self.result_px = []
        self.sizeresult = []
        self.intresult = []
        self.payload_result = b''
        self.payload_inter_result = b''
        self.payload_FFFFFF_result = b''
        self.plength_result = []
        self.dest_ip =  "0.0.0.0"
        self.previous_packet = None
        self.previous_packet_pi = None
        
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
                #print("IP address is founded in packet number: ", i)
                

            if self.ip_founded and packet.haslayer(IP):
                # collect packet where dest.ip or sour.ip == self.dest_ip (~20)
                # tcp:6, udp:17
                if ((packet[IP].proto == 6) or (packet[IP].proto == 17)) and \
                    ((packet[IP].src == self.dest_ip) or (packet[IP].dst == self.dest_ip)):
                    switcher = {
                            'p': self.payload,
                            's': self.packet_size,
                            'i': self.packet_interval
                            }
                    #print("packet num:", i)
                    switcher.get('p')(packet)
                    switcher.get('s')(packet)
                    switcher.get('i')(packet)
                    
                if self.count >= self.packet_num:
                    if len(self.payload_result) < self.wanted:
                        pass
                    else:
                        self.payload_result = self.payload_result[0:self.wanted]  #this is the 8000 length payload
                        self.payload_inter_result = self.payload_inter_result[0:self.wanted]
                        self.payload_FFFFFF_result = self.payload_FFFFFF_result[0:self.wanted]
                        #print("self.payload_result", self.payload_result)
                        
                    self.result = [i for i in self.payload_result]  # payload result
                    self.result_pi = [i for i in self.payload_inter_result]  # payload + interval result
                    self.result_px = [i for i in self.payload_FFFFFF_result]  # payload + interval result
                    #print("self.result:", self.result)
                    return self.result, self.result_pi, self.result_px

        return None, None, None


    def payload(self, packet):  # computer interval first for making p+i data, then store p and p+i data individually. i is for 4 bytes: '01122334'
        interval = []
        if self.previous_packet_pi is None:
            self.previous_packet_pi = packet
        else:
            delta = int(float(packet.time - self.previous_packet_pi.time) * 1000000)
            interval = [delta // 1000000, (delta // 10000)%100, (delta // 100) %100, delta % 100]  # interval = [12,34,56,78]
            self.previous_packet_pi = packet

        
        if packet[IP].proto == 6: # tcp
            #print("packet haslayer(TLS): ", ( "True" if packet.haslayer(TLS) else "False"))
            #print("packet.haslayer(SSLv2): ", ( "True" if packet.haslayer(SSLv2) else "False"))
            # TCP packet
            if packet.haslayer(TLS):
                if packet.haslayer(TLSApplicationData):
                    payload = packet[TLSApplicationData].data
                    self.payload_result = self.payload_result + payload # modified for packet-end-signal, 3 different places in the code.
                    if self.payload_inter_result != b'':
                        self.payload_inter_result = self.payload_inter_result + bytes(interval)  # directly add interval here
                    self.payload_inter_result = self.payload_inter_result + payload
                    if self.payload_FFFFFF_result != b'':
                        self.payload_FFFFFF_result = self.payload_FFFFFF_result + b'\xff' * 6 # directly add interval here
                    self.payload_FFFFFF_result = self.payload_FFFFFF_result + payload
                    #print("payload length: ", len(payload))
                    #print("payload decoding: ", hexdump(payload))
                    #print("data recorded!---------------------------------------")
                    #time.sleep(10)
                    self.plength_result.append(len(payload))
                else:
                    self.plength_result.append(0)

            # TLS packet
            elif packet.haslayer(SSLv2):
                if packet.haslayer(Raw):
                    payload = packet[Raw].load
                    #print("payload2:", payload)
                    #print("payload length: ", len(payload))
                    #print("payload decoding: ", hexdump(payload))
                    #print("payload type:", type(payload))
                    #print("payload len:", len(payload))
                    #print("payload 0 :", payload[0])
                    #print("int payload 0:", int(payload[0]))
                    #print("before r1:", self.payload_result)
                    #print("before r2:", self.payload_inter_result)
                    self.payload_result = self.payload_result + payload
                    #print("inserted interval: ", interval)
                    if self.payload_inter_result != b'':
                        self.payload_inter_result = self.payload_inter_result + bytes(interval)  # directly add interval here
                    self.payload_inter_result = self.payload_inter_result + payload
                    if self.payload_FFFFFF_result != b'':
                        self.payload_FFFFFF_result = self.payload_FFFFFF_result + b'\xff' * 6 # directly add interval here
                    self.payload_FFFFFF_result = self.payload_FFFFFF_result + payload
                    #print("r1:", self.payload_result)
                    #print("r2:", self.payload_inter_result)
                    self.plength_result.append(len(payload))
                    #print("data recorded!-------------------------------------------------------")
                    #time.sleep(5)
                else:
                    self.plength_result.append(0)
            else:	
                self.plength_result.append(0)

        elif packet[IP].proto == 17: # udp
            payload = packet[Raw].load
            self.payload_result = self.payload_result + payload
            if self.payload_inter_result != b'':
                self.payload_inter_result = self.payload_inter_result + bytes(interval)  # directly add interval here
            self.payload_inter_result = self.payload_inter_result + payload

            if self.payload_FFFFFF_result != b'':
                self.payload_FFFFFF_result = self.payload_FFFFFF_result + b'\xff' * 6 # directly add interval here
            self.payload_FFFFFF_result = self.payload_FFFFFF_result + payload
            #print("data recorded!--------------------------------------------------------------")
            self.plength_result.append(len(payload))

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
    http2_category = ['a','f','i','r','s','so','t','w']
    # http2_category = ['a', 'f', 'i', 'r']
    #http2_category = ['s','so','t','w']
    #http3_category = ['g','gc','gd','gdr','gf','tb','tr','y']
    total = 0
    for cate in http2_category:
        print(cate)
        total = 0
        file_list = listdir('./' + cate)
        pf= open(cate+"_p.txt","a")
        sf = open(cate+"_s.txt", "a")
        interf = open(cate+"_inter.txt", "a")
        plf = open(cate+"_pl.txt", "a")
        pif = open(cate+"_pi.txt","a")
        pxf = open(cate+"_px.txt", "a")

        for file in file_list:
            total+=1
            print(total)
            #print("./"+cate+"/"+file)
            payload = parser.parse_all_mode("./"+cate+"/"+file)
            if payload:
                pf.write(" ".join(str(int(j)) for j in payload[0])+"\n")  #payload
                sf.write(" ".join(str(int(j)) for j in payload[1])+"\n")  #size (length of packet, not payload) (for all the packets between the ip of sender and receiver)
                interf.write(" ".join(str(int(j*1000000)) for j in payload[2])+"\n")  #interval time
                plf.write(" ".join(str(int(j)) for j in payload[3])+"\n") #packet length (length of payload)
                pif.write(" ".join(str(int(j)) for j in payload[4])+"\n")  #payload + interval time
                pxf.write(" ".join(str(int(j)) for j in payload[5])+"\n")  #payload + FFFFFF
        
        pf.close()
        sf.close()
        interf.close()
        plf.close()
        pif.close()
        pxf.close()
