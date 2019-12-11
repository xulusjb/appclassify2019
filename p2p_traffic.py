rom qbittorrent import Client

qb = Client('http://127.0.0.1:8080/')

qb.login('admin', 'your-secret-password')
# not required when 'Bypass from localhost' setting is active.
# defaults to admin:admin.
# to use defaults, just do qb.login()

torrents = qb.torrents()

for torrent in torrents:
    print torrent['name']

qb.torrents(filter='downloading', category='my category')
# This will return all torrents which are currently
# downloading and are labeled as ``my category``.

qb.torrents(filter='paused', sort='ratio')
# This will return all paused torrents sorted by their Leech:Seed ratio.


magnet_link = "magnet:?xt=urn:btih:e334ab9ddd91c10938a7....."
qb.download_from_link(magnet_link)

# No matter the link is correct or not,
# method will always return empty JSON object.

link_list = [link1, link2, link3]
qb.download_from_link(link_list)