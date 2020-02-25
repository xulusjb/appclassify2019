import sys, os
from subprocess import Popen
from subprocess import check_output
from scapy.all import *


class Filter(object):
    """docstring for Filter"""
    def __init__(self):
        self.filelist = ['facebook', 'email', 'youtube', 'hangout', 'gmail', 'icq', 'netflix', 'skype', 'spotify', 'vimeo', 'voipbuster']
        self.domains = {
            'facebook': ['facebook'],
            'email': ['googlemail'],
            'youtube': ['googlevideo', 'google', 'youtube', 'gstatic', 'ytimg', 'ggpht', 'googleusercontent', 'googletagservices', 'googlesyndication', 'googleapis'],
            'hangout': ['google', 'gstatic', 'googleusercontent', 'googleapis'],
            'gmail': ['google'],
            'icq': ['microsoft'],
            'netflix': ['netflix'],
            'skype': ['skypeassets', 'skype', 'live', 'hotmail'],
            'spotify': ['spotify'],
            'vimeo': ['vimeocdn', 'vimeo'],
            'voipbuster': ['voipbuster']
            }
        self.ips = {}
        for name in self.filelist:
            self.ips[name] = []

    def read_sni(self, path):
        for filename in os.listdir(path):
            app = ''
            for name in self.filelist:
                if name in filename.lower():
                    app = name
                    break

            with open(path+filename, 'r') as f:
                rows = f.readlines()

            for row in rows:
                if row != '\n':
                    row = row.split(',')
                    if any(x in row[1] for x in self.domains[app]):
                        if row[0] not in self.ips[app]:
                            self.ips[app].append(row[0])

    def filter(self, path):
        try:
            os.mkdir('./pcaps_filtered/')
        except Exception as e:
            pass

        for filename in os.listdir(path):
            flag = False
            app = ''
            for name in self.filelist:
                if name in filename.lower():
                    app = name
                    flag = True
                    break

            if flag:
                try:
                    with open('./pcaps_filtered/'+filename.split('.')[0]+'_filtered.pcap') as f:
                        print(u'>> skipping '+filename.split('.')[0]+'_filtered.pcap')
                        flag = False
                        continue
                except:
                    pass

                print('Processing '+filename+' ...')
                # packets = rdpcap(path+filename)
                pcap_reader = PcapReader(path+filename)
                filtered = []
                for packet in pcap_reader:
                    if packet.haslayer(IP):
                        if packet[IP].src in self.ips[app]:
                            # Anonymize source ip
                            packet[IP].dst = "1.1.1.1"
                            filtered.append(packet)

                        elif packet[IP].dst in self.ips[app]:
                            # Anonymize source ip
                            packet[IP].src = "1.1.1.1"
                            filtered.append(packet)

                pcap_reader.close()
                wrpcap('./pcaps_filtered/'+filename.split('.')[0]+'_filtered.pcap', filtered)
                flag = False


if __name__ == '__main__':
    f = Filter()
    f.read_sni('./result/')
    f.filter('./pcaps')