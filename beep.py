import numpy as np
import os
import sys
import struct
from scipy import fftpack
from collections import defaultdict
import random
import json

from constants import *

def write_frame(frame,dst=sys.stdout.fileno()):
  os.write(dst,struct.pack('f'*len(frame),*frame))

def beep_win(t_on=0.05,t_off=0.1,n=10,t_fade=None,
    rate=RATE,ymin=0.,ymax=1.):
  if t_fade==None:
    t_fade = 0.1*t_on
  # t_fade takes away from t_on on both sides
  assert(t_on>2*t_fade)
  win = np.concatenate((
      np.linspace(ymin,ymin,num=0.5*t_off*rate),        # off
      np.linspace(ymin,ymax,num=t_fade*rate),           # fade in
      np.linspace(ymax,ymax,num=(t_on-2*t_fade)*rate),  # plateau
      np.linspace(ymax,ymin,num=t_fade*rate),           # fade out
      np.linspace(ymin,ymin,num=0.5*t_off*rate),        # off
      ))
  wins = np.array([])
  for i in range(n):
    wins = np.concatenate((wins,win))
  return wins
 
def beep(f_carrier=1001,vol=0.5,t_on=0.05,t_off=0.1,n=3,t_fade=None):
  """ Return an audio frame with a beep train """
  t_total = n*(t_on+t_off)
  phi = np.linspace(0,2*np.pi*f_carrier*t_total,num=t_total*RATE)
  carrier = np.sin(phi)
  win = beep_win(t_on,t_off,n,t_fade)
  return vol*win*carrier

def dtmf(char,t=0.2,vol=0.8):
  X=[1209.,1336.,1477.,1633.]
  Y=[697.,770.,852.,941.]
  codes={
      '1':(X[0],Y[0]),
      '2':(X[1],Y[0]),
      '3':(X[2],Y[0]),
      'A':(X[3],Y[0]),
      '4':(X[0],Y[1]),
      '5':(X[1],Y[1]),
      '6':(X[2],Y[1]),
      'B':(X[3],Y[1]),
      '7':(X[0],Y[2]),
      '8':(X[1],Y[2]),
      '9':(X[2],Y[2]),
      'C':(X[3],Y[2]),
      '*':(X[0],Y[3]),
      '0':(X[1],Y[3]),
      '#':(X[2],Y[3]),
      'D':(X[3],Y[3]),
      ' ':(0,0),
      }
  if not char in codes:
    raise Exception("Error: DTMF code '%s' not found."%char)
  tone1 = np.sin(np.linspace(0,2*np.pi*codes[char][0]*t,num=t*RATE))
  tone2 = np.sin(np.linspace(0,2*np.pi*codes[char][1]*t,num=t*RATE))
  frame = 0.5*vol*(tone1+tone2)
  w=beep_win(t_on=t,t_off=0,n=1,t_fade=t/100.)
  return np.multiply(w,frame)

if __name__=="__main__":
  if len(sys.argv)>=2:
    code = sys.argv[1]
  else:
    sys.stderr.write("ERROR: No DTMF string given on command line.\n")
    sys.exit(1)
  for c in code:
    write_frame(dtmf(c))
  sys.exit(0)

