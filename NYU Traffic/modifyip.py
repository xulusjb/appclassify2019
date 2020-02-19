# use scapy to modify ip: https://stackoverflow.com/questions/8726881/sending-packets-from-pcap-with-changed-src-dst-in-scapy
# use scapy to save pcap file: https://stackoverflow.com/questions/33740583/writing-to-a-pcap-with-scapy
from scapy.all import *
from scapy.utils import rdpcap

def write(pkt):
    wrpcap('filtered.pcap', pkt, append=True)

pkts=rdpcap("r_1572867748.pcap", 10)  # could be used like this rdpcap("filename",500) fetches first 500 pkts
for pkt in pkts:
    print(pkt[IP].src)
    pkt[IP].src = "1.1.1.1"
    print(pkt[IP].src)
    write(pkt)
    pass
