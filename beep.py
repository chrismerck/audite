import numpy as np
import os
import sys
import struct
from scipy import fftpack
from collections import defaultdict
import random
import json

RATE = 48000

def write_frame(frame,dst=sys.stdout.fileno()):
  os.write(dst,struct.pack('f'*len(frame),*frame))

def beep(f_carrier=1200,vol=0.5,t_on=0.05,t_off=0.05,n=3,t_fade=None):
  """ Return an audio frame with a beep train """
  if t_fade==None:
    t_fade = 0.1*t_on
  t_total = n*(t_on+t_off)
  phi = np.linspace(0,2*np.pi*f_carrier*t_total,num=t_total*RATE)
  carrier = np.sin(phi)
  # t_fade takes away from t_on on both sides
  assert(t_on>2*t_fade)
  win = np.concatenate((
      np.linspace(0,0,num=0.5*t_off*RATE),        # off
      np.linspace(0,1,num=t_fade*RATE),           # fade in
      np.linspace(1,1,num=(t_on-2*t_fade)*RATE),  # plateau
      np.linspace(1,0,num=t_fade*RATE),           # fade out
      np.linspace(0,0,num=0.5*t_off*RATE),        # off
      ))
  wins = np.array([])
  for i in range(n):
    wins = np.concatenate((wins,win))
  return vol*wins*carrier

if __name__=="__main__":
  write_frame(beep())
