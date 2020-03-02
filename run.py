# -*- coding: utf-8 -*-

import os
#os.environ['TZ'] = 'Asia/Vladivostok'

from libz.bottle import Bottle, static_file, request, response, template, redirect, SimpleTemplate, abort
from bbdata import app_rq, app_rq_txt, mydict, jout, dbj
from libz.peewee import fn
import userbb
import conf
import wh

bosfor = Bottle()
SimpleTemplate.defaults['request'] = request


def get_u():
    return userbb.check_auth(request.cookies.uhash)


@bosfor.route('/')
def bb_index():
    return template('tpl/index.html', u=get_u())


@bosfor.route('/bb/<bb:path>')
@bosfor.post('/bb/<bb:path>')
def bb_api(bb):
    response.set_header('content-type', 'text/plain; charset=utf-8')
    return app_rq_txt(bb, request.forms)

@bosfor.route('/topic/<tid>')
def show_topic(tid):
    msgs = []
    lrq = app_rq('topicid/%s/rev/1' % tid)
    lst = mydict()
    deftitle =  ''
    for n in lrq:
        lst[n.mid] = mydict(n._data)
        msgs.append(n.mid)
        deftitle = n.title if not deftitle else deftitle
    return template('tpl/msg.html', msgs=':'.join(msgs), lst=lst, u=get_u(), deftitle=u'Topic: %s' % deftitle)


@bosfor.route('/del/<mid>')
def del_mid(mid):
    if request.query.ok == 'ok':
        open('%s/blacklist.txt' % conf.DATA,'a').write(mid + '\n')
        dbj.msg.delete().where(dbj.msg.mid == mid).execute()
        return 'ok tak ok. msgid %s blacklisted' % mid
    else:
        return 'delete msgid %s? <a href="/del/%s?ok=ok">ok</a>' % (mid,mid)


@bosfor.route(['/l/<ea>', '/\:<ea>', '/l/<ea>/<opts>'])
def show_echoarea(ea, opts=''):
    if not '.' in ea:
        ea += '.11'
    opts = opts.split(',') + ['', '', '']
    lim, page, rev = '/lim/100', '', ''
    pg = 1
    if opts[0]:
        page = '/page/%s' % opts[0]
        pg = int(opts[0])
    if opts[1]:
        lim = '/lim/%s' % opts[1]
    if opts[2] == 'rev':
        rev = '/rev/1'
    cnt = app_rq('echolist/none/addecho/%s/cnt/1' % ea)[0][1]
    msgs = app_rq('echo/%s%s%s%s' % (ea, lim, page, rev))
    if opts[2] == 'intrev':
        msgdict = []
        for n in msgs:
            msgdict.append(mydict(n._data))
        msgs = msgdict[::-1]
    return template('tpl/echoarea.html', msgs=msgs, ea=ea, opts=opts, u=get_u(), cnt=cnt, page=pg)


@bosfor.route('/reply/<ea>/<repto>')
def reply_to(ea, repto):
    u = get_u()
    if not u:
        redirect('/user/me?redir=/reply/%s/%s' % (ea, repto))
    rep = repto if repto != '-' else ''
    if rep:
        # fix msgs// !
        rmsg = app_rq('msgs/%s/fmt/noempty' % rep)
    else:
        rmsg = mydict()
    return template('tpl/mform.html', rmsg=rmsg, ea=ea, repto=rep, u=u, zo=request.query.tn)


@bosfor.route('/q/<msgs:path>')
def show_msgid(msgs):
    msgs = msgs.replace('/',':')
    lrq = app_rq('msgs/%s' % msgs)
    lst = mydict()
    for n in lrq:
        lst[n.mid] = mydict(n._data)
    return template('tpl/msg.html', msgs=msgs, lst=lst, u=get_u())


@bosfor.post('/a/savemsg/<ea>')
def post_user(ea):
    if request.forms.outtxt:
        data = mydict(request.forms)
        uu = userbb.check_auth(data.uhash)
        if uu:
            data.update(uname=uu.uname.encode('utf-8'),addr='%s,%s' % (conf.STREET, uu.id))
        else:
            return 'no hash - no msg'
        app_rq('point/user/ea/%s' % ea, data)
    redirect(request.forms.beback or '/:%s' % ea)



@bosfor.route('/user/<umod>')
@bosfor.post('/user/<umod>')
def user_module(umod):
    out = userbb.uweb(umod, request.params, request.cookies)
    if 'cookie' in out and 'redir' in out:
        for k, v in out.cookie.items():
            response.set_cookie(k, v, path='/', max_age=7776000)
            return ('''<html><head>
                    <meta http-equiv="refresh" content="0; %s" />
                    </head><body></body></html>''' % out.redir)
    elif 'redir' in out:
        redirect(out.redir)
    elif 'txt' in out:
        request.content_type = 'text/plain; charset=utf-8'
        return out.txt
    else:
        if 'cookie' in out:
            for k, v in out.cookie.items():
                response.set_cookie(k, v, path='/', max_age=7776000)
        return out.html


