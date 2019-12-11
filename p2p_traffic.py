from qbittorrent import Client
from tShark import tSharkSniff

class bittorrentClient(object):
    """docstring for bittorrentClient"""
    def __init__(self):
        self.USERNAME = 'xxx'
        self.PASSWORD = 'xxx'

    def download(self, link):
        qb = Client('http://127.0.0.1:8080/')

        qb.login(self.USERNAME, self.PASSWORD)

        result = qb.download_from_link(link)
        return result


if __name__ == '__main__':
    sniff = tSharkSniff()
    client = bittorrentClient()
    linkes = []
    for link in links:
        sniff.start(output=output)
        client.download(link):
        sniff.stop()