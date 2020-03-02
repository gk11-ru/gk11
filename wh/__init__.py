import time
from splitparser import rend
from pager import render_pager

def datef(d,f):
    return time.strftime(f, time.localtime(int(d)))

def dateg(d,f):
    return time.strftime(f, time.gmtime(int(d)))

def ts_get(d,f=None):
    dat, tim = d.split()
    dmy = dat.replace('.','/').replace('-','/').split('/')
    if len(dmy) > 2 and len(dmy[2]) == 2:
        dmy[2] = '20' + dmy[2]
    elif len(dmy) == 2:
        dmy.append( dateg(int(time.time()),'%Y') )
    dat = '/'.join(dmy)
    print dat
    d = dat + ' ' + tim
    return int(time.mktime(time.strptime(d, f or r'%d/%m/%Y %H:%M:%S')))
