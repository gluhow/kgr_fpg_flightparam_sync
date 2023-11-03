#!/bin/python3
import os
import subprocess
for dir in os.listdir('./data'):
  path='./data/'+dir
  if os.path.isdir(path):
    param=['./neurosync.py', '-O',path,'-G','-E']
    FBKpath=path+'/FBK'
    if os.path.isdir(FBKpath):
      param=param+['-F', FBKpath]
    complexPatch=path+'/complex'
    if os.path.isdir(complexPatch):
      param=param+['-C', complexPatch]
    print(param)
    subprocess.run(param,stdout=subprocess.DEVNULL)