@bosfor.route('/rss/<echo>')
@bosfor.route('/rss/<echo>/<num:int>')
def rss_echo(echo,num=50):
    response.set_header('content-type','application/rss+xml; charset=utf-8')
    return userbb.gen_rss(echo, num)


@bosfor.route('/for/<carbon:path>')
def show_carbon(carbon):
    lrq = dbj.msg.select().order_by(dbj.msg.accepted.desc()).where(dbj.msg.msgto == carbon).limit(50)
    cbid, lst = [], mydict()
    for n in lrq:
        lst[n.mid] = mydict(n._data)
        cbid.append(n.mid)
    return template('tpl/msg.html', msgs=':'.join(cbid), lst=lst, deftitle=carbon, u=get_u())


@bosfor.route('/rssfor/<carbon:path>')
def rss_for_carbon(carbon):
    response.set_header('content-type','application/rss+xml; charset=utf-8')
    return userbb.rss_carbon(carbon)


@bosfor.route('/query')
def show_rq():
    rq=request.query
    cur = []
    if rq:
        cur=dbj.msg().select()
        if rq.dfrom:
            cur = cur.where(dbj.msg.date >= wh.ts_get(rq.dfrom + ' 00:00:00'))
        if rq.dto:
            cur = cur.where(dbj.msg.date <= wh.ts_get(rq.dto + ' 23:59:59'))
        if rq.msgfrom:
            cur = cur.where(dbj.msg.msgfrom == rq.msgfrom)
        if rq.msgto:
            cur = cur.where(dbj.msg.msgto == rq.msgto)
        if rq.ea:
            cur = cur.where(dbj.msg.echoarea << rq.ea.split())
        cur=cur.limit(400)
    return template('tpl/query.html', lst=cur, cnt=cur.count() if cur else 0,rq=rq)


@bosfor.route('/authors')
def show_authors():
    query = dbj.msg.select(dbj.msg.msgfrom,fn.COUNT(dbj.msg.msgfrom).alias('cnt')).group_by(dbj.msg.msgfrom).order_by(fn.COUNT(dbj.msg.msgfrom).desc())
    return template('tpl/authors.html',query=query)


@bosfor.route('/litelist')
@bosfor.route('/lite/auth/<authstr>')
def lite_list(authstr=None):
    if authstr:
        response.set_cookie('uhash', authstr, path='/', max_age=7776000)
    return template('tpl/litelist.html', elist=app_rq('echolist/public'))



@bosfor.route('/lite/<ea>')
@bosfor.route('/lite/reply/<ea>/<mid>')
def show_lite(ea,mid=''):
    if mid:
        rmsg = app_rq('msgs/%s/fmt/noempty' % mid)
    else:
        rmsg = mydict()
    msgs = app_rq('echo/%s/lim/30' % ea)
    return template('tpl/lite.html', msgs=msgs, ea=ea, u=get_u(), rmsg=rmsg)


@bosfor.route('/info.html')
def info_html():
    return template('data/info.html')


@bosfor.route('/settings/<k>/<v>')
def set_kv(k,v):
    response.set_cookie(k, v, path='/', max_age=7776000)
    return 'ok <a href="/">back</a>'


@bosfor.route('/json/<k>/<v>')
def json_ret(k,v):
    out = mydict()
    if k == 'msgs':
        for n in app_rq('msgs/%s' % v):
            out[n.mid] = mydict(n._data) - 'accepted' - 'id'
    elif k == 'echo':
        lim = 'lim/%s/' % request.params.lim if request.params.lim else ''
        for n in app_rq('%secho/%s' % (lim,v)):
            out.setdefault(n.echoarea, [])
            out[n.echoarea].append(n.mid)
    elif k == 'echolist':
        if request.params.cnt:
            out.echolist = mydict()
            for n in app_rq('echolist/%s/cnt/1' % v):
                out.echolist[n[0]] = n[1]
        else:
            out.echolist = app_rq_txt('echolist/%s' % v).splitlines()
    if request.params.callback:
        response.content_type = 'application/javascript; charset=utf-8'
        return '%s (\n%s\n)' % (request.params.callback, jout(out))
    else:
        response.content_type = 'application/json; charset=utf-8'
        return jout(out)


@bosfor.route('/s/<filename:path>')
def new_style(filename):
    return static_file(filename, root='./s')


bosfor.run(host=conf.BIND, port=15550, debug=True)
