# -*- coding: utf-8 -*-

from dbj import gts, save_msg, echolist_pass, get_pass, url_req, bb_sendmsg
from mydict import mydict, jout
import conf

def _mkkv(s):
    a = s.split('/')
    if a[-1] == '':
        a.pop()
    return mydict(zip(a[0::2], a[1::2]))


def app_rq(s, data=mydict(), rf=get_pass):
    ''' application request, data = post data '''
    kv = _mkkv(s)
    if kv.echolist:
        return echolist_pass(kv)
    elif kv.point:
        ea = data.ea or kv.ea or 'me'
        msgto = data.msgto or kv.msgto or 'All'
        title = data.title or kv.title or '***'
        repto = data.repto or kv.repto
        txt = data.outtxt or kv.txt
        t = (ea,msgto,title,repto,txt.replace('\r\n','\n'))
        tb = '%s\n%s\n%s\n%s\n\n%s' % t
        bb_sendmsg(data.uname, data.addr, tb.splitlines())
        return 'msg ok:'
    else:
        return rf(kv)

def app_rq_txt(s, data=mydict()):
    ''' convert db to plain text '''
    kv = _mkkv(s)
    out = '%s\n' % gts() if kv.appendts else ''
    outrq = app_rq(s,data,url_req)
    if kv.echolist:
        if kv.cnt:
            out += '\n'.join(['%s:%s:%s' % (n[0], n[1], n[0]) for n in outrq]) + '\n'
        else:
            out += '\n'.join(outrq) + '\n'
    else:
            out += outrq
    if kv.endkey:
        out += '\n%s' % kv.endkey
    return out
