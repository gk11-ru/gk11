# -*- coding: utf-8 -*-

import libz.bottle as bottle, re

def sp(s):
    pre = 0; code = 0; txt = ''
    for n in s.splitlines():
        if n == '====' and pre == 0:
            txt += u'</p>====<pre>'
            pre = 1
        elif n == '====' and pre == 1:
            if code == 1: txt += '</code>'
            txt += u'</pre>====<p>\n'
            pre = 0; code = 0
        elif pre == 1:
            txt += u'%s\n' % n
        else:
            txt += u'%s\n' % _ac(n)
    if code == 1: txt += '</code>'
    if pre == 1: txt += '</pre>'
    return txt

def _ac(t):
    o = t
    if 'http://' in o:
        o = _btn(o,'http://')
    if 'https://' in o:
        o = _btn(o,'https://')
    if o.rstrip().startswith('&gt;'):
        o = u'<em style="color:green">%s</em>' % o
    return o

def _settag(s,tag):
    if tag == 'http://' or tag == 'https://':
        return u'<a href="%s%s"><i class="fa fa-%s"></i>%s%s</a>' % (tag,s,'link' if tag == 'http://' else 'lock', tag,s)

def _btn(s,tag):
    k = s.split(tag)
    buf = k[0]
    for x in k[1:]:
        endl = x.split(' ',1)
        xl = None
        for eol in ('.',',',':','(',')','&quot;','&#039;', '&lt;', '&gt;'):
            if endl[0].endswith(eol):
                xl = _settag(endl[0][:-len(eol)],tag) + eol + ' ' + ' '.join(endl[1:])
        if xl is None: xl = _settag(endl[0],tag) + ' ' + ' '.join(endl[1:])
        buf += xl
    return buf

def rend(txt):
    out = bottle.html_escape(txt)
    out = sp(out)
    r2 = re.compile(r":fa-([-a-z0-9 ]*):")
    out = r2.sub(r'<i class="fa fa-\1"></i>',out)
    r3 = re.compile(r":img ([-_.A-Za-z0-9]*):")
    out = r3.sub(r'<img style="border-radius:4px" src="/s/img/\1" />',out)
    return out.replace('\n', '<br />')
