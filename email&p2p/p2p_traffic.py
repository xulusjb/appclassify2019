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
            if len(self.qbt_client.torrents.info.completed()) == 1:
                wait = False
            seconds += 1

        self.qbt_client.torrents.delete(delete_files=True, hashes='all')
        if not keep_download_file:
            shutil.rmtree(save_path)

if __name__ == '__main__':
    sniff = tSharkSniff(interface='WLAN')
    client = bittorrentClient()
    # magnet links of torrents
    urls = ['magnet:?xt=urn:btih:fbdcb0b248c6f2c567e957c664e9123eced7c3ca&dn=Kobe%20Bryant%20The%20Inspirational%20Story%20of%20One%20of%20the%20Greatest%20Basketball%20Players%20of%20All%20Time!&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80%2fannounce&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969%2fannounce&tr=udp%3a%2f%2feddie4.nl%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.to%3a2790%2fannounce&tr=udp%3a%2f%2ftracker.pirateparty.gr%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.com%3a2790%2fannounce&tr=udp%3a%2f%2f9.rarbg.me%3a2730%2fannounce&tr=udp%3a%2f%2fdenis.stalker.upeer.me%3a6969%2fannounce&tr=udp%3a%2f%2fopen.demonii.si%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.zer0day.to%3a1337%2fannounce&tr=udp%3a%2f%2fcoppersurfer.tk%3a6969%2fannounce',
            'magnet:?xt=urn:btih:fe2e5a8e15bb2c6f4d3cb852e1207af65631eab2&dn=Blue%20Moon%20(Jack%20Reacher%2c%20n.%2024)%20by%20Lee%20Child%20EPUB&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80&tr=udp%3a%2f%2fopen.demonii.com%3a1337&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969&tr=udp%3a%2f%2fexodus.desync.com%3a6969',
            'magnet:?xt=urn:btih:99cbaf52fc8a77b057c4552ab0028293fe6a7420&dn=Passive%20Income%2030%20Strategies%20and%20Ideas%20To%20Start%20an%20Online%20Business%20and%20Acquiring%20Financial%20Freedom%20(2016)%20%5bWWRG%5d&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80&tr=udp%3a%2f%2fopen.demonii.com%3a1337&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969&tr=udp%3a%2f%2fexodus.desync.com%3a6969',
            'magnet:?xt=urn:btih:01c227c8c9aac311f9365b163ea94708c27a7db4&dn=The%20Subtle%20Art%20of%20Not%20Giving%20a%20Fck%20-%20A%20Counterintuitive%20Approach%20to%20Living%20a%20Good%20Life%20(2016)%20(Epub)%20Gooner&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80&tr=udp%3a%2f%2fopen.demonii.com%3a1337&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969&tr=udp%3a%2f%2fexodus.desync.com%3a6969',
            'magnet:?xt=urn:btih:7fc834649fc60d706f6d08376e11d76b78623825&dn=Brain%20Training%20-%20How%20To%20Learn%20and%20Remember%20Everything&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80&tr=udp%3a%2f%2fopen.demonii.com%3a1337&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969&tr=udp%3a%2f%2fexodus.desync.com%3a6969']
    # urls = ['magnet:?xt=urn:btih:fbdcb0b248c6f2c567e957c664e9123eced7c3ca&dn=Kobe%20Bryant%20The%20Inspirational%20Story%20of%20One%20of%20the%20Greatest%20Basketball%20Players%20of%20All%20Time!&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80%2fannounce&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969%2fannounce&tr=udp%3a%2f%2feddie4.nl%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.to%3a2790%2fannounce&tr=udp%3a%2f%2ftracker.pirateparty.gr%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.com%3a2790%2fannounce&tr=udp%3a%2f%2f9.rarbg.me%3a2730%2fannounce&tr=udp%3a%2f%2fdenis.stalker.upeer.me%3a6969%2fannounce&tr=udp%3a%2f%2fopen.demonii.si%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.zer0day.to%3a1337%2fannounce&tr=udp%3a%2f%2fcoppersurfer.tk%3a6969%2fannounce']    
    # torrent_list = client.get_torrents()
    count = 0
    while count < 50:
        for url in urls:
            print(count)
            sniff.start(output='./result/vpn_p2p/vpn_p2p_'+str(int(time.time()))+'.pcap')
            time.sleep(3)
            client.download_from_url(url)
            time.sleep(5)
            sniff.stop()
            count += 1