import sys, os
from subprocess import Popen
from subprocess import check_output


def main():
    flag = False
    ignore = ['sftp', 'ftps', 'scp']
    filelist = ['facebook', 'email', 'youtube', 'hangout', 'gmail', 'icq', 'netflix', 'skype', 'spotify', 'vimeo', 'voipbuster']
    for filename in os.listdir('F:\\pcaps'):
        for i in filelist:
            if i in filename.lower():
                flag = True
                break
        try:
            with open('./result/'+filename.split('.')[0]+'.txt') as f:
                print(u'>> skipping '+filename.split('.')[0]+'.txt')
                flag = False
                continue
        except:
            pass

        if flag:
            print('Processing '+filename+'...')

            cmd = '\"C:\\Program Files\\Wireshark\\tshark.exe\" -r F:\\pcaps\\'+filename+' \
                    -T fields -E separator=\",\" -e ip.dst -e tls.handshake.extensions_server_name \
                    tls.handshake.extensions_server_name'

            ret = check_output(cmd, shell=True)
            print(ret)

            with open('./result/'+filename.split('.')[0]+'.txt', 'a') as output:
                output.write(ret.decode("utf-8") )

            flag = False

if __name__ == '__main__':
    main()