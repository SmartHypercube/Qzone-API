#!/usr/bin/python3
# encoding=utf-8

import urllib.request, json, time, http.cookiejar

UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'

qzone_cookie = {}

def cookie_dict_to_str(**cookie):
    return '; '.join(map('='.join, cookie.items()))

def cookie_str_to_dict(cookie):
    return dict(map(lambda s: s.partition('=')[::2], cookie.split('; ')))

def get_cookie_from_file(path):
    '''从cookie文件获取'''
    cookie = http.cookiejar.MozillaCookieJar()
    cookie.load(path, ignore_discard=True, ignore_expires=True)
    return dict(map(lambda s: (s.name, s.value), cookie))

def get_cookie_from_curl(curl):
    '''为了使用方便，提供一个从curl命令中解析出cookie的函数'''
    start = curl.find('Cookie: ') + 8
    end = curl.find("'", start)
    return cookie_str_to_dict(curl[start:end])

def make_url(url, order=None, **args):
    if not order:
        order = args
    return url + '?' + '&'.join(map(lambda k: k+'=%s'%args[k], order))

def make_g_tk(p_skey, __cache={}, **cookie):
    if p_skey in __cache:
        return __cache[p_skey]
    tk = 5381
    for c in p_skey:
        tk += (tk<<5) + ord(c)
    tk &= 0x7fffffff
    __cache[p_skey] = tk
    return tk

class NotLoadedType:
    '''用于表示尚未载入的内容'''
    '''这里本应通过重载__new__使这个类成为单件类，但我还没搞好
    _instance = None
    @staticmethod
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    '''
    _locked = False
    @staticmethod
    def __init__():
        if NotLoadedType._locked:
            raise ValueError('Do not make new instance of NotLoadedType')
        NotLoadedType._locked = True
    @staticmethod
    def __bool__():
        return False
    @staticmethod
    def __repr__():
        return 'NotLoaded'
NotLoaded = NotLoadedType()

