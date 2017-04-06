#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

from bitarray import bitarray
import sys
import binascii
import wave
import pulseaudio as pa
import numpy as np


dict4to5={"0000":"11110","0001":"01001","0010":"10100","0011":"10101","0100":"01010","0101":"01011","0110":"01110","0111":"01111","1000":"10010","1001":"10011","1010":"10110","1011":"10111","1100":"11010","1101":"11011","1110":"11100","1111":"11101"}

def code(A,B,M):

	T=bitarray()

	data = "{0:b}".format(int(B))
	for x in range(0,48-len(data)):
		T.append(0)
	for x in range(0,len(data)):
		if(data[x]=='0'):
			T.append(0)
		else:
			T.append(1)

	data = "{0:b}".format(int(A))
	for x in range(0,48-len(data)):
		T.append(0)
	for x in range(0,len(data)):
		if(data[x]=='0'):
			T.append(0)
		else:
			T.append(1)

	data = "{0:b}".format(len(M)-1)
	for x in range(0,16-len(data)):
		T.append(0)
	for x in range(0,len(data)):
		if(data[x]=='0'):
			T.append(0)
		else:
			T.append(1)

	for x in range(0, len(M)-1):
		data="{0:b}".format(ord(M[x]))
		for x in range(0,8-len(data)):
			T.append(0)
		for x in range(0,len(data)):
			if(data[x]=='0'):
				T.append(0)
			else:
				T.append(1)

	crc=binascii.crc32(T.tobytes())&0xffffffff
	data = "{0:b}".format(crc)
	for x in range(0,32-len(data)):
		T.append(0)
	for x in range(0,len(data)):
		if(data[x]=='0'):
			T.append(0)
		else:
			T.append(1)

	oldString=T.to01()
	newString=""
	for x in range(0, int((len(oldString))/4)):
		fragment=oldString[4*x:4*(x+1)]
		newString+=dict4to5[fragment]

	finString=""
	for x in range(0, 7):
		finString+="10101010"
	finString+="10101011"
	for x in range (0, len(newString)):
		if newString[x]==finString[x+63]:
			finString+="0"
		else:
			finString+="1"
	return finString



def play(frequency,howLong):

	x=44100/frequency
	L=[]
	for i in range(44100*howLong):
	      L.append(np.sin(i*2*np.pi/x)*23000)
	with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as player :
	      player.write(L)
	      player.drain()



tm=int(sys.argv[1])
f0=int(sys.argv[2])
f1=int(sys.argv[3])

for line in sys.stdin:
	i=0
	while line[i]!=' ':
		i+=1
	i2=i+1
	while line[i2]!=' ':
		i2+=1
	msg=code(line[0:i],line[i+1:i2],line[i2+1:])

	for x in range (0,len(msg)):
		if msg[x] == '0':
			play(f0,tm)
		else:
			play(f1,tm)
