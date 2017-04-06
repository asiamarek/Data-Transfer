#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import sys
import wave

import pulseaudio as pa
import numpy as np

from bitarray import bitarray
import binascii

t=int(sys.argv[1])
f0=int(sys.argv[2])
f1=int(sys.argv[3])


def listen(howLong):
    if howLong==0:
        return 0,0
	nframes = int(float(howLong) * recorder.rate)
   	data = recorder.read(nframes)
    if data.size == 0:
        return 0,0
   	A=np.fft.fft(data)
   	A=A[0:A.size/2]
   	A=np.abs(A)
   	if len(data)<nframes:
		return 0,0
	x=np.argmax(A)

    return x/float(howLong), A[x]

dict5to4={"11110":"0000","01001":"0001","10100":"0010","10101":"0011","01010":"0100","01011":"0101","01110":"0110","01111":"0111","10010":"1000","10011":"1001","10110":"1010","10111":"1011","11010":"1100","11011":"1101","11100":"1110","11101":"1111"}

def decode(C):

	if (len(C))%5 != 0:
        if(len(C))%5-1 == 0:
            C=C[:len(C)]
        else:
		    return
	if len(C)<181 :
		return
	newString=""
	C2='1'+C
	for x in range (0,len(C)):
		if C2[x+1]=="0":
			newString+=C2[x]
		else:
			if C2[x]=="0":
				newString+="1"
			else:
				newString+="0"

	C=newString
	newString=""
	for x in range(0,int(len(C)/5)):
		fragment=C[5*x:5*(x+1)]
		if fragment not in dict5to4:
			return
		newString+=dict5to4[fragment]
	C=newString

	recv=int(C[0:48],2)
	sendr=int(C[48:96],2)
	ln=int(C[96:112],2)

	data=C[0:112+8*ln]
	T=bitarray()
	for x in range(0,len(data)):
		if(data[x]=='0'):
			T.append(0)
		else:
			T.append(1)

	crc=binascii.crc32(T.tobytes())&0xffffffff
	data = "{0:b}".format(crc)

	zeroes=32-len(data)
	if data != C[112+8*ln+zeroes:len(C)] :
		return

	msg=''

	for x in range (1,ln+1):
		temp=C[112+8*(x-1):(112+8*x)]
		data=int(temp,2)
		msg+=chr(data)

	print('{} {} {}'.format(sendr,recv,msg))


(nchannels, sampwidth, sampformat, framerate) = (1, 2, pa.SAMPLE_S16LE, 44100)
with pa.simple.open(direction=pa.STREAM_RECORD, format=sampformat, rate=framerate, channels=nchannels) as recorder:

	while True:
		bestTry=0
		bestTryNr=0
		again=0
		for x in range(0,5):
			anotherTry, zmienna=listen(1/float(t))
            if abs(anotherTry-f0)>10 and abs(anotherTry-f1)>10 and x==0:
                again=1
			    break

            if zmienna > bestTry :
				bestTry=zmienna
				bestTryNr=x
			sth,sth2=listen(1/float(5*t))
        if again==1:
            continue
		msg=''
		listen(float(bestTryNr)/float(5*t))
		while True:

		    a,sth2=listen(1/float(t))
            if abs(a-f0)>20 and abs(a-f1)>20: 
                break

			if abs(a-f0) < abs(a-f1) :
				msg+="0"
			else:
				msg+="1"
		i=1
		while not (msg[i-1]=='1' and msg[i]=='1'):
			if i>=len(msg):
				break
			i+=1
		decode(msg[i+1:])
		break
