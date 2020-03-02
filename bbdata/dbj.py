# -*- coding: utf-8 -*-

import hashlib
from mydict import mydict
import base64
from textwrap import wrap
from libz.peewee import Model, TextField, CharField, IntegerField
import time
import conf


def _mkkv(s):
    a = s.split('/')
    if a[-1] == '':
        a.pop()
    return mydict(zip(a[0::2], a[1::2]))


def hsh(s):
    return base64.b32encode(hashlib.sha256(s).digest())[:11]


def hsh2(s):
    out = base64.urlsafe_b64encode(hashlib.sha256(s).digest())
    return out.replace('-', '').replace('_', '')[:8].ljust(8,'A')


def b64d(s):
    return base64.b64decode(s.replace('-', '+').replace('_', '/'))


def gts():
    return int(time.time())


db = conf.db


class msg(Model):
    mid = CharField(unique=True,default='')
    msgfrom = CharField(index=True,default='')
    msgto = CharField(index=True,default='')
    date = IntegerField(index=True,default=0)
    accepted = IntegerField(index=True,default=0) # время, когда сообщение пришло на станцию
    echoarea = CharField(index=True,default='')
    repto = CharField(index=True,default='')
    topicid = CharField(index=True,default='')
    addr = CharField(default='')
    title = CharField(default='')
    txt = TextField(default='')

    class Meta:
        database = db


