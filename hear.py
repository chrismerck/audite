import numpy as np
import os
import sys
import struct
from scipy import fftpack
from collections import defaultdict
import random
import json

from constants import *
from beep import beep_win
from DTMFdetector import DTMFdetector

TIMEOUT = 5
T_BLOCK = 1 

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

def make_filter(center_freq=1000,bandwidth=None):
  if bandwidth==None:
    bandwidth=center_freq*0.2
  def filter_func(freq):
    ''' triangular filter '''
    if freq < center_freq-bandwidth:
      return 0
    elif freq < center_freq:
      return (freq-(center_freq-bandwidth))/bandwidth
    elif freq < center_freq+bandwidth:
      return ((center_freq+bandwidth)-freq)/bandwidth
    else:
      return 0
  return filter_func

def get_spectrum_x_axis(frame_len, rate):
  return [ 0.5 * i * rate / float(frame_len) for i in range(frame_len)]

T_FRAME = 0.02 #s

def mk_env_filt(n=3):
  return beep_win(t_on=0.075,t_off=0.075,
      n=n,rate=1./T_FRAME,ymin=-1,ymax=1)

if __name__=="__main__":

  filt = None
  es = []
  i_prev = 0

  # filter for beep envelope
  env_filt = mk_env_filt()

  dtmf = DTMFdetector()

  t_total = 0
  while t_total < TIMEOUT:
    samps=T_BLOCK*RATE
    block = read_frame(samps)
    t_total += T_BLOCK

    # break up block into overlapping windowed 'frames'
    # use no overlap so we can see gaps in tone also
    for frame in split_frame(block, int(T_FRAME*RATE), 0): 
      w = window(frame)
      p = periodogram(w)

      print dtmf.in_block(frame)

      # create filter on demand
      if filt==None:
        filt_func = make_filter()
        X = get_spectrum_x_axis(len(p), RATE)
        filt = [ filt_func(x) for x in X ] 

      #print periodogram for debug
      '''for i in range(len(p)):
        print X[i],",",p[i]
      exit()'''

      # compute energy 
      e = np.log(np.sum(np.multiply(filt,p)))
      es.append(e)

    # find beep pattern in energy plot
    i_next = len(es)-len(env_filt)
    assert(i_next>i_prev)
    for i in range(i_prev,i_next):
      Q=pow(np.sum(env_filt*es[i:i+len(env_filt)]),2)
      Q_THRESH = 500
      #print es[i+len(env_filt)-1], ",", Q
      #if Q>Q_THRESH:
      #  print "Heard the beeps!"
      #  sys.exit(0)
    i_prev=i_next

  print "Timeout."
  sys.exit(1)


