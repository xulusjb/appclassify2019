import sys, os
import json
from subprocess import Popen
from subprocess import check_output
from scapy.all import *


class Filter(object):
    """docstring for Filter"""
    def __init__(self):
        self.domain_sni = {}
        self.inverted_ips = {}

    def read_sni(self, path):
        with open(path) as f:
            self.domain_sni = json.load(f)

        for app in self.domain_sni:
            for sni_ip in self.domain_sni[app]:
                ip = list(sni_ip.values())[0]
                self.inverted_ips[ip] = app


    def filter(self, path):
        try:
            os.mkdir('./pcaps_filtered/')
        except Exception as e:
            pass

        for filename in os.listdir(path):

            print('Processing '+filename+' ...')
            # packets = rdpcap(path+filename)
            pcap_reader = PcapReader(path+filename)
            self.filtered = {}
            for packet in pcap_reader:
                if packet.haslayer(IP):
                    if ((packet[IP].src in self.dest_ip) or (packet[IP].dst in self.dest_ip)):
                        if packet[IP].proto == 6:
                            self.check_packet(packet, 'TCP')
                        elif packet[IP].proto == 17:
                            self.check_packet(packet, 'UDP')

            pcap_reader.close()

    def check_packet(self, packet, proto):
        info = (packet[IP].src, packet[IP].dst, packet[proto].sport, packet[proto].dport)
        info_reverse = (packet[IP].dst, packet[IP].src, packet[proto].dport, packet[proto].sport)
        app = None

        is_candidate = False
        if packet[IP].src in self.inverted_ips:
            app = self.inverted_ips[packet[IP].src]
            # Anonymize source ip
            packet[IP].dst = "1.1.1.1"
            is_candidate = True

        elif packet[IP].dst in self.inverted_ips:
            app = self.inverted_ips[packet[IP].dst]
            # Anonymize source ip
            packet[IP].src = "1.1.1.1"
            is_candidate = True

        if is_candidate:
            if not info in self.filtered and not info_reverse in self.filtered:
                if self.check_client_hello(packet):
                    self.new_session(info, app, packet)

            elif info in self.result:
                if self.check_client_hello(packet):
                    self.save_pcap(info)
                    self.new_session(info, app, packet)
                else:
                    self.filtered[info]['packets'].append(packet)

            elif info_reverse in self.result:
                if self.check_client_hello(packet):
                    self.save_pcap(info_reverse)
                    self.new_session(info_reverse, app, packet)
                else:
                    self.filtered[info_reverse]['packets'].append(packet)

    def check_client_hello(self, packet, info):
        is_client_hello = False
        if packet.haslayer(TLS):
            print(packet)
            is_client_hello = 

        sys.exit()
        return is_client_hello

    def new_session(self, info, app, packet):
        self.filtered[info] = {}
        self.filtered[info]['app'] = app

        self.filtered[info]['packets'] = []
        self.filtered[info]['packets'].append(packet)


    def.save_pcap(self, info):
        app = self.filtered[info]['app']
        packets = self.filtered[info]['packets']

        path = './pcaps_filtered/'+app+'/'
        try:
            os.mkdir(path)
        except Exception as e:
            pass

        wrpcap(path+str(int(time.time()))+'.pcap', packets)

if __name__ == '__main__':
    load_layer("tls")
    f = Filter()
    f.read_sni('./domain_sni.json')
    print(f.inverted_ips.keys())
    f.filter('./pcaps')