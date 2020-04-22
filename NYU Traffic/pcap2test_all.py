from scapy.all import *
import os
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
        self.packet_num = 50
        self.payload_length = 99999999  # prevent the code to stop before accumulating packet_num packets
        self.wanted = 8000

        self.count = 0
        self.result = []
        self.result_pi = []
        self.result_px = []
        self.sizeresult = []
        self.intresult = []
        self.payload_result = b''
        self.payload_inter_result = b''
        self.plength_result = []
        self.previous_packet = None

    def parse_all_mode(self, file):
        total_result = []
        p, pi, px = self.parse(file,mode = 'p')
        if not p:  # this data piece can not form data
        	return None
        total_result.append(p)
        total_result.append(self.sizeresult)
        total_result.append(self.intresult)
        total_result.append(self.plength_result)
        total_result.append(pi)
        total_result.append(px)
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
        self.previous_packet_pi = None
        
        scapy_cap = rdpcap(file)
        category = (file.split("/")[-1]).split("_")[0]
        i = 0
        for packet in scapy_cap:
            i += 1
            self.payload(packet)
            self.packet_size(packet)
            self.packet_interval(packet)

            if self.count >= self.packet_num:
                return self.end_parse()

        return self.end_parse()

    def end_parse(self):
        if len(self.payload_result) < self.wanted:
            self.result = self.payload_result
            self.result_pi = self.payload_inter_result
            self.result_px = self.payload_FFFFFF_result
        else:
            self.payload_result = self.payload_result[0:self.wanted]  #this is the 8000 length payload
            self.payload_inter_result = self.payload_inter_result[0:self.wanted]
            self.payload_FFFFFF_result = self.payload_FFFFFF_result[0:self.wanted]
            #print("self.payload_result", self.payload_result)
            self.result = [i for i in self.payload_result]  # payload result
            self.result_pi = [i for i in self.payload_inter_result]  # payload + interval result
            self.result_px = [i for i in self.payload_FFFFFF_result]  # payload + FFFFFF
            #print("self.result:", self.result)

        return self.result, self.result_pi, self.result_px


    def payload(self, packet):  # computer interval first for making p+i data, then store p and p+i data individually. i is for 4 bytes: '01122334'
        interval = []
        if self.previous_packet_pi is None:
            self.previous_packet_pi = packet
        else:
            delta = int(float(packet.time - self.previous_packet_pi.time) * 1000000)
            if delta > 255:
                delta = 255
            interval = [delta // 1000000, (delta // 10000)%100, (delta // 100) %100, delta % 100]  # interval = [12,34,56,78]
            self.previous_packet_pi = packet

        
        if packet[IP].proto == 6: # tcp
            #print("packet haslayer(TLS): ", ( "True" if packet.haslayer(TLS) else "False"))
            #print("packet.haslayer(SSLv2): ", ( "True" if packet.haslayer(SSLv2) else "False"))
            # TLS packet
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
                    self.payload_result = self.payload_result + payload
                    if self.payload_inter_result != b'':
                        self.payload_inter_result = self.payload_inter_result + bytes(interval)  # directly add interval here
                    self.payload_inter_result = self.payload_inter_result + payload
                    if self.payload_FFFFFF_result != b'':
                        self.payload_FFFFFF_result = self.payload_FFFFFF_result + b'\xff' * 6 # directly add interval here
                    self.payload_FFFFFF_result = self.payload_FFFFFF_result + payload

                    self.plength_result.append(len(payload))
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

def open_files():
    pf= open('./result/'+cate+"_p.txt","a")
    sf = open('./result/'+cate+"_s.txt", "a")
    interf = open('./result/'+cate+"_inter.txt", "a")
    plf = open('./result/'+cate+"_pl.txt", "a")
    pif = open('./result/'+cate+"_pi.txt", "a")
    pxf = open('./result/'+cate+"_px.txt", "a")

    return pf, sf, interf, plf, pif, pxf

def write_to_files(payload, pf, sf, interf, plf, pif, pxf):
    pf.write(" ".join(str(int(j)) for j in payload[0])+"\n")  #payload
    sf.write(" ".join(str(int(j)) for j in payload[1])+"\n")  #size (length of packet) (for all the packets between the ip of sender and receiver)
    interf.write(" ".join(str(int(j*1000000)) for j in payload[2])+"\n")  #inter
    plf.write(" ".join(str(int(j)) for j in payload[3])+"\n") #packet length (length of payload)
    pif.write(" ".join(str(int(j)) for j in payload[4])+"\n")  #payload
    pxf.write(" ".join(str(int(j)) for j in payload[5])+"\n")  #payload

def close_files(pf, sf, interf, plf, pif, pxf):
    pf.close()
    sf.close()
    interf.close()
    plf.close()
    pif.close()
    pxf.close()

if __name__=="__main__":
    load_layer("tls")
    parser = Parser()
    NYU_category = os.listdir('./march_data')
    print(NYU_category)

    finished_category = []
    for file in os.listdir('./result'):
        cate = file.split('_')[0]
        if cate not in finished_category:
            finished_category.append(cate)
    print(finished_category)

    total = 0
    for cate in NYU_category:
        print('================')
        print(cate)
        if cate in finished_category:
            print('Passing '+cate+'...')
            continue

        total = 0
        file_list = os.listdir('./march_data/' + cate)
        try:
            os.mkdir('./result/')
        except Exception as e:
            pass

        pf, sf, interf, plf, pif, pxf = open_files()
        for file in file_list:
            total+=1
            if total%100 == 0:
                print(total)
            # print(file)
            #print("./"+cate+"/"+file)
            payload = parser.parse_all_mode("./march_data/"+cate+"/"+file)
            if payload:
                write_to_files(payload, pf, sf, interf, plf, pif, pxf)

        close_files(pf, sf, interf, plf, pif, pxf)
        print(total)