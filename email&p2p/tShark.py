import subprocess
import time

class tSharkSniff(object):
    """docstring for tSharkSniff"""
    def __init__(self, interface='Ethernet', packet_num=500):
        self.interface = interface
        self.packet_num = packet_num

    def start(self, output='output.pcap'):
        command = ['C:\\Program Files\\Wireshark\\tshark.exe', \
            '-P', \
            #'-a', 'durantion:100', \
            #'-c', str(self.packet_num), \
            '-i', self.interface, \
            #'-f', cfilter, \
            '-w', output]

        self.p = subprocess.Popen(command)

    def stop(self):
        self.p.kill()

if __name__ == '__main__':
    sniff = tSharkSniff(interface='WLAN')
    sniff.start(output='./result/email/email_'+str(int(time.time()))+'.pcap')
    # client.send_mail(name, email, message_template)
    time.sleep(10)
    sniff.stop()