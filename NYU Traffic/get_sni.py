import sys, os
from subprocess import Popen
from subprocess import check_output


def main():
    flag = False
    filelist = ['facebook', 'email', 'youtube', 'hangout', 'gmail', 'icq', 'netflix', 'skype', 'spotify', 'vimeo', 'voipbuster']
    try:
        os.mkdir("./result/")
    except Exception as e:
        pass

    for filename in os.listdir('./pcaps'):
        try:
            with open('./result/'+filename.split('.')[0]+'.txt') as f:
                print(u'>> skipping '+filename.split('.')[0]+'.txt')
                flag = False
                continue
        except:
            pass

        print('Processing '+filename+'...')

        cmd = 'tshark -r ./pcaps/'+filename+' \
                -T fields -E separator=\",\" -e ip.dst -e ssl.handshake.extensions_server_name \
                ssl.handshake.extensions_server_name'

        ret = check_output(cmd, shell=True)
        print(ret)
        print()

        with open('./result/'+filename.split('.')[0]+'.txt', 'a') as output:
            output.write(ret.decode("utf-8") )

if __name__ == '__main__':
    main()