def bb_transform(o,sep=1):
    ''' transofm db object to bb msg '''
    repto = '/repto/%s' % o.repto if o.repto else ''
    return 'ii/ok/topicid/%s%s\n%s\n%s\n%s\n%s\n%s\n%s\n\n%s' % (repto, o.topicid, o.echoarea, o.date // sep, o.msgfrom, o.addr, o.msgto, o.title, o.txt)


# echo_cnt = mydict()

def echo_count(ea):
    return msg.select().where(msg.echoarea == ea).count()

def save_msg(jd):
    ''' save bbmsg to db '''
    #print jd
    if not '.' in jd.echoarea:
        return
    msgid = hsh(bb_transform(jd,60))
    if jd.repto:
        obj = msg.get(msg.mid == jd.repto)
        jd.topicid = obj.topicid
    else:
        jd.topicid = msgid
    if '\n@@@@base64@@@@\n' in jd.txt:
        nw = jd.txt.split('\n@@@@base64@@@@\n',1)
        jd.txt = nw[0] + '\n> spoiler!\n' + '\n'.join(wrap(base64.b64encode(nw[1]),50))
    ji = mydict(mid=msgid,**jd)
    msg.save(msg(**ji))


def bb_sendmsg(user, addr, t):
    ''' send msg from site or client '''
    jd = mydict(
        echoarea=t[0],
        txt='\n'.join(t[5:]),
        repto=t[3],
        msgfrom=user,
        addr=addr,
        msgto=t[1],
        title=t[2],
        date=gts(),
        accepted=gts()
    )
    save_msg(jd)


def echolist_pass(kv):
    out = []
    if kv.echolist == 'discover':
        out = [n.echoarea for n in msg.select(msg.echoarea).distinct()]
    elif kv.echolist == 'public':
        out = open('%s/public.txt' % conf.DATA).read().splitlines()
    if kv.ignore:
        ignore = set(kv.ignore.split(':'))
        out = [n for n in out if n not in ignore]
    if kv.addecho:
        for n in kv.addecho.split(':'):
            if n not in out:
                out.append(n)
    if kv.cnt:
        out = [(x,echo_count(x)) for x in out]
    return out


def get_pass(kv):
    out = ''
    if kv.rev:
        order = msg.id
    else:
        order = msg.id.desc()
    cur = msg.select().order_by(order)
    if kv.echo:
        cur = cur.where(msg.echoarea << kv.echo.split(':'))
    if kv.msgs:
        cur = cur.where(msg.mid << kv.msgs.split(':'))
    if kv.afrom:
        cur = cur.where(msg.accepted >= int(kv.afrom))
    if kv.ato:
        cur = cur.where(msg.accepted <= int(kv.ato))
    if kv.dfrom:
        cur = cur.where(msg.date >= int(kv.dfrom))
    if kv.dto:
        cur = cur.where(msg.date <= int(kv.dto))
    if kv.noecho:
        cur = cur.where(msg.echoarea.not_in( kv.noecho.split(':') ))
    if kv.topics:
        cur = cur.where(msg.mid == msg.topicid)
    if kv.topicid:
        print kv.topicid
        cur = cur.where(msg.topicid == kv.topicid)
    if kv.lim or kv.page:
        # add .intrev, for revert object (not request)
        page = int(kv.page) if kv.page else 1
        lim = int(kv.lim) if kv.lim else 100
        cur = cur.paginate(page,lim)
    if kv.fmt == 'noempty':
        out = list(cur)
        return out[0] if out else msg()
    else:
        return cur


def url_req(kv):
    out = []
#    if kv.rev:
#        order = msg.id
#    else:
    order = msg.id.desc()
    if kv.msgs or kv.flatecho:
        cur = msg.select().order_by(order)
    elif kv.withecho:
        cur = msg.select(msg.mid,msg.echoarea).order_by(order)
    else:
        cur = msg.select(msg.mid).order_by(order)
    # preselect^
    if kv.afrom:
        cur = cur.where(msg.accepted >= int(kv.acceptedfrom))
    if kv.ato:
        cur = cur.where(msg.accepted <= int(kv.acceptedto))
    if kv.lim or kv.page:
        # add .intrev, for revert object (not request)
        page = int(kv.page) if kv.page else 1
        lim = int(kv.lim) if kv.lim else 100
        cur = cur.paginate(page,lim)
    # msgs or not msgs? vot v chem vopros
    if kv.flatecho:
        cur = cur.where(msg.echoarea == kv.flatecho).limit(200)
        for n in cur:
            o = bb_transform(n)
            out.append( '== %s ==\n%s\n\n' % (n.mid,o) )
    elif not kv.msgs:
        if kv.echo:
            cur = cur.where(msg.echoarea << kv.echo.split(':'))
        if kv.withecho:
            for n in cur:
                out.append( '%s:%s' % (n.mid,n.echoarea))
        else:
            for n in cur:
                out.append( n.mid )
    else:
        cur = cur.where(msg.mid << kv.msgs.split(':'))
        # dict for order - vnedrit VEZDE!
        dfo = dict()
        for n in cur:
            o = bb_transform(n)
            dfo[n.mid] = o if kv.fmt == 'flat' or kv.fmt == 'flatm' else base64.b64encode(o.encode('utf-8'))
        for sl in kv.msgs.split(':'):
            fmtstr = dfo[sl] if kv.fmt == 'flatm' else '== %s ==\n%s\n\n' % (sl,dfo[sl]) if kv.fmt == 'flat' else  '%s:%s' % (sl, dfo[sl])
            out.append (fmtstr)
    return '\n'.join(out) + '\n'


def point_msg(pauth,tmsg,uu):
    if not uu:
        return False
    msgfrom = uu.uname.encode('utf-8')
    tnew = tmsg.strip().replace('-','+').replace('_','/')
    tlines = base64.b64decode( tnew )
    lines = tlines.splitlines()
    echoarea = lines[0]
    mo = mydict(date=gts(),
                accepted=gts(),
                msgfrom=msgfrom,
                addr='%s,%s' % (conf.STREET, uu.id),
                echoarea=echoarea,
                msgto=lines[1],
                title=lines[2] or '***',
                txt='\n'.join(lines[4:])
                )
    if mo.txt.startswith('@repto:'):
        tmpmsg = mo.txt.splitlines()
        mo.repto = tmpmsg[0][7:]
        mo.repto = mo.repto[:20]
        mo.txt = '\n'.join(tmpmsg[1:])
    save_msg(mo)
    return 'msg ok:'

