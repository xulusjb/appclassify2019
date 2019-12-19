from tShark import tSharkSniff
import qbittorrentapi
import time
import os
import shutil

# 1. install qBittorrent on Windows
# 2. Enable Windows Internet Information Services (IIS)
# 3. Enable qBittorent webUI. 
#   >On the menu bar, go to Tools > Options qBittorrent WEB UI
#   >In the new window, choose Web UI option
#   >Check the Enable the Web User Interface (Remote control) option
#   >Choose a port (by default 8080)
#   >Set username and password (by default username: admin / password: adminadmin)
#   >Click on Ok to save settings.

class bittorrentClient(object):
    """docstring for bittorrentClient"""
    def __init__(self, url='http://127.0.0.1:8080/'):
        self.USERNAME = 'admin'
        self.PASSWORD = 'adminadmin'
        self.qbt_client = qbittorrentapi.Client(host=url, username=self.USERNAME, password=self.PASSWORD)

        try:
            self.qbt_client.auth_log_in()
        except qbittorrentapi.LoginFailed as e:
            print(e)
        
        print(f'qBittorrent: {self.qbt_client.app.version}')
        print(f'qBittorrent Web API: {self.qbt_client.app.web_api_version}')
        # for k,v in self.qbt_client.app.build_info.items(): print(f'{k}: {v}')

    def get_torrents(self):
        return self.qbt_client.torrents.info()

    def download_from_url(self, url, timeout=60, save_path='./torrents', keep_download_file = False):
        seconds = 0
        wait = True
        try:
            os.mkdir(save_path)
        except Exception as e:
            pass
        
        self.qbt_client.torrents.add(urls=url, save_path=save_path)
        while wait and seconds < timeout:
            time.sleep(1)
            if len(self.qbt_client.torrents.info.resumed()) == 0:
                wait = False
            seconds += 1

        self.qbt_client.torrents.delete(delete_files=True, hashes='all')
        if not keep_download_file:
            shutil.rmtree(save_path)

if __name__ == '__main__':
    sniff = tSharkSniff()
    client = bittorrentClient()
    urls = []   # magnet links of torrents
    # torrent_list = client.get_torrents()
    for url in urls:
        sniff.start(output=output)
        client.download_from_url(urls)
        sniff.stop()