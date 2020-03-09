import time
import os
import subprocess
import shlex
import psutil
import sys

class tSharkSniff(object):
    """docstring for tSharkSniff"""
    def __init__(self, interface='enp2s0', files=100):
        self.interface = interface
        self.files = files

    def start(self, cfilter='tcp or udp', output='output.pcap'):
        command = ['dumpcap', \
            # '-P', \
            # Stops after
            '-a', 'files:'+str(self.files), \
            # '-a', 'duration:3600', \
            # '-a', 'packets:10000'

            # Dump to multiple files, switch to the next file after 'filesize' (kb) or 'duration' seconds
            '-b', 'filesize:1024000', \
            # '-b', 'duration:60', \

            # Buffer Size (MB) x 12
            '-B', '12288', \

            '-i', self.interface, \
            '-f', cfilter, \
            '-w', output \
            ]

        self.p = subprocess.Popen(command, preexec_fn=os.setpgrp)
        print("Process spawned with PID: %s" % self.p.pid)
        return self.p

    def check(self):
        return self.p.poll()

    def pause(self):
        self.p.kill()
        time.sleep(10)
        count = len(os.listdir('./result/'))
        self.start(output='./result/NYU', files=self.files-count)

    def stop(self):
        self.p.kill()
        # pgid = os.getpgid(self.p.pid)
        # command = "sudo kill {}".format(pgid)
        # subprocess.check_output(shlex.split(command))

def main():
    sniff = tSharkSniff(interface='enp2s0', files=10000)
    try:
        os.mkdir('./result')
    except Exception as e:
        pass

    sniff.start(output='./result/NYU')

    try:
        while sniff.check() == None:
            if psutil.virtual_memory().percent > 95:
                print('Memory almost full.')
                sniff.pause()

    except KeyboardInterrupt:
        sniff.stop()
        sys.exit()

if __name__ == '__main__':
    main()