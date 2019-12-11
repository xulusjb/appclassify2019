class tSharkSniff(object):
    """docstring for tSharkSniff"""
    def __init__(self, interface='Ethernet', packet_num=500):
        self.interface = interface
        self.packet_num = packet_num

    def start(self, cfilter='', output='output.pcap'):
        command = ['C:\\Program Files\\Wireshark\\dumpcap.exe', \
            '-P', \
            #'-a', 'durantion:100', \
            #'-c', str(self.packet_num), \
            '-i', self.interface, \
            #'-f', cfilter, \
            '-w', output]

        self.p = subprocess.Popen(command)

    def stop(self):
        self.p.kill()