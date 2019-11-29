import selenium, time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import subprocess
import random

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

# chrome_options = Options()
# chrome_options.add_argument("--enable-quic --quic-version=h3-23")
# driver = webdriver.Chrome(options=chrome_options)

# driver = webdriver.Chrome()

sniff = tSharkSniff()
with open ("wordlist_top_noun.txt","r") as rfile:
	s = rfile.read()
verblist = s.split("\n")
''' 
#  for the 8 http2 pages 
http2_addr_dic = {"r":"https://www.reddit.com/search/?q={0}",
                             "t":"https://twitter.com/hashtag/{0}",
                             "s":"https://open.spotify.com/search/{0}",
                             "f":"https://www.facebook.com/public/{0}",
                             "i":"https://www.instagram.com/explore/tags/{0}",
                             "w":"https://en.wikipedia.org/w/index.php?search={0}",
                             "a":"https://www.amazon.com/s?k={0}",
                             "so":"https://stackoverflow.com/search?q={0}"}  #stackoverflow

for k,v in http2_addr_dic.items():  # create directory
	if not os.path.exists(k):
		os.makedirs(k)
    
for i in verblist:
	for k,v in http2_addr_dic.items():
		output = k + '\\\\' +k+'_'+str(int(time.time()))+'.pcap'
		subprocess.call('ipconfig /flushdns')

		sniff.start(output=output)

		chrome_options = Options()
		#chrome_options.add_argument("--enable-quic --quic-version=h3-23")
		chrome_options.add_argument("--incognito")
		driver = webdriver.Chrome(options=chrome_options)

		driver.get(v.format(i))
		#time.sleep(2)

		driver.close()
		sniff.stop()
'''


# for the 8 http3 pages
http3_addr_dic = {"g":"https://www.google.com/search?q={0}&sourceid=chrome&ie=UTF-8",
                             "y":"https://www.youtube.com/results?search_query={0}",
                             "tb":"https://www.tumblr.com/search/{0}",
                             "tr":"https://translate.google.com/?hl=zh-CN#view=home&op=translate&sl=auto&tl=zh-CN&text={0}" ,
                             "gf": ["https://www.google.com/flights?hl=en#flt=/m/02_286.LAX.2019-11-20*LAX./m/02_286.2019-11-24;c:USD;e:1;sd:1;t:f", "https://www.google.com/flights?hl=en#flt=SEA.LAS.2019-11-20*LAS.SEA.2019-11-24;c:USD;e:1;sd:1;t:f", "https://www.google.com/flights?hl=en#flt=/m/04jpl./m/0rh6k.2019-11-20*/m/0rh6k./m/04jpl.2019-11-24;c:USD;e:1;sd:1;t:f", "https://www.google.com/flights?hl=en#flt=/m/04jpl./m/0156q.2019-11-20*/m/0156q./m/04jpl.2019-11-24;c:USD;e:1;sd:1;t:f", "https://www.google.com/flights?hl=en#flt=ATL./m/04jpl.2019-11-20*/m/04jpl.ATL.2019-11-24;c:USD;e:1;sd:1;t:f", "https://www.google.com/flights?hl=en#flt=ATL./m/02_286.2019-11-20*/m/02_286.ATL.2019-11-24;c:USD;e:1;sd:1;t:f"],
                             "gc": ["https://calendar.google.com/calendar/embed?src=bmJhXzFfJTQxdGxhbnRhKyU0OGF3a3Mjc3BvcnRzQGdyb3VwLnYuY2FsZW5kYXIuZ29vZ2xlLmNvbQ", "https://calendar.google.com/calendar/embed?src=bmJhXzJfJTQyb3N0b24rJTQzZWx0aWNzI3Nwb3J0c0Bncm91cC52LmNhbGVuZGFyLmdvb2dsZS5jb20","https://calendar.google.com/calendar/embed?src=bmJhXzE3XyU0MnJvb2tseW4rJTRlZXRzI3Nwb3J0c0Bncm91cC52LmNhbGVuZGFyLmdvb2dsZS5jb20","https://calendar.google.com/calendar/embed?src=bmJhXzMwXyU0M2hhcmxvdHRlKyU0OG9ybmV0cyNzcG9ydHNAZ3JvdXAudi5jYWxlbmRhci5nb29nbGUuY29t","https://calendar.google.com/calendar/embed?src=bmJhXzRfJTQzaGljYWdvKyU0MnVsbHMjc3BvcnRzQGdyb3VwLnYuY2FsZW5kYXIuZ29vZ2xlLmNvbQ","https://calendar.google.com/calendar/embed?src=bmJhXzlfJTQ3b2xkZW4rJTUzdGF0ZSslNTdhcnJpb3JzI3Nwb3J0c0Bncm91cC52LmNhbGVuZGFyLmdvb2dsZS5jb20"],
                             "gdr": ["https://drive.google.com/drive/folders/1Ab-tWydPWLukGjsQ-sQpGZshiHJWYPkQ?usp=sharing","https://drive.google.com/drive/folders/17zUO8F6IgVc3g-kpfI4psFuHm0vS5BT4?usp=sharing","https://drive.google.com/drive/folders/1iExly-H4fWBdqxV3dX8wNjxzNq-XDJAg?usp=sharing","https://drive.google.com/drive/folders/1SE8lK6_JJq8i6AqBMKz191QUJhDyamnz?usp=sharing","https://drive.google.com/drive/folders/1J863GK-uOfO-a4m9mwBzWkMAJjg24zng?usp=sharing","https://drive.google.com/drive/folders/1NdwXUVLnP_Aiyx7HzcGw-bM8CtTk4TX_?usp=sharing"],
                             "gd":["https://docs.google.com/document/d/1d48-XWHE0W4n1756b47es6ZFN2Ry6L9Se-9E8lu6uC0/edit?usp=sharing","https://docs.google.com/document/d/1As2--Inp_nGIb9TFzsbRtDfD1yqhuXpao_XsYvvQBGo/edit?usp=sharing","https://docs.google.com/document/d/1Pwox7J4hBg68HeelDJcT0h3U8-0N8ZPnOeqRyZfq1JQ/edit?usp=sharing","https://docs.google.com/document/d/1_Q7-E6v0UmSD7M_VBzGQqsaFATDNS24ZXgvCXewrtoY/edit?usp=sharing","https://docs.google.com/document/d/1t_99nK_7S9cs_YvS3P1iBJUkpFSIqsiXytBqxYJrlzY/edit?usp=sharing","https://docs.google.com/document/d/1FRiDUwQpoA-U9F85I6pxiGBqzj4RmI4PAOl8uz07foU/edit?usp=sharing"]} 
for k,v in http3_addr_dic.items():  # create directory
	if not os.path.exists(k):
		os.makedirs(k)
    
for i in verblist:
	for k,v in http3_addr_dic.items():
		output = k + '\\\\' +k+'_'+str(int(time.time()))+'.pcap'
		subprocess.call('ipconfig /flushdns')

		sniff.start(output=output)

		chrome_options = Options()
		chrome_options.add_argument("--enable-quic --quic-version=h3-23")
		chrome_options.add_argument("--incognito")
		driver = webdriver.Chrome(options=chrome_options)
		
		if k in ["g","y", "tb", "tr"]:
			driver.get(v.format(i))
		else:
			driver.get(v[random.randint(0,5)])
		#time.sleep(2)

		driver.close()
		sniff.stop()
		