class Picture:
    '''图片'''
    def __init__(self, url):
        self.url = url
        if url.startswith('http://p.qpimg.cn/cgi-bin/cgi_imgproxy?'):
            self.url = url[url.find('url=')+4:]

    def open(self):
        req = urllib.request.Request(self.url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        return urllib.request.urlopen(req)

    def __str__(self):
        return '<Image>'

class Comment:
    '''评论'''
    def __init__(self, data):
        self.parse(data)

    def parse(self, data):
        self.content = data['content']
        self.ctime = data['create_time']
        self.nickname = data['name']
        self.tid = data['tid']
        self.author = data['uin']
        self.replys = []
        if 'list_3' in data:
            for r in data['list_3']:
                self.replys.append(Comment(r))
        self.pictures = []
        if 'rich_info' in data:
            for p in data['rich_info']:
                self.pictures.append(Picture(p['burl']))

    def __str__(self):
        s = '%s: %s%s' % (self.nickname, ''.join(map(str, self.pictures)), self.content)
        if self.replys:
            s += '\n| ' + '\n| '.join(map(str, self.replys))
        return s

class Emotion:
    '''说说

    这个类的部分属性值可能是NotLoaded，列表类型的属性值中也可能包含NotLoaded，表示相关信息必须进一步发送请求才能载入。调用load()方法可完全载入所有信息。'''
    def __init__(self, data):
        self.parse(data)

    def parse(self, data):
        '''解析各种信息

        目前支持的信息如下：
            comments
            shortcon
            content
            ctime
            forwardn
            location
            nickname
            pictures
            origin
            forwards
            source
            tid
            author
            like
        '''
        # comments
        if 'commentlist' in data:
            self.comments = list(map(Comment, data['commentlist']))
        else:
            self.comments = []
        # shortcon
        self.shortcon = data['content']
        # content
        if 'has_more_con' in data and data['has_more_con']:
            self.content = NotLoaded
        else:
            self.content = data['content']
        # ctime
        self.ctime = data['created_time']
        # forwardn
        self.forwardn = data['fwdnum']
        # location
        if 'lbs' in data:
            self.location = data['lbs']
        else:
            self.location = NotLoaded
        # nickname
        self.nickname = data['name']
        # pictures
        if 'pictotal' in data:
            self.pictures = list(map(lambda i:Picture(i['url1']), data['pic']))
            self.pictures += [NotLoaded] * (data['pictotal'] - len(self.pictures))
        else:
            self.pictures = []
        # origin
        if 'rt_con' in data and data['rt_tid']:
            odata = dict(commentlist=[], content=data['rt_con']['content'], created_time=NotLoaded, name=data['rt_uinname'])
            for k in data:
                if k.startswith('rt_'):
                    odata[k[3:]] = data[k]
            self.origin = Emotion(odata)
        else:
            self.origin = None
        # forwards
        if 'rtlist' in data:
            self.forwards = []
            for f in data['rtlist']:
                if 'con' not in f:
                    f['con'] = f['content']
                odata = dict(content=f['con'], has_more_con=1, created_time=NotLoaded, fwdnum=NotLoaded)
                for k in f:
                    odata[k] = f[k]
                self.forwards.append(Emotion(odata))
        # source
        self.source = data['source_name']
        # tid
        self.tid = data['tid']
        # author
        self.author = data['uin']
        # like
        if '__like' in data:
            self.like = {}
            for i in data['__like']:
                self.like[i['fuin']] = (i['nick'], Picture(i['portrait']))
        else:
            self.like = NotLoaded

    def load(self):
        '''完全载入一条说说的所有信息'''
        url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6',
                uin = self.author,
                tid = self.tid,
                num = 20,
                pos = 0,
                g_tk = make_g_tk(**qzone_cookie),
                not_trunc_con = 1)
        req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        with urllib.request.urlopen(req) as http:
            s = http.read().decode()
        data = json.loads(s[s.find('(')+1 : s.rfind(')')])
        for i in range(20, len(self.comments), 20):
            if len(data['commentlist']) != 20 * i:
                break
            url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6',
                    uin = self.author,
                    tid = self.tid,
                    num = 20,
                    pos = i,
                    g_tk = make_g_tk(**qzone_cookie),
                    not_trunc_con = 1)
            req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
            with urllib.request.urlopen(req) as http:
                s = http.read().decode()
            data['commentlist'] += json.loads(s[s.find('(')+1 : s.rfind(')')])['commentlist']
        url = make_url('http://users.edu.qzone.qq.com/cgi-bin/likes/get_like_list_app',
                uin = qzone_cookie['ptui_loginuin'],
                unikey = 'http%%3A%%2F%%2Fuser.qzone.qq.com%%2F%s%%2Fmood%%2F%s' % (self.author, self.tid),
                begin_uin = 0,
                query_count = 999999,
                if_first_page = 1,
                g_tk = make_g_tk(**qzone_cookie))
        req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        with urllib.request.urlopen(req) as http:
            s = http.read().decode()
        like = json.loads(s[s.find('(')+1 : s.rfind(')')])
        data['__like'] = like['data']['like_uin_info']
        self.parse(data)
        if self.pictures:
            url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_get_pics_v6',
                    uin = self.author,
                    tid = self.tid,
                    g_tk = make_g_tk(**qzone_cookie))
            req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
            with urllib.request.urlopen(req) as http:
                s = http.read().decode()
            pictures = json.loads(s[s.find('(')+1 : s.rfind(')')])
            self.pictures = list(map(Picture, pictures['imageUrls']))

    def __str__(self):
        s = self.nickname
        if self.ctime:
            s += ' ' + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.ctime))
        if self.location and self.location['name']:
            s += ' from %s' % self.location['name']
        if self.source:
            s += ' via %s' % self.source
        s += '\n'
        s += ''.join(map(str, self.pictures))
        if self.content:
            s += self.content
        else:
            s += self.shortcon + ' ...'
        s += '\n'
        if self.origin:
            s += '| ' + '\n| '.join(str(self.origin).splitlines()) + '\n'
        if self.like:
            s += '%s likes   ' % len(self.like)
        s += '%s forwards   %s comments\n' % (self.forwardn, len(self.comments))
        s += '\n'.join(map(str, filter(None, self.comments)))
        return s

class Qzone:
    def __init__(self, **cookie):
        global qzone_cookie
        qzone_cookie = cookie

    def emotion_list_raw(self, uin, num=20, pos=0, ftype=0, sort=0, replynum=100,
            code_version=1, need_private_comment=1):
        '''获取一个用户的说说列表，返回经过json解析的原始数据'''
        url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
                uin = uin,
                ftype = ftype,
                sort = sort,
                pos = pos,
                num = num,
                replynum = replynum,
                g_tk = make_g_tk(**qzone_cookie),
                callback = '_preloadCallback',
                code_version = code_version,
                format = 'jsonp',
                need_private_comment = need_private_comment)
        req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        with urllib.request.urlopen(req) as http:
            s = http.read().decode()
        return json.loads(s[s.find('(')+1 : s.rfind(')')])

    def emotion_list(self, uin, num=20, pos=0, ftype=0, sort=0, replynum=100,
            code_version=1, need_private_comment=1):
        '''获取一个用户的说说列表，返回Emotion对象列表'''
        l = self.emotion_list_raw(uin, num, pos, ftype, sort, replynum, code_version, need_private_comment)['msglist']
        return list(map(Emotion, l if l else []))
