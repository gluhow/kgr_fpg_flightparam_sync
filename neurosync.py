#!/bin/python3
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import glob
from pathlib import Path
import re
import datetime
import time

def gettimefromfilename(filename):
  date_str=re.search('(\d{1,2})_(\d{1,2})_(\d{4})_(\d{1,2})_(\d{1,2})_(\d{1,2})', filename)
  if date_str:
    day=date_str.group(1)
    month=date_str.group(2)
    year=date_str.group(3)
    H=date_str.group(4)
    M=date_str.group(5)
    S=date_str.group(6)
    return datetime.datetime(int(year), int(month), int(day), int(H), int(M), int(S))
  else: return -1

parser = argparse.ArgumentParser('Синхронизация параметров полета')
parser.add_argument('-F', '--fbk', type=str, default='', help='Каталог с данными от датчиков')
parser.add_argument('-C', '--complex', type=str, default='', help='Каталог с данными от комплекс')
parser.add_argument('-O', '--output', type=str, default='', help='Каталог с выходными данными')
parser.add_argument('-E', '--excel', action="store_true", help='Выгрузить данные в Excel')
parser.add_argument('-G', '--graph', action="store_true", help='Выгрузить график')
args=parser.parse_args()

if args.fbk:
  dir=args.fbk
  for path in Path(dir+'/').glob('*_FPG.csv'):
    FPG_file=path
    end_time=gettimefromfilename(str(FPG_file))
    print('End time=', end_time)
    break

  for path in Path(dir+'/').glob('*_KGR.csv'):
    KGR_file=path
    break

  for path in Path(dir+'/').glob('*_BTN.csv'):
    BTN_file=path
    break

  fpg_data=pd.read_csv(FPG_file, sep=';\t', header=None, names=['time', 'FPG'], engine='python')
  kgr_data=pd.read_csv(KGR_file, sep=';\t', header=None, names=['time', 'KGR'], engine='python').set_index('time')
  btn_data=pd.read_csv(BTN_file, sep=';\t', header=None, names=['time', 'BTN'], engine='python').set_index('time')
  btn_data['BEG']=(~btn_data.BTN.eq(btn_data.BTN.shift())) & (abs(btn_data.BTN)>0.75)
  #
  DATA=fpg_data.join(btn_data, on='time')
  DATA=DATA.join(kgr_data, on='time')
  end_shift=DATA['time'].iloc[-1]
  DATA['localtime']=DATA['time'].apply(lambda t: end_time-datetime.timedelta(seconds=end_shift-t))
  DATA['timestamp']=DATA['localtime'].apply(lambda t: t.timestamp())
  #DATA=DATA.set_index('time')
  print(DATA)
  if args.output and args.excel:
    epath=args.output+'/FBK.xlsx'
    print('Экспорт в', epath)
    DATA.to_excel(epath)
 
if args.complex:
  dir2=args.complex
  if not dir2:
    print('Не задан второй каталог')
    exit(1)
  print(dir2)


  gaze_data=pd.DataFrame()
  for path in glob.iglob(pathname='**/GazeData.txt', root_dir=dir2, recursive = True):
    print('path=', path)
    load_gaze_data=pd.read_csv(dir2+'/'+path, sep='$')
    gaze_data=gaze_data.append(load_gaze_data)

  flight_data=pd.DataFrame()
  for path in glob.iglob(pathname='**/FligthParameters.txt', root_dir=dir2, recursive = True):
    print('path=', path)
    load_flight_data=pd.read_csv(dir2+'/'+path, sep='$', header=None, names=['Freeze', 'Position freeze', 'Roll', 
            'Pitch', 'Angle', 'Heading', 'Altitude', 'Vertical', 'Horizontal',
            'Right Sidestick pitch', 'Right Sidestick roll', 'Reposition', 'WOW_L', 'WOW_R', 'WOW_N', 'SERVER_TIME'], skiprows=1)
    flight_data=flight_data.append(load_flight_data)
  flight_data['timestamp']=flight_data['SERVER_TIME']/1000+3600*3
  print(flight_data)
  if args.output and args.excel:
    epath=args.output+'/complex.xlsx'
    print('Экспорт в', epath)
    flight_data.to_excel(epath)
  #common_data=DATA.set_index('timestamp').join(flight_data, on='timestamp')
  #print(common_data)
  #common_data.plot(y=['FPG', 'KGR', 'Heading'])

if args.output and args.graph:
  ax1 = plt.subplot(311)
  plt.grid(True)

  if args.fbk:
    DATA.plot(y=['FPG', 'KGR'], x='timestamp', ax=ax1)
    DATA=DATA.set_index('timestamp')
    BEG_TIME=DATA.loc[DATA['BEG']].index
    [plt.axvline(_x, linewidth=1, color='g') for _x in BEG_TIME]

  ax2 = plt.subplot(312, sharex=ax1)
  if args.fbk:
    [plt.axvline(_x, linewidth=1, color='g') for _x in BEG_TIME]
  if args.complex:
    flight_data.plot(y=['Vertical', 'Horizontal','WOW_L', 'WOW_R', 'WOW_N'], x='timestamp', ax=ax2)

    ax3 = plt.subplot(313, sharex=ax1)
    if args.fbk:
      [plt.axvline(_x, linewidth=1, color='g') for _x in BEG_TIME]
    flight_data.plot(y=['Altitude'], x='timestamp', ax=ax3)

    #plt.tick_params('x', labelsize=6)
    plt.savefig(args.output+'/plot.png', dpi=300)
    #plt.show()
    exit(0)


    #print('gaze')
    #GAZE_file='/home/greenfil/Эксперимент эмоции/Student 4.3/Attempt 1/0/fe1ef6b8-d98f-437e-8ae2-abfe3948c1d6/GazeData.txt'
    #gaze_data=pd.read_csv(GAZE_file, sep='$').set_index('TIME')
    #print(gaze_data)
    #gaze_data.plot(y=['LPD'])
    #print('DATA_after=',DATA)
