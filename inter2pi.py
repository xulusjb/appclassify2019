import pandas as pd
import numpy as np
import os

def main():
    http2_category = ['a','f','i','r','s','so','t','w']
    for cate in http2_category:
        print(cate)
        file_list = os.listdir('./')

        payload = np.genfromtxt(cate+"_p.txt", delimiter=' ', dtype=int)
        interval = np.genfromtxt(cate+"_inter.txt", delimiter=' ', usecols=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18))
        interval = np.around(interval.astype(int))

        output = np.append(interval, payload, axis=1)

        print(output.shape)

        np.savetxt('./feature/'+cate+"_pi.txt", output, delimiter=' ', fmt='%d')


if __name__ == '__main__':
    main()
    
'''
t = ['g','gc','gd','gdr','gf','tb','tr','y']
existdic = {}



for app in t:
	print(app)
	pix = open(app+"_pix.txt","w")
	px = open(app+"_px.txt","w")
	ix = open(app+"_ix.txt","w")
	for i in range(1,6):
		pfile = "/".join([".",str(i),app+"_p.txt"])
		ifile = "/".join([".",str(i),app+"_inter.txt"])
		with open(pfile,"r") as pfi:
			with open(ifile, "r") as ifi:
				linp = pfi.readline().strip()
				while linp:
					lini = ifi.readline().strip()
					numlist = [int(i) for i in lini.split(" ")]
					needed = numlist[0:19]
					lini = " ".join([str(i) for i in needed])
					fingerprint = lini+" "+linp
					if fingerprint not in existdic:
						pix.write(lini+" "+linp+"\n")
						px.write(linp+"\n")
						ix.write(lini+"\n")
						existdic.update({fingerprint:1})
					linp = pfi.readline().strip()
	pix.close()
	px.close()
	ix.close()
'''
