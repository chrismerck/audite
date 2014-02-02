import numpy as np
import os
import sys
import struct
import string

from constants import *
from beep import beep_win
from DTMFdetector import DTMFdetector

TIMEOUT = 5 # default
T_BLOCK = 0.5

def read_frame(n=None,src=sys.stdin):
  if not n:
    s = src.read()
    n = len(s)/4
  else:
    s = ''
    while len(s) < 4*n:
      s += src.read(4*n-len(s))
  return struct.unpack('f'*n, s)

def window(frame):
  w = np.hanning(len(frame))
  return np.multiply(w,frame)

def periodogram(frame):
  return (np.abs(np.fft.rfft(frame))**2)/float(len(frame))

def split_frame(frame, nsamp, overlap):
  i = 0
  while True:
    head = i*(nsamp - overlap)
    if (head+nsamp)>len(frame):
      return # truncate last subframe
    yield frame[head:head+nsamp]
    i += 1

def get_spectrum_x_axis(frame_len, rate):
  return [ 0.5 * i * rate / float(frame_len) for i in range(frame_len)]

T_FRAME = 0.02 #s

def mk_env_filt(n=3):
  return beep_win(t_on=0.075,t_off=0.075,
      n=n,rate=1./T_FRAME,ymin=-1,ymax=1)

if __name__=="__main__":

  if len(sys.argv)==1:
    target_code = None
  else:
    target_code = sys.argv[1]

  if not target_code or 'h' in target_code or '?' in target_code:
    sys.stderr.write("Usage: hear [ - | <code> ]\n")
    sys.stderr.write(" - = listen and return recognized code. \n")
    sys.stderr.write(" <code> = non-repeating DTMF string to listen for \n")
    sys.exit(1)

  if 'TIMEOUT' in os.environ:
    try:
      TIMEOUT = float(os.environ['TIMEOUT'])
      sys.stderr.write("TIMEOUT=%1.2fs\n"%TIMEOUT)
    except:
      raise Exception("Error processing timeout env var: '%s'"%
          os.environ['TIMEOUT'])

  dtmf = DTMFdetector()

  t_total = 0
  while t_total < TIMEOUT:
    samps=int(T_BLOCK*RATE)
    block = read_frame(samps)
    t_total += T_BLOCK

    # break up block into overlapping windowed 'frames'
    # use no overlap so we can see gaps in tone also
    for frame in split_frame(block, int(T_FRAME*RATE), 0): 
      w = window(frame)
      #p = periodogram(w)

      recog_code = dtmf.in_block(frame)
      if target_code:
        if string.find(recog_code,target_code)>=0:
          print "Got target code!"
          sys.exit(0)

  if target_code:
    print "Timeout."
    sys.exit(1)
  else:
    if recog_code != '':
      print recog_code
      sys.exit(0)
    else:
      print "Timeout."
      sys.exit(1)

